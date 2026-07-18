# Backlog – Binokel Score Tracker V1

> **Workflow:** Session startet → diese Datei lesen → sofort im Bild.  
> Session endet → `BACKLOG.md` + `docs/copilot-handover-v1.md` + `/memories/repo/handover-status.md` synchron aktualisieren.

---

## ▶ Aktueller Fokus

**TASK-003 — Use Cases an ORM ankoppeln (Slice für Slice)**

`models.py` und Migrationen sind fertig (18.07.2026). Die Use Cases in `use_cases.py`
arbeiten derzeit ausschließlich auf reinen Python-Objekten ohne Persistenz.
Nach TASK-003 sollen alle 6 Slices Daten über das Django ORM speichern und laden.
behave muss weiterhin 28/28 GREEN bleiben.

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

- [ ] **TASK-003** Use Cases an ORM ankoppeln
  - Repository-Funktionen oder direkte ORM-Aufrufe in `use_cases.py`
  - Slices 1–6 nacheinander anbinden
  - Akzeptanztests (behave) müssen weiter GREEN bleiben

- [ ] **TASK-004** REST-Endpunkte — `views.py` + `urls.py`
  - Slice 1: `POST /api/spiele/` → spiel_anlegen
  - Slice 2: `POST /api/spiele/{id}/runden/` → normales_spiel_auswerten
  - Slices 3–6 analog
  - Entscheidung: DRF (Django REST Framework) oder einfaches JsonResponse? → ADR anlegen

- [ ] **TASK-005** `behave`-Szenarien gegen echte Django-API ausführen
  - `features/environment.py` ggf. anpassen (HTTP-Client statt direkter Use-Case-Aufrufe)
  - Alle 28 Szenarien müssen GREEN bleiben

### Phase 2 – Frontend (Vue) — noch nicht gestartet

- [ ] **TASK-006** Vue-Anwendung aufsetzen, API-Client konfigurieren
- [ ] **TASK-007** Spiel anlegen (UI)
- [ ] **TASK-008** Runde eingeben und auswerten (UI)
- [ ] **TASK-009** Spielstand anzeigen (UI)
- [ ] **TASK-010** Spiel abschließen / Sieger anzeigen (UI)

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

---

## Architektur-Entscheidungen (ADRs)

| ADR | Entscheidung |
|-----|-------------|
| ADR-001 | Backend vor Frontend |
| ADR-002 | Vertikale Slices |
| ADR-003 | behave als BDD-Toolchain |
| **offen** | DRF vs. einfaches JsonResponse für TASK-004 |

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
