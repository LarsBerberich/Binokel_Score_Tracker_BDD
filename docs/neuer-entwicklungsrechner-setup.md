# Setup neuer Entwicklungsrechner / Weiter von hier

> Dieses Dokument ist der direkte Handover für einen neuen Laptop oder einen anderen Rechner.
> Es fasst zusammen, was du brauchst, damit du am selben Punkt wie jetzt weiterarbeiten kannst,
> inklusive GitHub-Repo, SSH-Zugang zur VM und lokaler Projekt-Setup.

## 1. Aktueller Stand

- Repo: `LarsBerberich/Binokel_Score_Tracker_BDD`
- Branch: `main`
- Produktiv-SSH-Verbindung zu `api.bebe-soft.de` über Deploy-/Admin-Key
- letzte dokumentierte Handover-Phase: Domain-/Frontend-Fortsetzung + Governance-/Ops-Aufgaben

Den tatsächlichen Stand nicht aus diesem Dokument ablesen, sondern ermitteln — eine
hier eingetragene Commit-ID ist erfahrungsgemäß bereits beim nächsten Push veraltet:

```bash
git fetch origin
git log origin/main -1 --format='%h %s (%ad)' --date=short   # letzter gepushter Stand
git log origin/main..main --oneline                          # lokal, noch nicht gepusht
```

> **Hinweis:** Ein Push auf `main` löst nach grüner CI den Produktions-Deploy aus
> (`.github/workflows/cd.yml`). Lokale Commits bewusst sammeln und gezielt pushen.

Erwartete Testlage nach vollständigem Setup (Abschnitte 5 und 6):
**61 Django · 32 Behave · 61 Vitest · 1 Playwright-Smoke** — alle grün.

## 2. Voraussetzungen auf dem neuen Rechner

### 2.1 Standard-Tools

- Git
- VS Code + GitHub Copilot
- OpenSSH-Client
- Auf macOS: Xcode Command Line Tools (`xcode-select --install`)

**Weder Python noch Node müssen vorab installiert werden.** Beide Laufzeiten werden
projekt-lokal und versionsgenau von Werkzeugen bereitgestellt, die in Abschnitt 2.2
eingerichtet werden:

| Laufzeit | Version | Gepinnt in | Bereitgestellt durch |
|---|---|---|---|
| Python | **3.14** | `backend/.python-version`, `requires-python` in `backend/pyproject.toml` | `uv` |
| Node | **22** | `frontend/.node-version`, `engines.node` in `frontend/package.json` | `fnm` (ADR-012) |

> Ein System-Python (z. B. die macOS-Version 3.9) ist für dieses Projekt **nicht**
> verwendbar: `pyproject.toml` verlangt `>=3.14`. `uv` lädt den passenden Interpreter
> selbst — genau wie auf der Produktions-VM (`deploy/setup-server.sh`, ENG-004).

### 2.2 uv und fnm einrichten

**uv** (Python-Paket- und Interpreter-Manager) — derselbe offizielle Installer, den auch
`deploy/setup-server.sh` auf der VM verwendet. Installiert nach `~/.local/bin`, ohne `sudo`,
und ergänzt den PATH-Eintrag in der Shell-Startdatei:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**fnm** (Node-Versionsmanager) — gemäß **ADR-012** bewusst **nicht** per `curl | bash`,
sondern als Release-Binary mit Prüfsummenabgleich. Für macOS ist `fnm-macos.zip` das
richtige Asset (Universal Binary, enthält arm64 und x86_64); unter Linux `fnm-linux.zip`:

```bash
cd "$(mktemp -d)"
curl -sSL https://api.github.com/repos/Schniz/fnm/releases/latest -o fnm-release.json

# Download-URL und erwarteten SHA256 aus den Release-Metadaten lesen
read -r URL EXPECTED <<<"$(python3 -c '
import json, pathlib
d = json.loads(pathlib.Path("fnm-release.json").read_text())
a = next(x for x in d["assets"] if x["name"] == "fnm-macos.zip")
print(a["browser_download_url"], a["digest"].split(":", 1)[1])
')"

curl -sSL -o fnm-macos.zip "$URL"
ACTUAL=$(shasum -a 256 fnm-macos.zip | cut -d' ' -f1)
[ "$EXPECTED" = "$ACTUAL" ] || { echo "ABBRUCH: Pruefsumme weicht ab"; exit 1; }

unzip -q fnm-macos.zip
install -m 0755 fnm "$HOME/.local/bin/fnm"
```

Anschließend die Shell-Integration verankern, damit beim Betreten eines Verzeichnisses
automatisch die in `.node-version` gepinnte Version aktiv wird. Auf macOS ist die
Login-Shell `zsh`, also `~/.zshrc` (unter Linux analog `~/.bashrc`):

