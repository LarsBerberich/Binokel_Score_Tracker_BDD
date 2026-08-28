# Handover, Backup & Parallelentwicklung (Stand 2026-08-28)

> Zweck: (1) Übergabe an einen Agenten **ohne Chat-Historie**, (2) alles, was du sichern
> musst, um von einem **Windows-11-Rechner parallel** weiterzuentwickeln, (3) was vom
> **Server** gesichert werden muss (Zertifikate, Secrets, DB), (4) exakte Anleitung zur
> **Domain-Umstellung** auf `binokel.bebe-soft.de` (Frontend) + `api.bebe-soft.de` (API).

---

## 1. Projektstatus (Kurz, für history-losen Agenten)

- **App ist LIVE:** `https://api.bebe-soft.de/` — Vue-SPA (Frontend) + Django-JSON-API
  (`/api`, `/health`) Same-Origin über nginx + TLS. Deep-Links (`/spiel/:id`) funktionieren.
- **Backend:** Django 6 in `backend/`, venv `backend/.venv` (python3, `manage.py`).
  Tests: **61 Django** (`python manage.py test scoring`), **32 Behave**
  (Repo-Root: `backend/.venv/bin/python -m behave`).
- **Frontend:** `frontend/`, Vue 3 + Vite + TS, Node **22** (via fnm), `npm`.
  Tests: **61 Vitest** (`npm test`), Build `npm run build` → `frontend/dist/`.
  Genau 1 Playwright-E2E-Smoke (Teststrategie ADR-013: Fachlogik bleibt auf API-Ebene).
- **Repo:** `github.com/LarsBerberich/Binokel_Score_Tracker_BDD`, Branch `main`.
  origin ist aktuell (bis Commit der Smoke-Fix-Änderung gepusht).
