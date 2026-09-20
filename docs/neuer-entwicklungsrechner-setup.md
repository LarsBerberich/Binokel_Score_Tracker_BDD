# Setup neuer Entwicklungsrechner / Weiter von hier

> Dieses Dokument ist der direkte Handover für einen neuen Laptop oder einen anderen Rechner.
> Es fasst zusammen, was du brauchst, damit du am selben Punkt wie jetzt weiterarbeiten kannst,
> inklusive GitHub-Repo, SSH-Zugang zur VM und lokaler Projekt-Setup.

## 1. Aktueller Stand (Stand 13.09.2026)

- Repo: `LarsBerberich/Binokel_Score_Tracker_BDD`
- Branch: `main`
- letzter gepuschter Commit: `277cafa` (`docs: add new developer machine setup and handover notes`)
- GitHub-Remote: `origin/main` aktuell
- Produktiv-SSH-Verbindung zu `api.bebe-soft.de` ist durch den Deploy-/Admin-Key validiert
- letzte dokumentierte Handover-Phase: Domain-/-Frontend-Fortsetzung + Governance-/Ops-Aufgaben

## 2. Voraussetzungen auf dem neuen Rechner

### 2.1 Standard-Tools

- Git
- VS Code + GitHub Copilot
- Python 3.12+ (für Backend)
- Node 22 (für Frontend; ideal über `fnm` oder `nvm`)
- OpenSSH-Client

### 2.2 Python / Node-Versionen

Backend:

```bash
python --version
```

Frontend:

```bash
node --version
npm --version
```

Empfohlen:

```bash
fnm install 22
fnm use 22
```

## 3. SSH-Zugang zur Produktiv-VM vorbereiten

Wichtige Dateien aus dem alten Rechner mitnehmen:

- `~/.ssh/binokel_admin`
- `~/.ssh/binokel_admin.pub`
- `~/.ssh/binokel_deploy`
- `~/.ssh/binokel_deploy.pub`
- `~/.ssh/known_hosts`

Optional: vorhandene SSH-Konfiguration in `~/.ssh/config` ebenfalls kopieren.

### 3.1 SSH-Config (empfohlen)

Datei: `~/.ssh/config`

```sshconfig
Host binokel-admin
    HostName api.bebe-soft.de
    User binokel-admin
    IdentityFile ~/.ssh/binokel_admin
    IdentitiesOnly yes
    StrictHostKeyChecking yes
    UserKnownHostsFile ~/.ssh/known_hosts

Host binokel-deploy
    HostName api.bebe-soft.de
    User binokel-deploy
    IdentityFile ~/.ssh/binokel_deploy
    IdentitiesOnly yes
    StrictHostKeyChecking yes
    UserKnownHostsFile ~/.ssh/known_hosts
```

### 3.2 Verifikation

```bash
ssh -T binokel-admin 'echo OK'
ssh -T binokel-deploy 'echo SSH_OK'
```

Erwartung:

- Admin-Key für `binokel-admin` funktioniert
- Deploy-Key für CI/CD-/Remote-Deploy funktioniert
- Host-Checks sind in `known_hosts` gesetzt

## 4. Repository klonen

```bash
git clone https://github.com/LarsBerberich/Binokel_Score_Tracker_BDD.git
cd Binokel_Score_Tracker_BDD
```

Danach sicherstellen, dass der Branch stimmt:

```bash
git checkout main
git pull --ff-only origin main
```

### 4.1 Git-Identität setzen (vor dem ersten Commit)

Ohne gesetzte Identität leitet Git Autor und Committer aus Benutzername und Hostname ab
(z. B. `lberberi@MBP-von-Lars.fritz.box`). Solche Commits lassen sich auf GitHub keinem
Konto zuordnen. Für dieses Projekt gilt:

```bash
git config --global user.name "Lars Berberich"
git config --global user.email "lars.berberich@bebe-soft.de"
```

Prüfen: `git config --get user.email` bzw. am Commit selbst
`git log -1 --format='%an <%ae>'`.

Ein bereits erzeugter, **noch nicht gepushter** Commit mit falscher Identität lässt sich
nachträglich korrigieren:

```bash
git commit --amend --reset-author --no-edit
```

