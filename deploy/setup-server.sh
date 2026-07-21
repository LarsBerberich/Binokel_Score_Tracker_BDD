#!/usr/bin/env bash
# setup-server.sh — Einmaliges Initialsetup für die 1&1 Linux-VM
#
# Voraussetzungen:
#   - Referenzplattform: frisch installiertes Ubuntu 24.04 LTS (Noble), siehe ADR-008.
#     Debian 12 (Bookworm) / Ubuntu 22.04 sind grundsätzlich kompatibel, aber nicht
#     die getestete Zielplattform.
#   - Root-Zugriff per SSH (bzw. sudo als Admin-User)
#   - Domain zeigt bereits auf die Server-IP (für Certbot)
#   - Phase 1 des Runbooks (deploy/runbook-task-ci-006.md) ist abgeschlossen:
#     Non-root Admin-User und SSH-Daemon-Hardening (Root-/Passwort-Login aus) sind
#     BEREITS eingerichtet.
#
# Aufruf (als root):
#   bash setup-server.sh YOUR_DOMAIN your-github-repo-url
#
# Beispiel:
#   bash setup-server.sh binokel.example.com https://github.com/LarsBerberich/Binokel_Score_Tracker_BDD.git
#
# TROCKENLAUF (Wegwerf-VM): Certbot im Staging-Modus ausführen, um die strengen
# Let's-Encrypt-Produktions-Rate-Limits zu schonen. Das erzeugte Zertifikat ist
# BEWUSST UNGÜLTIG (Test-CA) — Browser/curl zeigen eine Zertifikatswarnung:
#   CERTBOT_STAGING=1 bash setup-server.sh test.example.com https://github.com/.../repo.git
# Staging und Produktion NICHT auf derselben VM mischen — die Trockenlauf-VM wird
# nach dem Test verworfen.
#
# Dieses Skript ist idempotent und richtet u. a. ein:
#   - Betriebsbenutzer, Verzeichnisse, uv, systemd, Nginx+TLS, UFW, Logrotation
#   - POSIX-ACLs für gemeinsamen Schreibzugriff (App- und Deploy-User)
#   - fail2ban (SSH-Brute-Force-Schutz)
#   - unattended-upgrades (automatische Sicherheitsupdates)
#   - chrony (Zeit-Synchronisation)
#   - tägliches SQLite-Backup (cron.d)
#
# BEWUSSTE ABGRENZUNG (siehe ADR-009 + deploy/runbook-task-ci-006.md, Phase 1):
#   Das SSH-Daemon-Hardening (PermitRootLogin no, PasswordAuthentication no, ggf.
#   Port) wird NICHT von diesem Skript vorgenommen. Grund: Es trägt ein SSH-Lockout-
#   Risiko, das nur durch menschliche Verifikation (zweite offene Sitzung) sicher
#   abgefangen werden kann. Es muss vorab MANUELL laut Runbook Phase 1 erfolgen.

set -euo pipefail

# Dieses Skript muss als root ausgeführt werden.
if [ "$(id -u)" -ne 0 ]; then
    echo "Fehler: Dieses Skript muss als root ausgeführt werden." >&2
    exit 1
fi

DOMAIN="${1:?Fehler: Domain als erstes Argument angeben, z. B. binokel.example.com}"
REPO_URL="${2:?Fehler: GitHub-Repo-URL als zweites Argument angeben}"
APP_DIR="/opt/binokel/app"
DATA_DIR="/opt/binokel/data"
STATIC_DIR="/opt/binokel/static"
LOG_DIR="/var/log/binokel"
# Geteiltes Zielverzeichnis für den von uv verwalteten Python-Interpreter, damit der
# Dienst-User binokel-app ihn erreichen kann (siehe UV_PYTHON_INSTALL_DIR in der
# env-Datei und Schritt [5/10]).
PYTHON_DIR="/opt/binokel/python"
APP_USER="binokel-app"
DEPLOY_USER="binokel-deploy"

# Optionaler Certbot-Staging-Modus für den Trockenlauf (siehe Header).
# Aktivierung über die Umgebungsvariable CERTBOT_STAGING=1|true|yes|on.
CERTBOT_STAGING="${CERTBOT_STAGING:-}"
CERTBOT_STAGING_FLAG=""
case "${CERTBOT_STAGING,,}" in
    1|true|yes|on)
        CERTBOT_STAGING_FLAG="--staging"
        echo "⚠️  CERTBOT_STAGING aktiv: Es wird ein UNGÜLTIGES Test-Zertifikat (Let's Encrypt Staging) ausgestellt."
        ;;
