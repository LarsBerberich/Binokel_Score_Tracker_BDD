# Architektur-Konformitätsprüfung

**Stand:** 11.10.2026 (aktualisiert nach Umsetzung von F-01, F-02, F-08) · **Basis:** Commit `cff5878`, Umsetzung in `e09af75`, `eda8710`, `e064cc6` · **Methode:** statische Durchsicht von
Backend (`scoring/`), Frontend (`frontend/src/`), `deploy/`, CI/CD und ADR-001 bis ADR-017.
Nicht geprüft: Laufzeitverhalten, Performance, Sicherheits-Penetrationstest.

Bewertung: ✅ konform · ⚠️ teilweise · ❌ Abweichung

## 1. Zusammenfassung

Die Grundarchitektur ist für die Größe des Projekts solide: ein Domänenkern ohne
Abhängigkeiten, Repository-Pattern, vertikale Slices, BDD-Black-Box-Tests über HTTP,
supply-chain-bewusste CI/CD (SHA-gepinnte Actions) und dokumentierte Entscheidungen (ADRs).
Die ursprüngliche Hauptschwäche – **aufgeweichte Schichtentrennung aus ADR-004** (Fachlogik in
`views.py` und `repositories.py`) und **keine automatische Prüfung** – ist behoben (F-01, F-02,
F-08, siehe unten). Offen sind die Befunde F-03 bis F-07 und F-09 (Backlog: TASK-ARCH-002).

## 2. Prüfung nach Mustern

| Muster / Prinzip | Bewertung | Befund |
|---|---|---|
| Clean / Hexagonal: Abhängigkeiten nach innen | ✅ | `domain.py` importiert nichts aus dem Projekt, `use_cases.py` nur `domain`, kein Django-Import. Verifiziert über die Import-Zeilen. |
| Trennung Fachlogik / Infrastruktur | ✅ | F-01, F-02 behoben |
| Repository-Pattern (ADR-004) | ✅ | ORM-Zugriffe nur in `repositories.py`; `views.py` importiert keine Modelle. |
| Application-Service-/Use-Case-Schicht | ✅ | Rundenauswertung liegt in `use_cases.runde_auswerten`; Views parsen und mappen nur. Kein Port/Interface für Persistenz – bei diesem Umfang vertretbar. |
| Vertikale Slices / Evolutionäre Architektur | ✅ | ADR-002, Backlog nach Slices. Innerhalb von `scoring/` liegen die Slices aber als technische Schichten in je einer großen Datei. |
| API-First / Vertrag | ⚠️ | OpenAPI-Vertrag existiert, ist aber handgepflegt („PFLICHT-Sync“), `types.ts` ebenfalls von Hand (F-03). |
| Testpyramide / BDD (ADR-013) | ✅ | Gherkin-Akzeptanztests über HTTP, Vitest für Komponenten, ein Playwright-Smoke. |
| Same-Origin-SPA (ADR-010) | ✅ | Kein CORS, einfache Cookie-/CSRF-Lage. |
| 12-Factor-Konfiguration | ✅ | Secrets, Hosts, DB-Pfad über Umgebungsvariablen; Start bricht bei Insecure-Default-Key ab. |
| Infrastructure as Code / CI/CD | ⚠️ | Pipeline vorbildlich gepinnt; Provisionierung per Shell-Skript statt deklarativ, Deploy ohne Versions-/Rollback-Konzept sichtbar (F-07). |
| Observability | ❌ | Nur `/health/` und Access-/Error-Log. Keine strukturierten Logs, Metriken, Fehler-Tracking (F-06). |
| Security-by-Design | ⚠️ | Gute Härtung auf Host-Ebene (ADR-009). Aber offene Schreib-API ohne Auth und `csrf_exempt` (F-05). |
| Architecture Fitness Functions | ✅ | `import-linter` (Backend) und `dependency-cruiser` (Frontend) in der CI (F-08). |
| Dokumentation (ADR, C4) | ✅ | 17 ADRs, jetzt C4-Modelle. |

## 3. Befunde

### F-01 · Fachlogik in der HTTP-Schicht (hoch) — ✅ behoben in `e064cc6`
`views.py:167` `_runde_wertung_berechnen` hat rund 180 Zeilen: Typ-Dispatch
(normal / einfaches / doppeltes Abgehen / Tausender), Stern-Zuweisung, Stichzwang-Anwendung,
Aufbau der Gegenspieler-Daten und die M|S-Invariante. Das ist Anwendungs-/Fachlogik, kein
HTTP-Mapping. Folge: nicht ohne HTTP-Kontext testbar, `views.py` hat 650 Zeilen mit mehreren
Änderungsgründen. Das widerspricht dem Kern von ADR-004 („jede Datei genau ein Änderungsgrund“).
**Empfehlung:** als `runde_auswerten(typ, eingabe, spiel) -> Rundenwertung` (Dataclass) nach
`use_cases.py` verschieben; die View parst nur JSON und mappt Fehler auf Status.

