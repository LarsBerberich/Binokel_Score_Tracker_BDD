# ADR-007 – GitHub Actions als CI/CD-Toolchain

## Status

Angenommen (19.07.2026)

## Kontext

Das Projekt benötigt eine automatisierte CI-Pipeline, die bei jedem Push und PR die BDD-Akzeptanztests ausführt. Für CD ist ein automatisches Deployment auf die 1&1 Linux-VM erforderlich.

Alternativen wurden verglichen:
- **GitHub Actions**: nativ in GitHub integriert, keine zusätzliche Infrastruktur nötig, kostenloses Kontingent für öffentliche Repos
- **GitLab CI**: würde einen Wechsel der Hosting-Plattform erfordern
- **Jenkins**: benötigt eigene Infrastruktur und Wartungsaufwand, überdimensioniert für den Projektumfang
- **CircleCI / Travis CI**: kostenlos eingeschränkt, zusätzlicher Dienst nötig

## Entscheidung

**GitHub Actions** wird als CI/CD-Toolchain eingesetzt.

## Begründung

1. Das Repository liegt bereits auf GitHub — keine zusätzlichen Accounts oder Dienste nötig.
2. GitHub Actions läuft direkt auf dem Repository-Kontext und hat Zugriff auf Secrets ohne externen Secret-Store.
3. Der Free-Tier reicht für den aktuellen Projektumfang (kleines Projekt, wenige Commits pro Tag).
4. Die GitHub-Environments-Funktion bietet ein Deployment-Gate für `main` ohne zusätzliche Tooling.
5. Workflow-Dateien liegen im Repo (`/home/runner/work/Binokel_Score_Tracker_BDD/Binokel_Score_Tracker_BDD/.github/workflows/`) und sind versioniert.

## Konsequenzen

### Positiv
- Vollständig versionierte CI/CD-Konfiguration im Repository
- Kein externer Dienst zu warten
- Einfache Secrets-Verwaltung über GitHub Repository Settings
- CI blockiert automatisch Merges bei fehlgeschlagenen BDD-Szenarien (Branch Protection)

### Negativ / Risiken
- GitHub-Abhängigkeit: falls das Repo migriert wird, muss CI/CD neu aufgebaut werden
- Minutes-Kontingent bei privatem Repo begrenzt (2.000 min/Monat im Free-Tier)
- Python 3.14 muss über `uv` installiert werden, da GitHub-Runner es möglicherweise nicht vorinstalliert haben

## Implementierung

- `/.github/workflows/ci.yml` — läuft bei jedem Push und PR
- `/.github/workflows/cd.yml` — deployt auf `main` nach erfolgreichem CI

## Empfehlung für Branch Protection

Im GitHub-Repository unter Settings → Branches → Branch Protection Rules für `main`:
- [x] Require status checks to pass before merging → `BDD Akzeptanztests`
- [x] Require branches to be up to date before merging