esac

echo "=== [1/10] Systempakete aktualisieren ==="
apt-get update -qq
apt-get upgrade -y -qq

echo "=== [2/10] Benötigte Pakete installieren ==="
apt-get install -y -qq \
    git curl nginx certbot python3-certbot-nginx \
    ufw logrotate acl \
    fail2ban unattended-upgrades apt-listchanges chrony

echo "=== [3/10] uv installieren (Python-Paketmanager) ==="
curl -LsSf https://astral.sh/uv/install.sh | sh
# uv systemweit verfügbar machen, damit auch nicht-interaktive SSH-Sessions
# (z. B. der CD-Workflow) uv ohne Anpassung des PATH nutzen können.
# Der Installationspfad variiert je nach uv-Version (~/.local/bin vs. ~/.cargo/bin),
# daher beide Kandidaten prüfen, statt einen festen Pfad anzunehmen.
UV_BIN=""
for _uv_candidate in "$HOME/.local/bin/uv" "$HOME/.cargo/bin/uv"; do
    if [ -x "$_uv_candidate" ]; then UV_BIN="$_uv_candidate"; break; fi
done
if [ -z "$UV_BIN" ]; then
    echo "Fehler: uv-Binary nach Installation nicht gefunden." >&2
    exit 1
fi
install -m 0755 "$UV_BIN" /usr/local/bin/uv

echo "=== [4/10] Betriebsbenutzer anlegen ==="
# Anwendungsbenutzer (keine Login-Shell, kein Home)
useradd --system --no-create-home --shell /usr/sbin/nologin "$APP_USER" || echo "Benutzer $APP_USER existiert bereits"

# Deploy-Benutzer (für CD-Pipeline per SSH)
useradd --create-home --shell /bin/bash "$DEPLOY_USER" || echo "Benutzer $DEPLOY_USER existiert bereits"
mkdir -p "/home/$DEPLOY_USER/.ssh"
chmod 700 "/home/$DEPLOY_USER/.ssh"

# Deploy-Benutzer darf systemctl für den App-Dienst ausführen (passwordlos).
# Kanonischer Pfad ist /usr/bin/systemctl (Ubuntu 24.04 / Debian usrmerge);
# sudo löst über secure_path genau diesen Pfad auf und vergleicht ihn literal.
#
# SICHERHEIT: BEWUSST nur restart/stop — KEINE `systemctl status`-Regel! `status`
# leitet die Ausgabe per Default durch einen Pager (less); aus einer interaktiven
# TTY (binokel-deploy hat SSH-Login + /bin/bash) ließe sich daraus mit `!sh` eine
# Root-Shell öffnen → Privilege-Escalation. Statusdiagnose erfolgt unprivilegiert
# (`systemctl status --no-pager`, `journalctl`, world-lesbares /var/log/binokel).
cat > "/etc/sudoers.d/binokel-deploy" << EOF
$DEPLOY_USER ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart binokel-tracker.service
$DEPLOY_USER ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop binokel-tracker.service
EOF
chmod 440 "/etc/sudoers.d/binokel-deploy"

echo "=== [5/10] Verzeichnisstruktur anlegen ==="
mkdir -p "$APP_DIR" "$DATA_DIR" "$STATIC_DIR" "$LOG_DIR"
mkdir -p /etc/binokel
# Geteiltes Verzeichnis für den von uv verwalteten Python-Interpreter (siehe
# UV_PYTHON_INSTALL_DIR in /etc/binokel/env). uv lädt den Interpreter sonst nach
# ~binokel-deploy/.local/share/uv/python (Home = 0750) — dort kommt der Dienst-User
# binokel-app nicht hin und kann den venv-Python (Shebang-Ziel von gunicorn) nicht
# ausführen (systemd: status=203/EXEC). Ein Verzeichnis unter /opt (world-traversierbar)
# löst das; die ACL sichert es umask-unabhängig ab.
mkdir -p "$PYTHON_DIR"