- **CI/CD:** `.github/workflows/ci.yml` (Tests+Build) → gate → `cd.yml`
  (Deploy auf VM: Backend `uv sync`/`migrate`/`collectstatic`/Restart **und** Frontend
  `npm run build` + rsync `dist/` → `/opt/binokel/frontend`). CD triggert bei Push auf `main`
  (nach grüner CI) oder manuell (Actions → „CD" → Run workflow → `confirm=yes`).
- **Wichtige Konventionen:** siehe `docs/project-foundation.md` §18 (PFLICHT-KONVENTION:
  jede Änderung Doku-synchron); Regelwerk `docs/rule-set-v1.md`; ADRs `docs/adr/`;
  Fallstricke `docs/engineering-notes/`; Backlog `BACKLOG.md`.
- **Nächster geplanter Schritt:** Domain-Trennung (Abschnitt 4) — Frontend auf
  `binokel.bebe-soft.de`, API auf `api.bebe-soft.de` (301-Redirect api→binokel). Dies ist
  das ADR-010-Zielbild; der aktuelle Single-Domain-Betrieb auf `api.bebe-soft.de` war die
  effiziente Interim-Lösung (BACKLOG `TASK-CI-011`).

---

## 2. Windows-11: Parallelentwicklung einrichten

### 2.1 Werkzeuge installieren
- **Git** (git-scm.com) + **VS Code** (+ GitHub Copilot).
- **Python 3.12+** (python.org, „Add to PATH"). Optional **uv** (`pip install uv`).
- **Node 22** über **fnm** (`winget install Schniz.fnm`) oder **nvm-windows**; dann
  `fnm install 22 && fnm use 22`. Version ist über `frontend/.node-version` gepinnt.

### 2.2 Repo klonen & Projekt aufsetzen
```powershell
git clone https://github.com/LarsBerberich/Binokel_Score_Tracker_BDD.git
cd Binokel_Score_Tracker_BDD
# Backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .            # oder: uv sync
python manage.py migrate    # lokale SQLite (Dev)
python manage.py runserver 127.0.0.1:8000
# Frontend (neues Terminal)
cd ..\frontend
npm ci
npm run dev                 # http://localhost:5173 (Dev-Proxy /api+/health → :8000)
```
Tests: Backend `python manage.py test scoring`; Behave (Repo-Root)
`backend\.venv\Scripts\python -m behave`; Frontend `npm test`.

### 2.3 Was du auf den Windows-Rechner mitnehmen musst
- **Nichts Geheimes für reine Dev-Arbeit** — der Code liegt im öffentlichen Repo, die lokale
  Dev-DB ist eine leere SQLite. Prod-Secrets werden **nicht** für die Entwicklung gebraucht.
- **Nur wenn du vom Windows-Rechner deployen/SSH willst:** die SSH-Keys (Abschnitt 3.1).
- Git-Identität setzen: `git config --global user.name/user.email`.

> **Parallel-Hinweis:** Auf beiden Rechnern denselben Branch `main` sauber pullen/pushen;
> vor dem Weiterarbeiten immer `git pull`. `git push origin main` **triggert Produktions-Deploy** —
> bewusst einsetzen.

---

## 3. Backup / Disaster-Recovery — was gesichert werden MUSS

### 3.1 Lokal (dein Rechner) — SSH-Zugang zur VM (KRITISCH, nicht reproduzierbar)
| Datei | Zweck |
|---|---|
| `~/.ssh/binokel_admin` (+ `.pub`) | Admin-Login `binokel-admin@…` (sudo). **Passphrase-geschützt** — Passphrase in Passwortmanager sichern! |
| `~/.ssh/binokel_deploy` (+ `.pub`) | Deploy-User (CD/rsync). Ist zugleich GitHub-Secret `VM_SSH_KEY`. |

Sichere diese Keys **verschlüsselt** (Passwortmanager/USB-Tresor). Ohne den Admin-Key +
Passphrase kommst du nur noch über die IONOS-Cloud-Console (VNC/Rescue) auf die VM.

### 3.2 Server (VM) — für Wiederaufbau/Migration KRITISCH
Als root/`sudo` sichern (z. B. per `scp` auf einen sicheren Rechner):
| Pfad auf der VM | Inhalt / Warum |
|---|---|
| `/etc/binokel/env` | **DJANGO_SECRET_KEY** + Pfade/Hosts. 600 root:root + ACL. **Geheim!** |
| `/etc/letsencrypt/` (komplett) | **TLS-Zertifikate** inkl. `archive/`, `live/`, `accounts/`, `renewal/`. Für HTTPS ohne Neuausstellung. `tar czf letsencrypt.tgz /etc/letsencrypt` (als root). |
| `/opt/binokel/data/db.sqlite3` | **Produktionsdaten** (Spiele/Runden). Konsistente Kopie via `sqlite3 db.sqlite3 ".backup kopie.db"`. |
| `/etc/systemd/system/binokel-tracker.service` | Dienst-Definition (liegt auch im Repo `deploy/`). |
| `/etc/nginx/sites-*` (aktive Config) | Aus Template generiert (Repo `deploy/nginx.conf.template`); Kopie hilft beim schnellen Vergleich. |

> **Automatisches DB-Backup** ist bereits eingerichtet: `setup-server.sh` installiert
> `/usr/local/bin/binokel-backup.sh` + `/etc/cron.d/binokel-backup` (tägl. 03:00,
> `sqlite3 .backup` + `integrity_check`, 30 Tage Retention). **Diese Backups liegen aber auf
> derselben VM** → für echte DR **offsite** kopieren (scp-Pull) und/oder **IONOS-VM-Snapshot**
> (BACKLOG FUTURE-003). Certs + `env` sind NICHT im DB-Cron enthalten → separat sichern (s. o.).

### 3.3 GitHub (reproduzierbar, aber dokumentieren)
- **Secret:** `VM_SSH_KEY` (= Inhalt von `~/.ssh/binokel_deploy`).
- **Variables:** `VM_HOST` (SSH-Ziel, aktuell `api.bebe-soft.de`), `VM_USER`
  (`binokel-deploy`), `VM_SSH_KNOWN_HOSTS` (Ausgabe von
  `ssh-keyscan -t rsa,ecdsa,ed25519 <VM_HOST>` — beim Domainwechsel neu erzeugen!).

### 3.4 Schneller Sicherungs-Einzeiler (auf der VM, als binokel-admin)
```bash
sudo tar czf ~/binokel-backup-$(date +%F).tgz \
  /etc/binokel/env /etc/letsencrypt \
  /etc/systemd/system/binokel-tracker.service
sudo sqlite3 /opt/binokel/data/db.sqlite3 ".backup '/tmp/db-$(date +%F).sqlite3'"
# danach beide Dateien per scp auf einen sicheren Rechner ziehen und lokal löschen
```

---

## 4. Domain-Umstellung: Frontend `binokel.bebe-soft.de`, API `api.bebe-soft.de`

Zielbild (ADR-010): `binokel.bebe-soft.de` serviert die SPA + proxied `/api`;
`api.bebe-soft.de` → **301** auf `binokel.bebe-soft.de` (Altbestand/Bookmarks bleiben).
Beide im **SAN-Zertifikat** (Lineage der **Primärdomain** = erstes `-d` = binokel).
Die Infrastruktur (Zwei-Domain-Modus + Redirect-Block) ist in `nginx.conf.template` und
`setup-server.sh` **bereits vorbereitet**.

### Schritte (in dieser Reihenfolge)
1. **DNS:** A-Record `binokel.bebe-soft.de` → **dieselbe VM-IP** wie `api.bebe-soft.de`
   setzen (IONOS-DNS). Warten bis auflösbar (`nslookup binokel.bebe-soft.de`).
2. **env anpassen** (VM, als root) in `/etc/binokel/env` **beide** Domains eintragen:
   ```
   DJANGO_ALLOWED_HOSTS=binokel.bebe-soft.de,api.bebe-soft.de
   DJANGO_CSRF_TRUSTED_ORIGINS=https://binokel.bebe-soft.de,https://api.bebe-soft.de
   ```
   Danach: `sudo systemctl restart binokel-tracker.service`.
3. **Cert-Lineage-Falle (ENG-005) beachten:** Es existiert bereits eine Einzel-Lineage
   `api.bebe-soft.de`. Das neue SAN-Cert soll unter der **binokel**-Lineage liegen. Sauberster
   Weg — Certbot ein SAN-Cert mit Primär binokel ausstellen lassen (expandiert/ersetzt):
   ```bash
   sudo certbot --nginx -d binokel.bebe-soft.de -d api.bebe-soft.de --redirect
   # Prüfen: sudo certbot certificates   (eine Lineage mit BEIDEN Domains)
   ```
   (Alternativ vorher `setup-server.sh` laufen lassen — nächster Punkt — der ruft Certbot
   mit genau dieser Domain-Reihenfolge auf.)
4. **nginx auf Zwei-Domain-Modus** umstellen (VM, als root) — Primärdomain zuerst, API-Domain
   als 3. Argument:
   ```bash
   sudo bash /opt/binokel/app/deploy/setup-server.sh \
     binokel.bebe-soft.de https://github.com/LarsBerberich/Binokel_Score_Tracker_BDD.git \
     api.bebe-soft.de
   ```
   Das rendert beide server-Blöcke (SPA auf binokel, 301 api→binokel), Certbot SAN, idempotent.
   `env` wird **nicht** überschrieben (Punkt 2 bleibt erhalten).
5. **CI/CD-Smoke auf Primärdomain** umstellen: GitHub-Variable **`VM_HOST` bleibt der
   SSH-erreichbare Host** (kann `api.bebe-soft.de` bleiben, da SSH dort lauscht). Da der
   Smoke-Test `https://$VM_HOST/` prüft und `api` künftig **301** liefert, den Smoke-`/`-Check
   auf die Primärdomain zeigen lassen **oder** `curl -L` (Redirect folgen). Empfehlung: separate
   Variable `SMOKE_BASE=https://binokel.bebe-soft.de` in `cd.yml` verwenden. (Kleiner
   `cd.yml`-Patch; danach `VM_SSH_KNOWN_HOSTS` unverändert lassen, da SSH weiter auf `api` geht.)
6. **Verifizieren:**
   ```bash
   curl -s -o /dev/null -w '%{http_code}\n' https://binokel.bebe-soft.de/         # 200 (SPA)
   curl -s -o /dev/null -w '%{http_code}\n' https://api.bebe-soft.de/             # 301 → binokel
   curl -s -o /dev/null -w '%{http_code}\n' https://binokel.bebe-soft.de/health/  # 200
   ```
7. **Doku-Sync (PFLICHT):** `BACKLOG.md` (TASK-CI-011 M4 abhaken), `docs/copilot-handover-v1.md`,
   `/memories/repo/handover-status.md`, ggf. ADR-010-Nachtrag (Interim→Zielbild vollzogen),
   diese Datei aktualisieren.

> **Sicherung vor dem Domainwechsel:** Punkt 3.4 (env + `/etc/letsencrypt` + DB) ausführen —
> falls Certbot/nginx-Umbau schiefgeht, kannst du die alte Config/Certs zurückspielen.

---

## 5. Offene Punkte / Governance (BACKLOG)
- `TASK-CI-011` M4: Domain-Umstellung (Abschnitt 4).
- `TASK-CI-007` Reviewer-Gate `production`, `TASK-CI-008` Branch Protection `main`,
  `TASK-CI-009` IONOS-Ports 8000/8443/8447 schließen, `TASK-CI-010`/`FUTURE-003` Offsite-Backup.
- `TASK-017/018/019`: kleine Frontend-Kosmetik/UX aus dem FND-006-Durchspielen.
- Kleinigkeit: Seitentitel ist noch Vite-Default `frontend` (`frontend/index.html` `<title>` +
  Favicon) — schnelle Politur.

---

## 6. Wichtige Pfade (VM) — Referenz
| Pfad | Inhalt |
|---|---|
| `/opt/binokel/app` | Code (git-Klon; CD rsynct hierher) |
| `/opt/binokel/frontend` | Ausgelieferte Vue-SPA (`dist/`), nginx-Root, `www-data`-ACL |
| `/opt/binokel/data/db.sqlite3` | Produktions-DB |
| `/opt/binokel/static` | Django-Static |
| `/opt/binokel/python` | uv-verwalteter Python-Interpreter (geteilt) |
| `/etc/binokel/env` | Secrets/Config (SECRET_KEY, Hosts, Pfade) |
| `/etc/letsencrypt` | TLS-Zertifikate |
| `/etc/systemd/system/binokel-tracker.service` | gunicorn-Dienst |
| `/var/log/binokel/` | App-Logs |
| Dienst-User: `binokel-app` (läuft), `binokel-deploy` (CD), `binokel-admin` (sudo) | |
