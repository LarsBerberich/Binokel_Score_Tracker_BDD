#!/usr/bin/env bash
# setup-server.sh — Einmaliges Initialsetup für die 1&1 Linux-VM
#
# Voraussetzungen:
#   - Frisch installiertes Debian 12 (Bookworm) oder Ubuntu 22.04/24.04
#   - Root-Zugriff per SSH
#   - Domain zeigt bereits auf die Server-IP (für Certbot)
#
# Aufruf (als root):
#   bash setup-server.sh YOUR_DOMAIN your-github-repo-url
#
# Beispiel:
#   bash setup-server.sh binokel.example.com https://github.com/LarsBerberich/Binokel_Score_Tracker_BDD.git

set -euo pipefail

DOMAIN="${1:?Fehler: Domain als erstes Argument angeben, z. B. binokel.example.com}"
REPO_URL="${2:?Fehler: GitHub-Repo-URL als zweites Argument angeben}"
APP_DIR="/opt/binokel/app"
DATA_DIR="/opt/binokel/data"
STATIC_DIR="/opt/binokel/static"
LOG_DIR="/var/log/binokel"
APP_USER="binokel-app"
DEPLOY_USER="binokel-deploy"

echo "=== [1/9] Systempakete aktualisieren ==="
apt-get update -qq
apt-get upgrade -y -qq

echo "=== [2/9] Benötigte Pakete installieren ==="
apt-get install -y -qq \
    git curl nginx certbot python3-certbot-nginx \
    ufw logrotate

echo "=== [3/9] uv installieren (Python-Paketmanager) ==="
curl -LsSf https://astral.sh/uv/install.sh | sh
# uv zum PATH hinzufügen (gilt für dieses Skript)
export PATH="$HOME/.cargo/bin:$PATH"

echo "=== [4/9] Betriebsbenutzer anlegen ==="
# Anwendungsbenutzer (keine Login-Shell, kein Home)
useradd --system --no-create-home --shell /usr/sbin/nologin "$APP_USER" || echo "Benutzer $APP_USER existiert bereits"

# Deploy-Benutzer (für CD-Pipeline per SSH)
useradd --create-home --shell /bin/bash "$DEPLOY_USER" || echo "Benutzer $DEPLOY_USER existiert bereits"
mkdir -p "/home/$DEPLOY_USER/.ssh"
chmod 700 "/home/$DEPLOY_USER/.ssh"

# Deploy-Benutzer darf systemctl für den App-Dienst ausführen (passwordlos)
cat > "/etc/sudoers.d/binokel-deploy" << EOF
$DEPLOY_USER ALL=(ALL) NOPASSWD: /bin/systemctl restart binokel-tracker.service
$DEPLOY_USER ALL=(ALL) NOPASSWD: /bin/systemctl rollback binokel-tracker.service
$DEPLOY_USER ALL=(ALL) NOPASSWD: /bin/systemctl stop binokel-tracker.service
$DEPLOY_USER ALL=(ALL) NOPASSWD: /bin/systemctl status binokel-tracker.service
EOF
chmod 440 "/etc/sudoers.d/binokel-deploy"

echo "=== [5/9] Verzeichnisstruktur anlegen ==="
mkdir -p "$APP_DIR" "$DATA_DIR" "$STATIC_DIR" "$LOG_DIR"
mkdir -p /etc/binokel

chown "$DEPLOY_USER:$DEPLOY_USER" "$APP_DIR"
chown "$APP_USER:$APP_USER" "$DATA_DIR" "$STATIC_DIR" "$LOG_DIR"
chmod 750 /etc/binokel

echo "=== [6/9] Repository klonen ==="
sudo -u "$DEPLOY_USER" git clone "$REPO_URL" "$APP_DIR" || echo "Repo existiert bereits"

echo "=== [7/9] Umgebungsdatei anlegen (manuell befüllen!) ==="
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

echo "=== [8/9] systemd-Dienst installieren ==="
cp "$APP_DIR/deploy/binokel-tracker.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable binokel-tracker.service

echo "=== [9/9] Nginx konfigurieren und TLS-Zertifikat anfordern ==="
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

echo ""
echo "══════════════════════════════════════════════════════════"
echo "✅ Server-Setup abgeschlossen!"
echo ""
echo "Nächste Schritte:"
echo "  1. /etc/binokel/env befüllen (DJANGO_SECRET_KEY etc.)"
echo "  2. chmod 640 /etc/binokel/env && chown root:binokel-app /etc/binokel/env"
echo "  3. Den öffentlichen SSH-Key des Deploy-Benutzers eintragen:"
echo "     /home/$DEPLOY_USER/.ssh/authorized_keys"
echo "  4. Diesen Key als GitHub-Secret VM_SSH_KEY hinterlegen"
echo "  5. Secrets VM_HOST und VM_USER in GitHub eintragen"
echo "  6. Ersten Deploy manuell auslösen (GitHub Actions → CD → Run workflow)"
echo "══════════════════════════════════════════════════════════"