chown "$DEPLOY_USER:$DEPLOY_USER" "$APP_DIR" "$PYTHON_DIR" "$STATIC_DIR"
chown "$APP_USER:$APP_USER" "$DATA_DIR" "$LOG_DIR"
chmod 750 /etc/binokel

# Such-/Traversal-Recht (nur x, kein Lesen/Listen) auf /etc/binokel für App- und
# Deploy-User. Das Verzeichnis gehört root:root (750); ohne Verzeichnis-x können
# binokel-app und binokel-deploy die env-Datei trotz Datei-ACL nicht erreichen.
# (Der systemd-Dienst liest die Datei als root — betroffen ist nur der direkte
#  Zugriff, z. B. `. /etc/binokel/env` im CD-Deploy und im Phase-3-Check.)
setfacl -m u:"$APP_USER":x -m u:"$DEPLOY_USER":x /etc/binokel

# Der Dienst läuft als binokel-app, der App-Code (inkl. des von binokel-deploy beim
# Deploy erzeugten .venv mit der gunicorn-Binary) liegt unter APP_DIR und gehört
# binokel-deploy. Ohne Lese-/Ausführungsrecht kann binokel-app gunicorn nicht starten
# (systemd: status=203/EXEC, "Permission denied") — je nach umask des Deploy-Users.
# rX = Lesen + x-Bit nur auf Verzeichnissen/ausführbaren Dateien. Die Default-ACL sorgt
# dafür, dass von git clone / uv sync neu erzeugte Dateien (z. B. .venv/bin/gunicorn)
# das Recht erben — umask-unabhängig.
setfacl -R -m u:"$APP_USER":rX "$APP_DIR"
setfacl -R -d -m u:"$APP_USER":rX "$APP_DIR"

# Lese-/Ausführungsrecht für binokel-app auf das geteilte Interpreter-Verzeichnis.
# uv legt den Python-Interpreter dorthin (UV_PYTHON_INSTALL_DIR); der venv-Python ist
# nur ein Symlink darauf. Ohne Zugriff kann binokel-app gunicorn (Shebang → dieser
# Python) nicht ausführen (status=203/EXEC). Die Default-ACL sorgt dafür, dass der von
# uv beim Deploy als binokel-deploy entpackte Interpreter-Baum das Recht erbt.
setfacl -R -m u:"$APP_USER":rX "$PYTHON_DIR"
setfacl -R -d -m u:"$APP_USER":rX "$PYTHON_DIR"

# Gemeinsamer Zugriff auf Daten- und Static-Verzeichnis, aber mit Least Privilege:
#   DATA_DIR:   binokel-app rwX (SQLite-DB + Backup zur Laufzeit) UND binokel-deploy rwX
#               (migrate). Beide müssen dieselben Dateien schreiben.
#   STATIC_DIR: NUR binokel-deploy rwX (collectstatic). binokel-app bekommt lediglich
#               rX — der internet-exponierte Dienst darf NICHT in das von Nginx unter
#               der Domain ausgelieferte Static-Verzeichnis schreiben (sonst könnte eine
#               App-Lücke dort Phishing-/JS-Dateien ablegen). Nginx liefert /static/
#               ohnehin nur lesend per alias aus.
# POSIX-ACLs inkl. Default-ACLs stellen das umask-unabhängig auch für neu erzeugte
# Dateien sicher.
setfacl -R -m u:"$APP_USER":rwX -m u:"$DEPLOY_USER":rwX "$DATA_DIR"
setfacl -R -d -m u:"$APP_USER":rwX -m u:"$DEPLOY_USER":rwX "$DATA_DIR"
setfacl -R -m u:"$APP_USER":rX -m u:"$DEPLOY_USER":rwX "$STATIC_DIR"
setfacl -R -d -m u:"$APP_USER":rX -m u:"$DEPLOY_USER":rwX "$STATIC_DIR"

echo "=== [6/10] Repository klonen ==="
sudo -u "$DEPLOY_USER" git clone "$REPO_URL" "$APP_DIR" || echo "Repo existiert bereits"

echo "=== [7/10] Umgebungsdatei anlegen (manuell befüllen!) ==="
if [ ! -f /etc/binokel/env ]; then
    cat > /etc/binokel/env << 'ENV_TEMPLATE'
