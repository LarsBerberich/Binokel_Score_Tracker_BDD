# Backlog – Binokel Score Tracker V1

> **Workflow:** Session startet → diese Datei lesen → sofort im Bild.  
> Session endet → `BACKLOG.md` + `docs/copilot-handover-v1.md` + `/memories/repo/handover-status.md` synchron aktualisieren.

---

## ▶ Aktueller Fokus

**TASK-006 ist abgeschlossen. Nächster Schritt noch offen — siehe Open/Priorisiert.**

---

## Offen / Priorisiert

### Phase 1 – Backend (Outside-In, Slice für Slice)

- [x] **TASK-001** `models.py` — Django ORM-Modelle angelegt (18.07.2026)
  - `SpielModel`, `SpielerModel`, `RundeModel`, `GegenspielerRundeModel`
  - UniqueConstraints für Position, Rundennummer und Gegenspieler pro Runde
  - `_RUNDENAUSGANG_CHOICES` von `domain.Rundenausgang` abgeleitet (Single Source of Truth)

- [x] **TASK-002** Datenbankmigrationen erzeugt und angewendet (18.07.2026)
  - `scoring/migrations/0001_initial.py`
  - `python3 manage.py migrate` — alle Migrationen OK
  - 28/28 Behave-Szenarien weiterhin GREEN

- [x] **TASK-003** Use Cases an ORM ankoppeln (18.07.2026)
  - `backend/scoring/repositories.py` neu angelegt
  - `spiel_persistieren`, `spiel_laden`, `runde_persistieren`, `punktestaende_laden`
  - Use cases bleiben pure Funktionen (keine Änderung an `use_cases.py`)
  - 28/28 Behave-Szenarien weiterhin GREEN

- [x] **TASK-004** REST-Endpunkte implementiert (18.07.2026)
  - `backend/scoring/views.py` — 5 Views (JsonResponse, keine DRF-Abhängigkeit)
  - `backend/binokel_tracker/urls.py` — 6 URL-Muster registriert
  - `docs/adr/ADR-005-jsonresponse-statt-drf.md` — Entscheidung dokumentiert
  - Toten Code in `use_cases.py` entfernt
  - Bug in `repositories.py` behoben (Gegenspieler-Punkte korrekt aggregiert)
  - 28/28 Behave-Szenarien weiterhin GREEN

- [x] **TASK-005** API-Integrationstests in `scoring/tests.py` (TestCase + TestClient) — 19.07.2026
  - 18 Tests, alle GREEN
  - `SpielAnlegenApiTest`, `RundeAuswertenApiTest`, `PunktestaendeUndSiegerApiTest`
  - Normative Quelle: ADR-006

- [x] **TASK-006** Behave-Steps Slice 1 auf HTTP umgestellt, Infrastruktur für alle weiteren Slices bereitgestellt — 19.07.2026
  - `features/environment.py`: Test-Datenbank-Setup + `context.client` pro Szenario + Cleanup
  - `features/steps/spiel_anlegen_steps.py`: vollständige HTTP-Migration (ADR-006)
  - Slices 2–5: Domänen-Steps bleiben (testen interne Berechnungsregeln, nicht HTTP-sichtbar)
  - Slice 6: Domänen-Steps bleiben (Punktestände werden direkt gesetzt, keine passenden HTTP-Endpunkte)
  - Normative Quelle: ADR-006

### Phase 2 – Frontend (Vue) — noch nicht gestartet

- [ ] **TASK-007** Vue-Anwendung aufsetzen, API-Client konfigurieren
- [ ] **TASK-008** Spiel anlegen (UI)
- [ ] **TASK-009** Runde eingeben und auswerten (UI)
- [ ] **TASK-010** Spielstand anzeigen (UI)
- [ ] **TASK-011** Spiel abschließen / Sieger anzeigen (UI)

---

## Abgeschlossen

- [x] **TASK-000** Gherkin-Feature-Dateien (6 Features, alle Szenarien) — 26.06.2026
- [x] **TASK-000b** Gherkin-Nacharbeiten (3 fehlende Szenarien) — 28.06.2026
- [x] **TASK-000c** Engineering-Dokumentation (development-approach-v1.md, ADRs) — 28.06.2026
- [x] **TASK-000d** Domänenlogik (`domain.py` + `use_cases.py`, 28/28 Szenarien GREEN) — 02.07.2026
- [x] **TASK-000e** `docs/datenmodell-v1.puml` — PlantUML-Klassendiagramm angelegt und bereinigt — 18.07.2026

---

## Zukünftig / V2+ (noch nicht priorisiert)

- [ ] **FUTURE-001** i18n / Mehrsprachigkeit
  - `verbose_name`-Werte in `gettext_lazy(_())` einpacken
  - `LANGUAGE_CODE` + `LOCALE_PATHS` in `settings.py` konfigurieren
  - `.po`-Dateien für gewünschte Sprachen anlegen
  - Entscheidung: Bleibt die API-Sprache Deutsch oder wird sie ebenfalls übersetzt? → ADR anlegen
  - Fachbegriffe im Code (Ubiquitous Language) bleiben bewusst Deutsch — nur UI-Strings werden übersetzt

- [ ] **FUTURE-002** DRF (Django REST Framework) als Upgrade
  - Kandidat wenn: Auth, Throttling, Pagination oder OpenAPI-Schema benötigt werden
  - Normative Quelle: ADR-005 (JsonResponse für V1)

---

## Architektur-Entscheidungen (ADRs)

| ADR | Entscheidung |
|-----|-------------|
| ADR-001 | Backend vor Frontend |
| ADR-002 | Vertikale Slices |
| ADR-003 | behave als BDD-Toolchain |
| ADR-004 | Repository Pattern (Trennung Domäne/Persistenz) |
| ADR-005 | JsonResponse statt DRF für V1-API |
| ADR-006 | Behave-Tests via HTTP (Blackbox) statt direkter Use-Case-Aufrufe |

---

## Normative Quellen (Kurzreferenz)

| Thema | Dokument |
|-------|----------|
| Spielregeln | `docs/rule-set-v1.md` |
| Fachbegriffe | `docs/ubiquitous-language.md` |
| Sprachkonventionen | `docs/language-conventions.md` |
| Datenmodell | `docs/datenmodell-v1.puml` |
| Entwicklungsstrategie | `docs/development-approach-v1.md` |
| Gherkin-Phrasen | `docs/gherkin-step-phrase-reference-v1.md` |
| Vollständiger Handover | `docs/copilot-handover-v1.md` |
