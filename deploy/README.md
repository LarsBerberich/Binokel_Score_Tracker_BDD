# Deploy-Dokumentation — Binokel Score Tracker

Dieses Verzeichnis enthält alle Artefakte für das Production-Deployment auf einer **1&1 / IONOS Linux-VM** (**Ubuntu 24.04 LTS**, siehe [ADR-008](../docs/adr/ADR-008-vm-deployment-strategie.md)).

> **Erster Produktions-Deploy (TASK-CI-006):** Die vollständige, phasenweise
> Schritt-für-Schritt-Anleitung inklusive **Internet-Hardening**, Verifikation und
> Rollback je Phase steht in **[`runbook-task-ci-006.md`](runbook-task-ci-006.md)**.
> Dieses README bleibt die laufende Betriebsreferenz.

---

## Übersicht der Dateien

| Datei | Zweck |
|---|---|
| `runbook-task-ci-006.md` | Schritt-für-Schritt-Runbook für den erstmaligen Aufbau + Erst-Deploy |
| `setup-server.sh` | Einmaliges Server-Initialsetup (als root ausführen) |
| `binokel-tracker.service` | systemd-Unit: startet die Django-App via Gunicorn |
| `nginx.conf.template` | Nginx Reverse-Proxy-Konfiguration mit TLS (Platzhalter ersetzen) |

---

## Internet-Hardening der VM

Vor dem Anwendungsbetrieb im offenen Internet wird die VM gemäß
**[ADR-009](../docs/adr/ADR-009-internet-hardening-baseline.md)** gehärtet. Die
Baseline und die genaue Aufgabenteilung stehen im
[Runbook, Phase 1 + 2](runbook-task-ci-006.md).

| Maßnahme | Wo eingerichtet |
|---|---|
| Non-root Admin-User + sudo, SSH-Key-only | **manuell**, Runbook Phase 1 |
| sshd-Hardening (Root-/Passwort-Login aus, `MaxAuthTries`) | **manuell**, Runbook Phase 1 |
| UFW-Firewall (nur SSH/HTTP/HTTPS) | `setup-server.sh` |
| fail2ban (SSH-Brute-Force-Schutz) | `setup-server.sh` |
| unattended-upgrades (automatische Sicherheitsupdates) | `setup-server.sh` |
| chrony (Zeit-Synchronisation) | `setup-server.sh` |
| TLS/HTTPS-Erzwingung + HSTS | `setup-server.sh` + `nginx.conf.template` |

> **Warum das sshd-Hardening manuell bleibt:** Ein Skript kann sich nicht selbst
> gegen einen SSH-Lockout absichern; das sichere Vorgehen erfordert eine zweite,
> parallel offene Sitzung zur Verifikation (menschliche Kontrollhandlung). Begründung
> siehe ADR-009. `fail2ban`, `unattended-upgrades` und `chrony` sind idempotent und
> ohne Lockout-Risiko und werden daher automatisiert.

---

## Erstmaliges Server-Setup

> Ausführliche Fassung mit Verifikation und Rollback: [Runbook](runbook-task-ci-006.md).

```bash
# 1. Per SSH als root anmelden (Erst-Login; danach Hardening laut Runbook Phase 1)
ssh root@IHRE_VM_IP

# 2. Setup-Skript herunterladen und ausführen (nach abgeschlossenem Hardening)
curl -LO https://raw.githubusercontent.com/LarsBerberich/Binokel_Score_Tracker_BDD/main/deploy/setup-server.sh
sudo bash setup-server.sh IHRE_DOMAIN https://github.com/LarsBerberich/Binokel_Score_Tracker_BDD.git
```

> **Trockenlauf zuerst:** Vor dem echten Deploy den kompletten Pfad einmal risikofrei
> gegen eine Wegwerf-VM mit Certbot-Staging durchspielen (`CERTBOT_STAGING=1`).
> Schritt-für-Schritt-Anleitung: [Trockenlauf-Runbook](runbook-dry-run.md).

Das Skript richtet folgendes ein:
- Betriebsbenutzer `binokel-app` (App-Prozess) und `binokel-deploy` (CI/CD-Pipeline)
- Verzeichnisstruktur unter `/opt/binokel/`
- systemd-Dienst und Nginx mit TLS (Let's Encrypt via Certbot)
- Firewall (UFW: nur SSH, HTTP, HTTPS)
- **fail2ban, unattended-upgrades, chrony** (Härtung, siehe oben)
- POSIX-ACLs für gemeinsamen Schreibzugriff (`binokel-app` + `binokel-deploy`) auf `data`/`static`
- Tägliches SQLite-Backup (`cron.d`)
- Logrotation

---

## GitHub-Secrets einrichten

In **GitHub → Repository → Settings → Secrets and Variables → Actions** folgende Secrets anlegen:

| Secret-Name | Inhalt |
|---|---|
| `VM_SSH_KEY` | Privater SSH-Schlüssel des `binokel-deploy`-Benutzers |
| `VM_HOST` | IP-Adresse oder Domain der VM (z. B. `192.0.2.10`) |
| `VM_USER` | `binokel-deploy` |
| `VM_SSH_KNOWN_HOSTS` | **(Pflicht)** Bekannte Host-Keys der VM im `known_hosts`-Format. Erzeugen mit `ssh-keyscan -H <VM_HOST>`. Ohne dieses Secret bricht der CD-Workflow bewusst ab – es gibt **keinen** Laufzeit-`ssh-keyscan`-Fallback mehr (MITM-Schutz, siehe ADR-009). |

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
# Produktionskonfiguration laden (gleiche Pfade wie der Dienst):
set -a; . /etc/binokel/env; set +a
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

`setup-server.sh` richtet automatisch ein **tägliches Backup** ein
(`/etc/cron.d/binokel-backup`, läuft als `binokel-app` um 03:00 Uhr, Aufbewahrung 30 Tage):

```bash
# /etc/cron.d/binokel-backup (vom Setup-Skript angelegt)
0 3 * * * binokel-app cp /opt/binokel/data/db.sqlite3 /opt/binokel/data/db.sqlite3.bak.$(date +\%Y\%m\%d) 2>/dev/null || true
5 3 * * * binokel-app find /opt/binokel/data/ -name "db.sqlite3.bak.*" -mtime +30 -delete
```

**Restore** (Dienst vorher stoppen, danach starten):

```bash
sudo systemctl stop binokel-tracker.service
sudo -u binokel-app cp /opt/binokel/data/db.sqlite3.bak.YYYYMMDD /opt/binokel/data/db.sqlite3
sudo systemctl start binokel-tracker.service
```