# /etc/binokel/env — Production-Konfiguration
# ACHTUNG: Diese Datei enthält Secrets (DJANGO_SECRET_KEY).
# Berechtigungen: 600 root:root. Der systemd-Dienst liest sie als root (EnvironmentFile);
# binokel-deploy erhält gezielten Lesezugriff per ACL (setfacl weiter unten), binokel-app
# braucht KEINEN Datei-Lesezugriff (systemd injiziert die Variablen in den Prozess).

DJANGO_SECRET_KEY=REPLACE_WITH_SECURE_RANDOM_KEY_MIN_50_CHARS
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=REPLACE_WITH_YOUR_DOMAIN
DJANGO_DB_PATH=/opt/binokel/data/db.sqlite3
DJANGO_STATIC_ROOT=/opt/binokel/static
DJANGO_CSRF_TRUSTED_ORIGINS=https://REPLACE_WITH_YOUR_DOMAIN

# uv installiert den verwalteten Python-Interpreter in dieses geteilte Verzeichnis
# (statt ~binokel-deploy/.local/share/uv/python, wo der Dienst-User binokel-app nicht
# hinkommt). Der Deploy exportiert diese Variable vor `uv sync`, sodass
# Interpreter-Installation und venv-Symlink hierhin zeigen.
UV_PYTHON_INSTALL_DIR=/opt/binokel/python
ENV_TEMPLATE
    chmod 600 /etc/binokel/env
    echo "⚠️  /etc/binokel/env wurde angelegt. Bitte vor dem ersten Start befüllen!"
fi

# Deploy-User Lesezugriff auf die Produktionskonfiguration geben, damit der
# CD-Deploy migrate/collectstatic mit denselben Pfaden (DJANGO_DB_PATH,
# DJANGO_STATIC_ROOT) wie der systemd-Dienst ausführt. Least Privilege bleibt
# gewahrt: binokel-deploy rsynct ohnehin den App-Code und startet den Dienst neu,
# der Key-Lesezugriff erhöht das reale Risiko daher nicht (siehe ADR-009-Nachtrag).
setfacl -m u:"$DEPLOY_USER":r /etc/binokel/env

echo "=== [8/10] systemd-Dienst installieren ==="
cp "$APP_DIR/deploy/binokel-tracker.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable binokel-tracker.service

echo "=== [9/10] Nginx konfigurieren und TLS-Zertifikat anfordern ==="
mkdir -p /var/www/certbot

CERT_LIVE_DIR="/etc/letsencrypt/live/$DOMAIN"
if [ ! -f "$CERT_LIVE_DIR/fullchain.pem" ]; then
    # Henne-Ei-Problem: Das vollständige Template referenziert TLS-Zertifikate
    # und von Certbot bereitgestellte Include-Dateien, die es beim Erstlauf noch
    # nicht gibt. Deshalb zuerst einen minimalen HTTP-only-Serverblock ausrollen,
    # damit nginx startet und Certbot die ACME-Challenge über Port 80 beantworten
    # kann. Andernfalls schlägt "nginx -t" fehl und bricht das Skript ab.
    cat > /etc/nginx/sites-available/binokel-tracker << BOOTSTRAP
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'bootstrap ok';
        add_header Content-Type text/plain;
    }
}
BOOTSTRAP
    ln -sf /etc/nginx/sites-available/binokel-tracker /etc/nginx/sites-enabled/binokel-tracker
    rm -f /etc/nginx/sites-enabled/default
    nginx -t
    systemctl reload nginx

    # Zertifikat anfordern. Der --nginx-Installer legt zusätzlich
    # /etc/letsencrypt/options-ssl-nginx.conf und ssl-dhparams.pem an, die das
    # vollständige Template per include benötigt. $CERTBOT_STAGING_FLAG ist im
    # Trockenlauf "--staging" (Test-CA), sonst leer (Produktions-CA).
    certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos \
        --email "admin@$DOMAIN" --redirect $CERTBOT_STAGING_FLAG
fi

# Vollständiges Template (inkl. 443/TLS) ausrollen — die Zertifikate und
# Certbot-Include-Dateien existieren jetzt.
sed "s/REPLACE_WITH_YOUR_DOMAIN/$DOMAIN/g" \
    "$APP_DIR/deploy/nginx.conf.template" \
    > "/etc/nginx/sites-available/binokel-tracker"