```bash
cat >> ~/.zshrc <<'EOF'

# fnm (Node-Versionsmanager, ADR-012)
if command -v fnm >/dev/null 2>&1; then
  eval "$(fnm env --use-on-cd --shell zsh)"
fi
EOF
```

Danach Node installieren und als Standard setzen:

```bash
exec zsh -l          # Shell neu laden, damit PATH und fnm greifen
fnm install 22
fnm default 22
```

### 2.3 Verifikation der Toolchain

```bash
uv --version     # z. B. uv 0.12.17
fnm --version    # z. B. fnm 1.39.0
node --version   # v22.x   (beim Betreten von frontend/ automatisch)
npm --version    # 10.x
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

`uv` liest `backend/.python-version`, lädt den passenden Interpreter und erzeugt
`backend/.venv` aus `uv.lock` — identisch zum CI-Job in `.github/workflows/ci.yml`.
`--dev` ist nötig, sonst fehlen `pytest` und `pytest-django` aus der `dependency-groups`.

```bash
cd backend
uv python install        # installiert Python 3.14 (Version aus .python-version)
uv sync --dev            # erzeugt .venv und installiert alle Abhängigkeiten
```

Verifikation — dieselben Gates wie in der CI:

```bash
uv run python manage.py check
uv run python manage.py makemigrations --check   # "No changes detected"
uv run python manage.py migrate                  # lokale Dev-SQLite anlegen
uv run python manage.py test scoring             # erwartet: 61 Tests OK
```

Behave-Akzeptanztests aus dem **Repo-Root** (nicht aus `backend/`). `PYTHONPATH=backend`
ist erforderlich, damit das Settings-Modul aus `behave.ini` gefunden wird:

```bash
cd ..
PYTHONPATH=backend backend/.venv/bin/python -m behave   # erwartet: 32 Szenarien passed
```

> Es wird bewusst **kein** `pip install -e .` in einem selbst angelegten venv verwendet:
> Das umgeht `uv.lock` (keine reproduzierbaren Versionen), erfordert einen bereits
> installierten Python 3.14 und weicht von CI und Produktion ab.

## 6. Frontend einrichten

```bash
cd frontend
npm ci                   # reproduzierbar aus package-lock.json
npm run build            # Vite-Build inkl. vue-tsc Typecheck
npm test                 # Vitest, erwartet: 61 Tests in 7 Dateien
```

Für den Playwright-E2E-Smoke wird zusätzlich der an die Playwright-Version gepinnte
Browser benötigt (ca. 150 MB nach `~/Library/Caches/ms-playwright`, nicht im Repo).
Bewusst **nicht** der lokal installierte Chrome: Nur die gepinnte Build stellt sicher,
dass lokal derselbe Browser läuft wie im CI-Job `frontend-e2e`. Auf macOS ohne
`--with-deps` (das installiert Linux-Systembibliotheken):

```bash
npx playwright install chromium
npm run test:e2e         # 1 Szenario (ADR-013); startet den Dev-Server selbst
```

Entwicklung mit laufendem Backend — zwei Terminals, Dev-Proxy laut `vite.config.ts`
(`/api` und `/health` → `127.0.0.1:8000`), damit lokal dieselbe Same-Origin-Situation
herrscht wie in Produktion (ADR-010):

```bash
# Terminal 1 — Backend
cd backend && uv run python manage.py runserver 127.0.0.1:8000

# Terminal 2 — Frontend
cd frontend && npm run dev          # http://localhost:5173
```

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

Setzt voraus, dass `uv` und `fnm` nach Abschnitt 2.2 eingerichtet sind.

```bash
git clone https://github.com/LarsBerberich/Binokel_Score_Tracker_BDD.git
cd Binokel_Score_Tracker_BDD

# Backend: Interpreter, venv, DB, Tests
cd backend
uv python install && uv sync --dev
uv run python manage.py migrate
uv run python manage.py test scoring

# Akzeptanztests aus dem Repo-Root
cd ..
PYTHONPATH=backend backend/.venv/bin/python -m behave

# Frontend
cd frontend
npm ci && npm run build && npm test
npm run dev                       # http://localhost:5173

# Nur für Deploy/Remote-Zugriff nötig (Abschnitt 3)
ssh -T binokel-deploy 'echo SSH_OK'
```

## 12. Handover-Regel

Vor dem Start einer neuen Session immer zuerst lesen:

1. `BACKLOG.md`
2. `docs/neuer-entwicklungsrechner-setup.md`
3. `docs/handover-backup-parallelentwicklung.md`
4. `docs/copilot-handover-v1.md`

Damit bleibt der Projektstand nachvollziehbar, auch ohne Chat-Historie.
