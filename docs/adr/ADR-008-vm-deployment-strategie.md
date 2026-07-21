# ADR-008 – VM-Deployment-Strategie: Direktes Systemd-Deployment ohne Container

## Status

Angenommen (19.07.2026)

## Kontext

Die Anwendung soll auf einer 1&1 Linux-VM produktiv betrieben werden. Für die Auslieferung wurden verschiedene Strategien betrachtet:

1. **Direktes Deployment** auf der VM: Code via rsync/git, App als systemd-Dienst, Nginx als Reverse Proxy
2. **Docker-Container**: App im Container, Compose-Setup für App + Nginx
3. **Docker + Orchestrierung** (Kubernetes, Nomad): für den aktuellen Umfang deutlich überdimensioniert

## Entscheidung

**Direktes Deployment** ohne Container wird gewählt:
- Betriebssystem-Basis: **Ubuntu 24.04 LTS (Noble)** als getestete Referenzplattform
- Django-App als **systemd-Dienst** (via Gunicorn)
- **Nginx** als Reverse Proxy mit TLS (Let's Encrypt)
- Code via **rsync** aus GitHub Actions
- Abhängigkeiten via **uv** direkt auf der VM

## Begründung

| Kriterium | Direkt | Docker |
|---|---|---|
| Betriebskomplexität | Niedrig | Mittel |
| Debugging auf VM | Einfach (systemctl, journalctl) | Erfordert Docker-Know-how |
| Aktuelle Reife des Projekts | Passend (kein Frontend, SQLite) | Sinnvoll erst mit mehr Services |
| Für 1&1 VM-Ressourcen | Ressourcensparend | Overhead durch Docker-Daemon |
| Rollback | systemctl rollback (systemd-native) | docker pull, compose down/up |

Docker bietet mehr Vorteile, sobald das Projekt:
- ein Frontend (Vue) als separaten Build-Step hat,
- mehrere Services braucht (z. B. PostgreSQL, Redis),
- Horizontal skaliert werden soll.

Bis dahin erhöht Docker die Komplexität, ohne klaren Mehrwert zu liefern.

### Betriebssystem-Basis: Ubuntu 24.04 LTS

Als Referenzplattform wird **Ubuntu 24.04 LTS (Noble)** gewählt (Entscheidung 21.07.2026):

- **Reife statt Neuheit:** 24.04 ist seit April 2024 im Feld und stabil; das jüngste
  LTS (26.04, April 2026) wird als `.0`-Release für einen Erst-Deploy bewusst gemieden.
- **Python-Version irrelevant für die Wahl:** Die App zieht ihre Python-Version über
  `uv python install` unabhängig vom System-Python — der Hauptvorteil neuerer Distros
  entfällt hier.
- **Supportfenster ausreichend:** Standard-Support bis 2029 (ESM bis 2034) deckt V1 ab.
- **Skript-Kompatibilität:** `deploy/setup-server.sh` ist auf 24.04 abgestimmt
  (u. a. `/usr/bin/systemctl`-Pfad in der sudoers-Regel, usrmerge).

Eine spätere Anhebung auf 26.04 LTS erfolgt frühestens nach dessen `.1`-Point-Release
und mit erneutem Trockenlauf.

## Konsequenzen

### Positiv
- Einfaches, gut verstandenes Betriebsmodell
- Direkte systemd-Integration: automatischer Neustart, Logging via journalctl
- Geringe Ressourcenanforderungen an die VM
- Keine Docker-Kenntnisse für Betrieb nötig

### Negativ / Risiken
- Kein Isolation zwischen Prozessen wie in Containern
- Migration zu Containern später erfordert Umbau der Pipeline
- Umgebungsunterschiede zwischen Dev und Prod möglich (kein "läuft bei mir, läuft überall")

### Meilenstein für Überprüfung dieser Entscheidung

Diese Entscheidung wird überprüft, wenn:
- Das Vue-Frontend produktionsbereit ist (TASK-006–010), oder
- Weitere Services (PostgreSQL, Redis) hinzukommen, oder
- Horizontal skaliert werden muss.

## Implementierung

- `deploy/binokel-tracker.service` — systemd-Unit
- `deploy/nginx.conf.template` — Nginx-Konfiguration
- `deploy/setup-server.sh` — Initialsetup-Skript
- `deploy/README.md` — Betriebsrunbook
- `.github/workflows/cd.yml` — CD-Pipeline (rsync + SSH)
