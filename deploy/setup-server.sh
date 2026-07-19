#!/usr/bin/env bash
# setup-server.sh — Einmaliges Initialsetup für die 1&1 Linux-VM
#
# Voraussetzungen:
#   - Frisch installiertes Debian 12 (Bookworm) oder Ubuntu 22.04/24.04
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
# Dieses Skript ist idempotent und richtet u. a. ein:
#   - Betriebsbenutzer, Verzeichnisse, uv, systemd, Nginx+TLS, UFW, Logrotation
#   - fail2ban (SSH-Brute-Force-Schutz)
#   - unattended-upgrades (automatische Sicherheitsupdates)
#   - chrony (Zeit-Synchronisation)
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
APP_USER="binokel-app"
DEPLOY_USER="binokel-deploy"

echo "=== [1/10] Systempakete aktualisieren ==="
apt-get update -qq
apt-get upgrade -y -qq

echo "=== [2/10] Benötigte Pakete installieren ==="
apt-get install -y -qq \
    git curl nginx certbot python3-certbot-nginx \
    ufw logrotate \
    fail2ban unattended-upgrades apt-listchanges chrony

echo "=== [3/10] uv installieren (Python-Paketmanager) ==="
curl -LsSf https://astral.sh/uv/install.sh | sh
# uv systemweit verfügbar machen, damit auch nicht-interaktive SSH-Sessions
# (z. B. der CD-Workflow) uv ohne Anpassung des PATH nutzen können.
install -m 0755 "$HOME/.cargo/bin/uv" /usr/local/bin/uv

echo "=== [4/10] Betriebsbenutzer anlegen ==="
# Anwendungsbenutzer (keine Login-Shell, kein Home)
useradd --system --no-create-home --shell /usr/sbin/nologin "$APP_USER" || echo "Benutzer $APP_USER existiert bereits"

# Deploy-Benutzer (für CD-Pipeline per SSH)
useradd --create-home --shell /bin/bash "$DEPLOY_USER" || echo "Benutzer $DEPLOY_USER existiert bereits"
mkdir -p "/home/$DEPLOY_USER/.ssh"
chmod 700 "/home/$DEPLOY_USER/.ssh"

# Deploy-Benutzer darf systemctl für den App-Dienst ausführen (passwordlos)
cat > "/etc/sudoers.d/binokel-deploy" << EOF
$DEPLOY_USER ALL=(ALL) NOPASSWD: /bin/systemctl restart binokel-tracker.service
$DEPLOY_USER ALL=(ALL) NOPASSWD: /bin/systemctl stop binokel-tracker.service
$DEPLOY_USER ALL=(ALL) NOPASSWD: /bin/systemctl status binokel-tracker.service
EOF
chmod 440 "/etc/sudoers.d/binokel-deploy"

echo "=== [5/10] Verzeichnisstruktur anlegen ==="
mkdir -p "$APP_DIR" "$DATA_DIR" "$STATIC_DIR" "$LOG_DIR"
mkdir -p /etc/binokel

chown "$DEPLOY_USER:$DEPLOY_USER" "$APP_DIR"
chown "$APP_USER:$APP_USER" "$DATA_DIR" "$STATIC_DIR" "$LOG_DIR"
chmod 750 /etc/binokel

echo "=== [6/10] Repository klonen ==="
sudo -u "$DEPLOY_USER" git clone "$REPO_URL" "$APP_DIR" || echo "Repo existiert bereits"

echo "=== [7/10] Umgebungsdatei anlegen (manuell befüllen!) ==="
if [ ! -f /etc/binokel/env ]; then
    cat > /etc/binokel/env << 'ENV_TEMPLATE'
# /etc/binokel/env — Production-Konfiguration
# ACHTUNG: Diese Datei enthält Secrets. Berechtigungen: 640 root:binokel-app
#
# Nach dem Befüllen: chmod 640 /etc/binokel/env && chown root:binokel-app /etc/binokel/env

DJANGO_SECRET_KEY=REPLACE_WITH_SECURE_RANDOM_KEY_MIN_50_CHARS
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=REPLACE_WITH_YOUR_DOMAIN
DJANGO_DB_PATH=/opt/binokel/data/db.sqlite3
DJANGO_STATIC_ROOT=/opt/binokel/static
DJANGO_CSRF_TRUSTED_ORIGINS=https://REPLACE_WITH_YOUR_DOMAIN
ENV_TEMPLATE
    chmod 600 /etc/binokel/env
    echo "⚠️  /etc/binokel/env wurde angelegt. Bitte vor dem ersten Start befüllen!"
fi

echo "=== [8/10] systemd-Dienst installieren ==="
cp "$APP_DIR/deploy/binokel-tracker.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable binokel-tracker.service

echo "=== [9/10] Nginx konfigurieren und TLS-Zertifikat anfordern ==="
# Nginx-Config einrichten
sed "s/REPLACE_WITH_YOUR_DOMAIN/$DOMAIN/g" \
    "$APP_DIR/deploy/nginx.conf.template" \
    > "/etc/nginx/sites-available/binokel-tracker"
ln -sf /etc/nginx/sites-available/binokel-tracker /etc/nginx/sites-enabled/binokel-tracker
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

# TLS-Zertifikat (interaktiv — E-Mail-Adresse eingeben)
certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos \
    --email "admin@$DOMAIN" --redirect

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

echo "=== [10/10] Härtung: fail2ban, automatische Sicherheitsupdates, Zeit-Sync ==="
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
