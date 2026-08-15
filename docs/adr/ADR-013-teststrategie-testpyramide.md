# ADR-013 – Teststrategie und Testpyramide

## Status

Angenommen (23.07.2026)

## Kontext

Mit Phase 2 entstehen mehrere Testebenen nebeneinander:

| Ebene | Werkzeug | Bestand | Zweck |
|---|---|---|---|
| Domäne / Unit (Backend) | Django/pytest | 18 Integrationstests | Regel- & Wertungslogik |
| Akzeptanz API (Backend) | Behave HTTP-Blackbox | 28 Szenarien | **Fachliche Wahrheit** (Gherkin) |
| Unit/Komponente (Frontend) | Vitest + Test Utils | 1 (Smoke) | Komponenten, Stores, API-Client |
| E2E (Frontend) | Playwright + playwright-bdd | 0 (geplant: 1) | Kritische User-Journeys |

Ohne klare Zuständigkeit droht **teure Duplikation**: Die Binokel-Fachregeln würden
sonst auf E2E-Ebene erneut nachgebaut, obwohl sie bereits per API-Szenarien vollständig
abgedeckt sind. E2E-Tests sind langsamer, spröder und wartungsintensiver.

## Entscheidung

**1. Fachlichkeit lebt auf der API-Ebene.** Die Gherkin-Fachwahrheit bleibt in den
Behave-HTTP-Szenarien (`features/`). Neue Fachregeln werden **dort** spezifiziert,
nicht in Playwright.

**2. Zuständigkeit je Ebene (keine Überlappung):**

- **Behave HTTP** — alle fachlichen Rundentypen, Wertung, Sieger, Fehlerfälle.
- **Vitest** — Komponenten-Rendering, Formular-/Store-Logik, API-Client-Verhalten
  (Fehler-Mapping, URL-Bildung) mit **gemocktem `fetch`** (kein echtes Backend).
- **Playwright/playwright-bdd** — nur **kritische Ende-zu-Ende-Journeys** gegen echtes
  Frontend+Backend: „App lädt", später ggf. „Spiel anlegen → Runde eintragen → Sieger
  sehen" als **einzelner** Happy-Path.

**3. E2E-Budget (harte Leitplanke):**

- **Jetzt: genau 1 Smoke-Szenario** (App lädt, Startseite sichtbar).
- Jede weitere E2E-Journey erfordert eine **explizite Einzelentscheidung**
  (Begründung: fachliches Risiko, das API/Unit **nicht** abdecken).
- Richtwert-Obergrenze bis MVP: **≤ 3–5 E2E-Szenarien** insgesamt.

**4. Kein E2E-Nachbau von API-Regeln.** Wenn eine Prüfung auch per Behave (API) oder
Vitest (Komponente) möglich ist, gehört sie **dorthin**.

**5. Testorganisation im Frontend – Co-Location.** Unit-/Komponententests liegen
**direkt neben** der geprüften Einheit (Co-Location), z. B. `RundeForm.spec.ts` neben
`RundeForm.vue` in `src/components/`. Das ist die im Vue-/Vite-/Vitest-Ökosystem
übliche Best Practice und bewusst gewählt:

- **Erkennbarkeit** über die Namenskonvention `*.spec.ts` (alternativ `*.test.ts`);
  Vitest sammelt sie über den Glob `src/**/*.{test,spec}.ts` (`vite.config.ts`).
- **Nähe & Wartung:** Test wandert bei Umbenennung/Verschiebung mit der Einheit;
  fehlende Tests fallen im selben Verzeichnis eher auf.
- **Kein Produktions-Ballast:** `*.spec.ts`-Dateien werden von keinem App-Code
  importiert und landen daher **nicht** im Vite-Build-Output (`dist/`).
- **E2E ist getrennt:** Playwright-Journeys liegen außerhalb von `src/` unter
  `frontend/e2e/` (eigener CI-Job `frontend-e2e`).

Ein gespiegeltes Top-Level-`tests/`-Verzeichnis wird im Frontend **nicht** verwendet.
Backend-Tests bleiben davon unberührt: Django-Tests in `backend/scoring/tests.py`,
Behave-Akzeptanztests in `features/`.

## Begründung

- Die API-Blackbox-Tests (ADR-006) decken die Fachlogik bereits sprachlich (Gherkin)
  und vollständig ab → E2E-Duplikation wäre Verschwendung.
- Testpyramide: viele schnelle Unit/API-Tests, wenige teure E2E-Tests.
- Same-Origin-Deployment (ADR-010) macht 1 echten E2E-Durchstich wertvoll
  (Integration Frontend↔API↔Nginx), aber nur als schmale Absicherung.

## Konsequenzen

### Positiv
- Schnelle, stabile CI; klare Verantwortlichkeiten; wenig Flakiness.
- Fachänderungen haben **einen** Ort (Behave-Features).

### Negativ / Risiken
- E2E deckt UI-Details bewusst nicht breit ab → manuelle/geführte Tests für UX nötig.
- Disziplin erforderlich, damit E2E nicht „aus Bequemlichkeit" wächst (Review-Gate).

### Meilenstein für Überprüfung
- Vor jedem Ausbau > 1 E2E-Szenario; spätestens bei MVP-Abschluss Ratio erneut bewerten.

## Verweise
- ADR-003 (Behave als Backend-BDD-Toolchain), ADR-006 (HTTP-Blackbox-Tests),
  ADR-011 (Frontend-Stack + Teststrategie-Leitplanke), `docs/project-foundation.md` §16.