> **Hinweis:** `--global` gilt für alle Repositories dieses Rechners. Wird derselbe Rechner
> auch für Arbeits-Repositories mit anderer Adresse genutzt, dort repo-lokal überschreiben
> (`git config user.email "…"` ohne `--global`).

## 5. Backend einrichten

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
python manage.py migrate
python manage.py test scoring
```

Alternative mit `uv`:

```bash
cd backend
uv sync
```

Behave-Tests aus dem Repo-Root:

```bash
cd ..
backend/.venv/bin/python -m behave
```

## 6. Frontend einrichten

```bash
cd frontend
npm ci
npm test
npm run build
npm run dev
```

Dev-Proxy erwartet nach Vite-Config:

- `/api` -> Django
- `/health` -> Django

## 7. GitHub-Secrets und Variablen prüfen

Auf GitHub im Repo müssen aktuell diese Werte vorhanden sein:

- `VM_SSH_KEY` = Inhalt von `~/.ssh/binokel_deploy`
- `VM_HOST` = `api.bebe-soft.de` oder passende VM-Host-Identität
- `VM_USER` = `binokel-deploy`
- `VM_SSH_KNOWN_HOSTS` = komplette Ausgabe von `ssh-keyscan -H api.bebe-soft.de`

Wichtig:

- `VM_SSH_KNOWN_HOSTS` ist ein öffentliches Host-Keys-Set, kein Secret
- es ist Pflicht, damit der CD-Workflow nicht mit MITM-Risiko läuft

## 8. Nächste Reihenfolge, um am selben Punkt weiterzumachen

1. SSH-Verbindung prüfen
2. Git-Status + GitHub-Remote prüfen
3. `git pull --ff-only origin main`
4. Domain-/Frontend-Cutover im Sinne von ADR-010 prüfen
5. `TASK-CI-007` bis `TASK-CI-010` abschließen
6. kleine UX-Fixes `TASK-017`, `TASK-018`, `TASK-019` laden
7. danach produktiven Handover erneut dokumentieren

## 9. Aktuelle offene Fokusfelder

### 9.1 Domain-/Frontend-Cutover

- Frontend primär unter `https://binokel.bebe-soft.de`
- API auf `https://api.bebe-soft.de`
- `api` soll 301 auf `binokel` weiterleiten
- SAN-Cert/Certbot mit `binokel` als Primärdomain

### 9.2 Governance-/Ops-Nacharbeiten

- `TASK-CI-007` Reviewer-Gate `production`
- `TASK-CI-008` Branch Protection `main`
- `TASK-CI-009` IONOS-Ports schließen
- `TASK-CI-010` Backup-/Restore-Probe automatisieren

### 9.3 UX-/Kosmetik-Findings

- `TASK-017` Anschreibetabelle-Header
- `TASK-018` Korrektur-Dialog bei Tausendern
- `TASK-019` Rundenzähler nach Spielende

## 10. Wichtige Projektdateien

- `BACKLOG.md`
- `docs/handover-backup-parallelentwicklung.md`
- `docs/copilot-handover-v1.md`
- `docs/neuer-entwicklungsrechner-setup.md`
- `deploy/setup-server.sh`
- `deploy/nginx.conf.template`
- `backend/binokel_tracker/settings.py`
- `.github/workflows/cd.yml`

## 11. Schnellstart (wenn du sofort loslegen willst)

```bash
git clone https://github.com/LarsBerberich/Binokel_Score_Tracker_BDD.git
cd Binokel_Score_Tracker_BDD

# SSH-Keys und known_hosts vor dem ersten Remote-Deploy sicherstellen
ssh -T binokel-deploy 'echo SSH_OK'

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
python manage.py migrate

# Frontend
cd ../frontend
npm ci
npm run dev
```

## 12. Handover-Regel

Vor dem Start einer neuen Session immer zuerst lesen:

1. `BACKLOG.md`
2. `docs/neuer-entwicklungsrechner-setup.md`
3. `docs/handover-backup-parallelentwicklung.md`
4. `docs/copilot-handover-v1.md`

Damit bleibt der Projektstand nachvollziehbar, auch ohne Chat-Historie.
