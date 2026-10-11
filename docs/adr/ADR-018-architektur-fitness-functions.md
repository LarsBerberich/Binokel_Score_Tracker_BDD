# ADR-018 – Architektur-Fitness-Functions in der CI

## Status

Angenommen (11.10.2026)

## Kontext

ADR-004 legt die Schichtregeln fest (Domäne und Use Cases ohne Framework, ORM nur im Repository).
Die C4-Konformitätsprüfung (`docs/architecture/architektur-konformitaet.md`) zeigte, dass diese
Regeln nur durch Disziplin gehalten wurden: Fachlogik war unbemerkt in `views.py` und
`repositories.py` gelandet (F-01, F-02).

## Entscheidung

Die Schichtregeln werden maschinell geprüft und als CI-Schritt erzwungen:

- **Backend:** `import-linter` mit Verträgen in `backend/.importlinter` (Domäne/Use Cases ohne
  Django, Domäne ohne äußere Schichten, Use Cases ohne Persistenz/HTTP, Persistenz ohne
  HTTP/Use Cases, Views nur über Repositories zur Datenbank). Aufruf: `uv run lint-imports`.
- **Frontend:** `dependency-cruiser` mit Regeln in `frontend/.dependency-cruiser.cjs`
  (`domain/` rein, Komponenten ohne API-Client, Views und Store, keine Zyklen).
  Aufruf: `npm run lint:arch`.

Verworfene Alternativen: `pytestarch` bzw. eigene Tests (mehr Eigenbau, Regeln liegen im
Testcode statt deklarativ) und reine Code-Review-Disziplin (hat die Abweichungen nicht verhindert).

## Konsequenzen

**Positiv:** Verstöße gegen ADR-004 brechen den Build; die Regeln sind deklarativ und lesbar.

**Negativ / Kompromisse:** Zwei zusätzliche Dev-Abhängigkeiten. Die Frontend-Regel „Komponenten
nutzen den API-Client nicht“ erkennt nur direkte Imports von `api/client`, nicht den Weg über
`api/index.ts`.

## Verwandte Entscheidungen

- ADR-004: Repository Pattern und Schichtenregel, die hier abgesichert wird
- ADR-013: Teststrategie – die Fitness Functions ergänzen die Testpyramide um Strukturprüfungen
