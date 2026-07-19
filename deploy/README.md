# Deploy-Dokumentation — Binokel Score Tracker

Dieses Verzeichnis enthält alle Artefakte für das Production-Deployment auf einer **1&1 Linux-VM** (Debian/Ubuntu).

---

## Übersicht der Dateien

| Datei | Zweck |
|---|---|
| `setup-server.sh` | Einmaliges Server-Initialsetup (als root ausführen) |
| `binokel-tracker.service` | systemd-Unit: startet die Django-App via Gunicorn |
| `nginx.conf.template` | Nginx Reverse-Proxy-Konfiguration mit TLS (Platzhalter ersetzen) |

---

## Erstmaliges Server-Setup

```bash
# 1. Per SSH als root anmelden
ssh root@IHRE_VM_IP

# 2. Setup-Skript herunterladen und ausführen
curl -LO https://raw.githubusercontent.com/LarsBerberich/Binokel_Score_Tracker_BDD/main/deploy/setup-server.sh
bash setup-server.sh IHRE_DOMAIN https://github.com/LarsBerberich/Binokel_Score_Tracker_BDD.git
```

Das Skript richtet folgendes ein:
- Betriebsbenutzer `binokel-app` (App-Prozess) und `binokel-deploy` (CI/CD-Pipeline)
- Verzeichnisstruktur unter `/opt/binokel/`
- systemd-Dienst und Nginx mit TLS (Let's Encrypt via Certbot)
- Firewall (UFW: nur SSH, HTTP, HTTPS)
- Logrotation

---

## GitHub-Secrets einrichten

In **GitHub → Repository → Settings → Secrets and Variables → Actions** folgende Secrets anlegen:

| Secret-Name | Inhalt |
|---|---|
| `VM_SSH_KEY` | Privater SSH-Schlüssel des `binokel-deploy`-Benutzers |
| `VM_HOST` | IP-Adresse oder Domain der VM (z. B. `192.0.2.10`) |
| `VM_USER` | `binokel-deploy` |
| `VM_SSH_KNOWN_HOSTS` | *(optional, empfohlen)* Bekannte Host-Keys der VM im `known_hosts`-Format. Erzeugen mit `ssh-keyscan -H <VM_HOST>`. Wenn nicht gesetzt, führt der Workflow `ssh-keyscan` automatisch aus – das ist praktisch, bietet aber keinen Schutz vor einem Man-in-the-Middle beim ersten Verbindungsaufbau. |

---

## Production-Konfiguration auf der VM

Die Datei `/etc/binokel/env` muss nach dem Setup befüllt werden:

```bash
# Auf der VM als root:
nano /etc/binokel/env
chmod 640 /etc/binokel/env
chown root:binokel-app /etc/binokel/env
```

Inhalt (Platzhalter ersetzen):

```env
DJANGO_SECRET_KEY=<mindestens 50 zufällige Zeichen — niemals aus dem Repo verwenden>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=binokel.example.com
DJANGO_DB_PATH=/opt/binokel/data/db.sqlite3
DJANGO_STATIC_ROOT=/opt/binokel/static
DJANGO_CSRF_TRUSTED_ORIGINS=https://binokel.example.com
```

Einen sicheren SECRET_KEY erzeugen:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(60))"
```

---

## Deployment-Prozess (automatisch via CD-Pipeline)

1. Entwickler pushed auf `main`
2. CI-Workflow läuft (BDD-Tests müssen GREEN sein)
3. Bei Erfolg startet CD automatisch:
   - **Preflight:** Prüft, dass `uv`, App-Verzeichnis, `/etc/binokel/env` und systemd-Unit auf der VM vorhanden sind
   - Quellcode per `rsync` auf VM übertragen
   - `uv sync`, `migrate`, `collectstatic`
   - `systemctl restart binokel-tracker`
   - Healthcheck auf `http://localhost/health/`
   - **Bei Fehler:** Workflow schlägt fehl; `systemctl status` und `journalctl`-Ausgabe werden zur Diagnose im Workflow-Log angezeigt. Ein automatischer Rollback auf eine vorherige Anwendungsversion ist nicht implementiert — bei einem fehlgeschlagenen Deploy muss der Fix gepusht oder der letzte funktionierende Commit auf `main` gebracht werden.

---

## Deploy-Voraussetzungen (Preflight)

Der CD-Workflow prüft vor jedem Deploy automatisch, dass die folgenden Voraussetzungen auf der VM erfüllt sind:

- `uv` ist systemweit verfügbar (`/usr/local/bin/uv`)
- App-Verzeichnis `/opt/binokel/app` existiert
- Umgebungsdatei `/etc/binokel/env` existiert
- systemd-Unit `/etc/systemd/system/binokel-tracker.service` ist vorhanden

Schlägt eine dieser Prüfungen fehl, bricht der Workflow vor dem eigentlichen Deploy ab. In diesem Fall muss das Server-Setup erneut ausgeführt oder die fehlende Voraussetzung manuell nachgezogen werden.

> **Hinweis zu `uv`:** Das Setup-Skript (`setup-server.sh`) installiert `uv` systemweit nach `/usr/local/bin/uv`, damit auch nicht-interaktive SSH-Sessions (wie die CD-Pipeline) `uv` ohne Anpassung des `PATH` nutzen können.

---

## Fehlerbehandlung bei fehlgeschlagenem Healthcheck

Besteht der Dienst den Healthcheck nach dem Deploy nicht, schlägt der Workflow fehl und gibt folgende Diagnoseinformationen im Workflow-Log aus:

- `systemctl status binokel-tracker.service`
- `journalctl -u binokel-tracker.service` (letzte 50 Zeilen)

Ein automatischer Rollback auf eine vorherige Anwendungsversion ist nicht implementiert. Vorgehen bei einem fehlgeschlagenen Deploy:

1. Diagnoseinformationen im GitHub Actions-Log prüfen
2. Fix entwickeln und auf `main` pushen (löst neuen Deploy aus)
3. **Oder:** Letzten bekannten guten Commit per `git revert` oder `git reset` auf `main` bringen

---

## Manueller Deploy (Notfall)

```bash
# Auf der VM als binokel-deploy:
cd /opt/binokel/app
git pull origin main
cd backend
uv sync --no-dev
uv run python manage.py migrate --noinput
uv run python manage.py collectstatic --noinput
sudo systemctl restart binokel-tracker.service

# Status prüfen
sudo systemctl status binokel-tracker.service
curl -s http://localhost/health/
```

---

## Logs

```bash
# App-Logs (Gunicorn)
tail -f /var/log/binokel/access.log
tail -f /var/log/binokel/error.log

# systemd Journal
journalctl -u binokel-tracker.service -f

# Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## Backup

Die SQLite-Datenbank liegt unter `/opt/binokel/data/db.sqlite3`.
Tägliches Backup empfohlen:

```bash
# /etc/cron.d/binokel-backup
0 3 * * * binokel-app cp /opt/binokel/data/db.sqlite3 /opt/binokel/data/db.sqlite3.bak.$(date +\%Y\%m\%d)
# Backups älter als 30 Tage löschen
5 3 * * * binokel-app find /opt/binokel/data/ -name "db.sqlite3.bak.*" -mtime +30 -delete
```