### F-02 · Wertungsregel in der Persistenzschicht (hoch) — ✅ behoben in `eda8710`
`repositories.py:340` `_runde_beitrag` implementiert, wie eine Runde in den STAND eingeht
(Gewinn, Verlust, Mitpunkte, Tausender frieren ein) – eine Kernregel des Spiels –, und
`punktestaende_laden` aggregiert sie. Diese Regel ist ohne Datenbank nicht testbar und liegt
außerhalb der Domäne. **Empfehlung:** Repository liefert Runden als Domänenobjekte,
Berechnung des STAND liegt in `domain.py`/`use_cases.py`.

### F-03 · Vertrag ohne Maschinenprüfung (mittel)
Drei Quellen müssen manuell synchron bleiben: Django-Views, `binokel-api.v1.yaml`,
`frontend/src/api/types.ts`. **Empfehlung:** Typen aus OpenAPI generieren
(z. B. `openapi-typescript`) und im CI einen Vertragstest ergänzen
(z. B. `schemathesis` gegen die Django-App). Dafür ist keine Framework-Umstellung nötig.

### F-04 · Regeln doppelt implementiert (mittel)
`frontend/src/domain/regeln.ts` und `rotation.ts` spiegeln Backend-Konstanten und
Geber-Rotation (`Spiel.geber_in_runde`). Vertretbar für UX-Validierung, aber Drift-Risiko ohne
gemeinsame Testfälle. **Empfehlung:** Backend bleibt die einzige Wahrheit; Konstanten über
einen Endpunkt/Vertrag ausliefern oder gemeinsame Beispieltabelle in beiden Testsuiten nutzen.

### F-05 · Offene Schreib-API (mittel, bewusste V1-Entscheidung)
Alle Spiele sind für jeden mit der URL les- und schreibbar; die drei schreibenden Views sind
`csrf_exempt`, obwohl `CsrfViewMiddleware` aktiv ist. Das ist mit „keine Auth in V1“
(ADR-005) konsistent, aber im Internet exponiert und ohne Rate-Limiting (fail2ban schützt nur
sshd). **Empfehlung:** Rate-Limiting in Nginx (`limit_req`), Spiel-IDs nicht erratbar machen
(UUID/Token statt Auto-Inkrement), Entscheidung als ADR festhalten.

### F-06 · Fehlende Observability (mittel)
Nur Health-Endpunkt und Logdateien. **Empfehlung:** strukturierte Logs (JSON) mit
Request-ID, einfacher Uptime-Check extern, optional Sentry-kompatibles Fehler-Tracking.
Nicht überdimensionieren – ein ADR „Betriebsmindeststandard“ reicht.

### F-07 · Betrieb & Rollback (niedrig)
Single VM, SQLite, `rsync --delete`: für den Zweck passend. Nicht dokumentiert sind
Datenbank-Backup und Rollback auf die vorherige Version. `deploy/` enthält Runbooks;
**Empfehlung:** Backup-/Restore-Test und Rollback-Schritt dort ergänzen.

### F-08 · Keine Fitness Functions (niedrig, hoher Hebel) — ✅ behoben in `e09af75`
Die Schichtregel „`use_cases` und `domain` ohne Django“ wird nur durch Disziplin gehalten.
**Empfehlung:** `import-linter` (Backend, Verträge `domain` ← `use_cases` ← `views`, und
„`views` darf `models` nicht importieren“) und `dependency-cruiser` (Frontend:
Komponenten dürfen `api/client` nicht importieren). Beides als CI-Schritt. Zusätzlich fehlen
Linter/Typprüfung im Backend (`ruff`, `mypy`); das Frontend prüft Typen via `vue-tsc`.

### F-09 · Große Dateien (niedrig)
`views.py` 650, `repositories.py` 568, `RundeForm.vue` 570 Zeilen. Nach F-01/F-02 teilweise
erledigt; danach `scoring/` entlang der Slices in Module gliedern
(`spiel/`, `runde/`, `abrechnung/`), wenn weitere Slices hinzukommen.

## 4. Umsetzung und Restliste

Umgesetzt wurden F-08, F-02 und F-01 in dieser Reihenfolge. Die Tests (`features/`, `scoring/tests.py`,
`*.spec.ts`) blieben unverändert und waren vor und nach jedem Schritt grün (98 Django-Tests, 66 Behave-Szenarien).
Zusätzlich wurden die npm-Schwachstellen per Lockfile-Update behoben (`95dcd3d`).

Offen (niedrige Priorität, TASK-ARCH-002): F-03 (Vertragsgenerierung), danach F-05/F-06 als ADRs mit
kleinen Maßnahmen; F-04, F-07, F-09 nach Bedarf. Bekannte Lücke von F-08: Die Frontend-Regel
„Komponenten nutzen den API-Client nicht“ erkennt nur direkte Imports von `api/client`, nicht den Weg über `api/index.ts`.
