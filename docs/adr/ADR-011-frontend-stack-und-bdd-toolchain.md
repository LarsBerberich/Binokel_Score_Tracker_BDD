# ADR-011 – Frontend-Technologie-Stack und BDD-Toolchain

## Status

Angenommen (23.07.2026)

## Kontext

Für Phase 2 (Frontend) ist der Technologie-Stack der Vue-SPA und die BDD-Toolchain
für die End-to-End-Ebene festzulegen. Die Produktvision (mobil-first, live am
Spieltisch nutzbar) und die bisherigen Prinzipien (Outside-In-BDD, deutsche
Fachsprache, schlanke Abhängigkeiten) sind Randbedingungen.

## Entscheidung

**Frontend-Framework und Werkzeuge:**

- **Vue 3.5** (Composition API) + **Vite** (Build/Dev-Server) + **TypeScript**
- **Vue Router** (Client-Routing, History-Mode) + **Pinia** (State)
- **Tailwind CSS** (utility-first, mobil-first)
- **PWA** via `vite-plugin-pwa`; **Capacitor-ready** für spätere native Verpackung
- **Vitest** für Unit-/Komponententests

**BDD-/E2E-Toolchain:**

- **Playwright** + **playwright-bdd** für die Gherkin-getriebene End-to-End-Ebene.

**API-Vertrag:**

- **Handgeschriebenes OpenAPI 3.1** jetzt (leichtgewichtig, kein DRF-Umbau).
  Automatische Schemagenerierung bleibt zurückgestellt (FUTURE-002).

## Begründung

- **Vue** ist bereits in `docs/project-foundation.md` §19 als Frontend-Richtung
  gesetzt; Vue 3.5 + Vite + TS ist der aktuelle, gut dokumentierte Standardpfad.
- **Tailwind** beschleunigt mobil-first-Layouts ohne eigenes Design-System (MVP).
- **Playwright + playwright-bdd** hält die Gherkin-Kultur des Projekts auch im
  Frontend konsistent (dieselbe Sprache/Feature-Denkweise wie Behave im Backend).
- **Handgeschriebenes OpenAPI 3.1** liefert einen präzisen Vertrag für den API-Client,
  ohne die bewusste DRF-Vermeidung (ADR-005) rückgängig zu machen.

### Teststrategie-Leitplanke (wichtig)

Die fachliche Abdeckung liegt schwerpunktmäßig auf der **API-Ebene** (18 Django-
Integrationstests + 28 Behave-HTTP-/Domänen-Szenarien). Die **E2E-Ebene (Playwright)
bleibt bewusst schlank**: kritische User-Journeys und Smoke-Pfade statt breiter
Nachbildung der Fachlogik. Verschwenderische E2E-Duplikation der bereits per API
abgedeckten Regeln wird vermieden. Diese Leitplanke ist vor dem breiten Ausbau der
playwright-bdd-Szenarien mit dem Repository-Eigentümer final abzustimmen.

> Ausformuliert und verbindlich festgelegt in **ADR-013 (Teststrategie und Testpyramide)**:
> Fachlichkeit auf API-Ebene, genau 1 E2E-Smoke jetzt, Richtwert ≤ 3–5 E2E-Szenarien bis MVP.

## Konsequenzen

### Positiv
- Moderner, wartbarer, gut dokumentierter Stack mit kleiner Einstiegshürde.
- Konsistente BDD-Kultur über Backend und Frontend hinweg.
- Mobil-first und PWA/Capacitor-Pfad ohne frühe Festlegung auf native Distribution.

### Negativ / Risiken
- Zusätzliche Toolchain (Node/npm, Playwright-Browser) im CI erhöht Build-Zeit/-Umfang.
- Handgepflegtes OpenAPI kann von der Implementierung abdriften → Disziplin/Review nötig
  (Gegenmittel später: FUTURE-002 Schemagenerierung).
- E2E-Tests sind langsamer/spröder als API-Tests → strikte Beschränkung auf Journeys.

### Meilenstein für Überprüfung
Bei wachsender API-Fläche oder Vertragsabweichungen: FUTURE-002 (automatisches
OpenAPI). Bei häufiger E2E-Sprödigkeit: Journey-Auswahl und Test-Doubles neu bewerten.

## Verweise
- ADR-005 (JsonResponse statt DRF), ADR-010 (Same-Origin-Deployment),
  ADR-003 (Behave als Backend-BDD-Toolchain), `docs/project-foundation.md` §16, §19.