ln -sf /etc/nginx/sites-available/binokel-tracker /etc/nginx/sites-enabled/binokel-tracker
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

# Logrotation
cat > /etc/logrotate.d/binokel << 'LOGROTATE'
/var/log/binokel/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 binokel-app binokel-app
    sharedscripts
    postrotate
        systemctl kill -s USR1 binokel-tracker.service 2>/dev/null || true
    endscript
}
LOGROTATE

# Firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

echo "=== [10/10] Betriebshärtung & Backup: fail2ban, Sicherheitsupdates, Zeit-Sync, DB-Backup ==="
# Idempotente Härtungsmaßnahmen, die OHNE SSH-Lockout-Risiko automatisierbar sind.
# (Das sshd-Daemon-Hardening selbst bleibt bewusst manuell — siehe Skript-Header
#  und deploy/runbook-task-ci-006.md, Phase 1 / ADR-009.)

# fail2ban: SSH-Brute-Force-Schutz (lokale Jail-Konfiguration, überschreibt Distro-Defaults nicht)
cat > /etc/fail2ban/jail.d/binokel-sshd.local << 'FAIL2BAN'
[sshd]
enabled  = true
backend  = systemd
maxretry = 5
findtime = 10m
bantime  = 1h
FAIL2BAN
systemctl enable fail2ban
systemctl restart fail2ban

# unattended-upgrades: automatische Sicherheitsupdates aktivieren
cat > /etc/apt/apt.conf.d/20auto-upgrades << 'AUTOUPG'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
AUTOUPG
# Nur Sicherheitsupdates automatisch; kein automatischer Reboot als Default
# (Reboot-Fenster bei Bedarf über Unattended-Upgrade::Automatic-Reboot-Time setzen).
systemctl enable unattended-upgrades
systemctl restart unattended-upgrades

# chrony: Zeit-Synchronisation (wichtig für TLS-Gültigkeit und Log-Korrelation)
systemctl enable chrony
systemctl restart chrony
# Tägliches SQLite-Backup per cron.d (idempotent überschrieben). Läuft als
# binokel-app (Eigentümer der DB). Das '|| true' unterdrückt Fehler-Mails, solange
# die DB (vor dem ersten Deploy) noch nicht existiert. Backups > 30 Tage werden gelöscht.
cat > /etc/cron.d/binokel-backup << 'BACKUP'
# Binokel Score Tracker — tägliches SQLite-Backup
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
0 3 * * * binokel-app cp /opt/binokel/data/db.sqlite3 /opt/binokel/data/db.sqlite3.bak.$(date +\%Y\%m\%d) 2>/dev/null || true
5 3 * * * binokel-app find /opt/binokel/data/ -name "db.sqlite3.bak.*" -mtime +30 -delete
BACKUP
chmod 644 /etc/cron.d/binokel-backup
echo ""
echo "══════════════════════════════════════════════════════════"
echo "✅ Server-Setup abgeschlossen!"
echo ""
echo "Vollständige Schritt-für-Schritt-Anleitung: deploy/runbook-task-ci-006.md"
echo ""
echo "Nächste Schritte:"
echo "  1. /etc/binokel/env befüllen (DJANGO_SECRET_KEY etc.)  → Runbook Phase 3"
echo "  2. chmod 640 /etc/binokel/env && chown root:binokel-app /etc/binokel/env"
echo "  3. Den öffentlichen SSH-Key des Deploy-Benutzers eintragen:  → Runbook Phase 4"
echo "     /home/$DEPLOY_USER/.ssh/authorized_keys"
echo "  4. Diesen Key als GitHub-Secret VM_SSH_KEY hinterlegen"
echo "  5. Secrets VM_HOST, VM_USER, VM_SSH_KNOWN_HOSTS in GitHub eintragen"
echo "  6. Branch Protection für main aktivieren (ADR-007)  → Runbook Phase 5"
echo "  7. Ersten Deploy manuell auslösen (GitHub Actions → CD → Run workflow, confirm=yes)"
echo ""
echo "Hinweis: SSH-Daemon-Hardening (Root-/Passwort-Login aus) muss laut Runbook"
echo "         Phase 1 bereits VOR diesem Setup erfolgt sein (ADR-009)."
echo "══════════════════════════════════════════════════════════"
