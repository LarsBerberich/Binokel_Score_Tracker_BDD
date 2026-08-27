# Copilot-Handover für V1

## Ziel
Dieses Repository modelliert fachlich einen Binokel Score Tracker auf Basis von BDD.

## Führende Dokumente
Die folgende Priorität gilt bei fachlichen Unklarheiten:

1. `docs/rule-set-v1.md`
2. `docs/ubiquitous-language.md`
3. `docs/language-conventions.md`
4. `docs/Anschreibetabelle_4_Spieler.md`

## Engineering-Dokumente
Für Entwicklungsprozess und technische Entscheidungen:

- `docs/project-foundation.md` – Produktvision, BDD-Strategie, Architektur- und Technologieprinzipien
- `docs/development-approach-v1.md` – Operativer Entwicklungsansatz: Outside-In, RED-Green-Refactor, Vertikale Slices, Phasenmodell
- `docs/agents/coding-agent.md` – Rollenbeschreibung Coding-Agent
- `docs/agents/rubber-duck-agent.md` – Rollen- und Prompt-Guide für den ergänzenden Rubber-Duck-Agenten
- `docs/agents/devops-agent.md` – Rollenbeschreibung Dev/Ops-Agent
- `docs/agents/orchestration.md` – Orchestrierungs-Workflow der Agenten
- `docs/adr/ADR-001-backend-vor-frontend.md` – Backend vor Frontend in Phase 1
- `docs/adr/ADR-002-vertikale-slices.md` – Vertikale Slices statt horizontaler Schichten
- `docs/adr/ADR-003-behave-als-bdd-toolchain.md` – behave als BDD-Toolchain für Django
- `docs/adr/ADR-004-repository-pattern.md` – Repository Pattern zur Trennung von Domäne und Persistenz
- `docs/adr/ADR-005-jsonresponse-statt-drf.md` – JsonResponse statt Django REST Framework für V1
- `docs/adr/ADR-006-behave-http-blackbox-tests.md` – Behave-Akzeptanztests via HTTP (Blackbox)
- `docs/adr/ADR-007-github-actions-ci-cd.md` – GitHub Actions als CI/CD-Toolchain
- `docs/adr/ADR-008-vm-deployment-strategie.md` – VM-Deployment via systemd/Gunicorn/Nginx
- `docs/adr/ADR-009-internet-hardening-baseline.md` – Internet-Hardening-Baseline der VM
- `docs/adr/ADR-010-frontend-deployment-same-origin.md` – Frontend Same-Origin-Deployment
- `docs/adr/ADR-011-frontend-stack-und-bdd-toolchain.md` – Frontend-Stack (Vue) und BDD-Toolchain
- `docs/adr/ADR-012-node-toolchain-fnm.md` – Node-Toolchain via fnm
- `docs/adr/ADR-013-teststrategie-testpyramide.md` – Teststrategie/Testpyramide
- `docs/adr/ADR-014-zehner-eingabe-und-endrunden-tiebreak.md` – Zehner-Eingabe des STAND + Endrunden-Tiebreak
- `docs/adr/ADR-015-korrektur-nur-letzte-runde.md` – Korrektur: nur die letzte Runde bearbeitbar

## V1-Scope
V1 unterstützt ausschließlich:

- 4 Spieler
- Einzelwertung
- Geber setzt aus
- feste Spielerreihenfolge gegen den Uhrzeigersinn
- feste Rundenzahl als Vielfaches von 4
- Default: 12 Runden

Nicht Teil von V1 sind insbesondere:

- Zielspiel-Endbedingungen wie 1000 oder 1500
- Teamwertung
- andere Spielerzahlen

## Wichtige Rundenausgänge
- gewonnenes Spiel
- einfaches Abgehen
- doppeltes Abgehen
- Tausender gewonnen
- Tausender verloren

## Fachliche Kernaussagen
- Der Geber spielt in der Runde nicht mit.
- In der Geber-Spalte wird in der Rundenzeile ein Strich dargestellt.
- Der Spielmacher nimmt den Dapp auf und drückt anschließend 4 Karten.
- Dapp und gedrückte Karten sind fachlich nicht dasselbe.
- Eingegebene Stichwerte enthalten den letzten Stichbonus bereits.
- Die Gesamtsumme aus Stichwerten einschließlich gedrückter Karten und letztem Stich beträgt 250.
- Wenn zwei Stichwerte bekannt sind, kann der dritte automatisch ermittelt werden.
- Reizwerte und Mitpunkte sind volle 10er.
- Nur Stichwerte können 1er-genau sein.
- Im Regelfall werden Stichwerte auf volle 10 gerundet gespeichert.
- In der letzten Runde werden bei möglichem Gleichstand zusätzlich exakte 1er-Werte berücksichtigt.

## Stich-Zwang
- Im Normalfall gilt der Stich-Zwang für alle aktiven Spieler.
- Meldepunkte zählen nur mit mindestens einem eigenen Stich.
- Beim einfachen Abgehen behalten die Gegenspieler ihre Meldepunkte auch ohne eigenen Stich.
- Beim doppelten Abgehen gilt für Gegenspieler weiterhin der normale Stich-Zwang.

## Verlustwertung
- Einfaches Abgehen: negativer einfacher Reizwert
- Doppeltes Abgehen: negativer doppelter Reizwert
- Verlustwerte werden in der Darstellung mit Minuszeichen und in Klammern geschrieben.

## Tausender
- Keine Meldepunkte
- Keine Stichwerte
- Keine Mitpunkte
- Kein Einfluss auf den numerischen Punktestand
- Sterne nur als Zusatzinformation
- Ausgang wird explizit als gewonnen oder verloren erfasst

## Stand 26.08.2026 (TASK-014 Nacharbeit — 3 Findings aus Pairing-Durchspielen behoben)

Beim manuellen Durchspielen der Anschreibetabelle + Korrektur-Flow (Tester-Agent Pairing) wurden
drei Findings gefunden und behoben (`docs/testing/explorative-testprotokoll.md` FND-003…005):

- **FND-003 (Bug):** `(0 Stiche)`-Schneider-Annotation erschien fälschlich bei einfachem Abgehen.
  Wurzel: Das Backend liefert `rundenausgang` als **Klartext** (`"einfaches Abgehen"`,
  `domain.Rundenausgang.value`), Frontend und Frontend-Tests verglichen fälschlich gegen **Slugs**
  (`'einfaches_abgehen'`). Die falschen Slug-Testdaten maskierten den Bug. Fix: zentrale
  `RUNDENAUSGANG`-Klartext-Konstanten in `api/types.ts`; `Anschreibetabelle.vue` und
  `SpielView.vue::ausgangZuTyp` vergleichen gegen Klartext; Tests + OpenAPI-Doku korrigiert. Der
  latente Nebenbug (Korrektur-Vorbelegung von einfachem Abgehen/Tausender fiel immer auf „normal“)
  ist damit ebenfalls behoben.
- **FND-005 (Darstellung):** Der Rundenausgang war in der Anschreibetabelle nicht ausgewiesen.
  `Anschreibetabelle.vue` zeigt jetzt je Runde ein Ausgangs-Label unter „Gereizt bis“
  (`ausgangLabel`, `data-testid=ausgang-{nr}`).
- **FND-004 (Persistenz, Rubber-Duck GO Option A):** Die Korrektur einer als **doppeltes Abgehen**
  gewerteten Runde war blockiert (SM-Stichwert mit 0 vorbelegt → Kontrollsumme 190/250 → Speichern
  gesperrt). Fix: Bei doppeltem Abgehen werden die roh erfassten Spielmacher-`M | S` persistiert
  (Korrektur-Beleg). Die Invariante `spielmacher_punkte == M + S` gilt damit nur bei gewonnenem
  Spiel; einfaches Abgehen/Tausender bleiben `0 | 0`. Anschreibetabelle (`(-x)|0|0`) und STAND
  (`verlustwert`) bleiben unberührt — kein Frontend-Code-Change. Doku: `models.py`,
  `datenmodell-v1.puml`, `ubiquitous-language.md` §4.25, ADR-015-Nachtrag.

Validierung: **55 Django + 31 Behave + 59 Vitest + Build** grün; zusätzlich Live-Browser (FND-003/005)
und Live-curl (FND-004: GET liefert SM-Stichwert 60 statt 0). Kein neues E2E (ADR-013). Nicht committet.

## Stand 17.08.2026 (Phase 2b — TASK-013 Tausender-Sterne anzeigen, Backend + Frontend)

Der Wertungsbereich zeigt jetzt die **Tausender-Sterne** je Spieler. Ein Stern entsteht
ausschließlich aus Tausender-Runden (§15): Der Spielmacher erhält bei „Tausender gewonnen"
einen Stern, bei „Tausender verloren" erhält **jeder aktive Gegenspieler** einen Stern.

Backend: `sterne_laden(spiel_id)` in `repositories.py` aggregiert die booleschen
`RundeModel.spielmacher_stern`/`gegenspieler_stern`-Felder je Spieler. Beide Slice-6-Endpunkte
(`punktestaende/` und `sieger/`) liefern additiv ein `sterne: {name: int}`-Mapping
(rückwärtskompatibel, keine Migration). **Kernfallstrick (RD-bestätigt):** Bei Tausender-Runden
werden **keine** `GegenspielerRundeModel`-Zeilen angelegt — die aktiven Gegenspieler müssen
daher aus `alle Spieler − Geber − Spielmacher` hergeleitet werden (der Geber setzt aus und
bekommt keinen Stern, §15.3). Der Django-Test `SterneApiTest` sichert insbesondere
„Tausender verloren" gezielt ab.

Frontend: neuer Typ `SterneMap`; `SpielView` (laufender Punktestand) und `SpielendeView`
(Endstand) zeigen die Sterne symbolisch als `★` (`data-testid="sterne-{name}"`, nur wenn
count > 0). Doku-Sync: OpenAPI (`Punktestaende` + `SiegerErgebnis` um `sterne`), Typen,
BACKLOG. Kein neues Datenmodell/Regelwerk nötig (Sterne stammen aus bestehenden Feldern).
Validierung: 26 Django + 28 Behave + 37 Vitest grün, Build grün. Kein neues E2E (ADR-013).

## Stand 15.08.2026 (Plausibilitätsregel Meldepunkte — aus Live-Test)

Beim manuellen Durchspielen fiel auf, dass die Meldepunkte eines einzelnen Spielers
unbegrenzt eingegeben werden konnten. Eingeführt wurde eine **Plausibilitätsgrenze**:
Meldepunkte je Spieler und Runde liegen zwischen **0 und 1800**. Das Maximum von 1800
ist das theoretische Höchstmaß im württembergischen Doppelblatt — **doppelte Familie**
einer Farbe (1500) plus **doppelter Binokel** (300), wobei die beiden Blatt-Ober der
Familie zugleich den Binokel bilden (Karten dürfen mehrfach gemeldet werden). Das
allgemeine Binokel-Regelwerk wurde dazu gegengeprüft.

Durchsetzung mehrschichtig: Domäne (`MELDEPUNKTE_MAXIMUM`, `UngueltigeMeldepunkte`),
Use Case (`meldepunkte_validieren`), HTTP-View (Rundenerfassung → 400 bei Verstoß) sowie
im `RundeForm`-UI (Absenden gesperrt + Hinweis). Nachgezogen: `rule-set-v1.md` §7.1
(Herleitung), `ubiquitous-language.md` §4.9, OpenAPI-Vertrag (`minimum: 0`, `maximum: 1800`).
Validierung: 22 Django + 28 Behave + 35 Vitest grün, Build grün, Live-curl (1801 → 400,
1800 → 201).

## Stand 24.07.2026 (Phase 2b — TASK-012 Häppchen B: Stichwerte 1er-genau, Auto-3.-Stichwert, Ableitungen)

**TASK-012 komplett** (Häppchen A + B). Häppchen B umgesetzt + validiert; anschließend
Rubber-Duck-Review.

- **Regel-Korrektur (USER 24.07.2026): Stichwerte 1er-genau.** „Bei knappen Spielen ist ein
  genaues Zählen auf Einer-Werte notwendig." → Stichwert-Felder `step=1` (statt 10). `rule-set-v1.md`
  §9.1 + §17.2 aktualisiert: UI erfasst Stichwerte grundsätzlich 1er-genau; Rundung auf 10 ist nur
  optionale Bequemlichkeit, wird nie erzwungen. **Meldepunkte + Reizwert bleiben `step=10`.** Der
  frühere „Tiebreak-Nachzügler" (§9.3/§17.2) ist damit nativ erledigt — kein Sonderfeld nötig.
- **`RundeForm.vue` (012.3/012.5/012.7):**
  - **012.3** Stich-Checkboxen (`sm-stich`/`gs-stich-*`) + `hatEigenenStich` aus `SpielerDetail`
    entfernt. Payload leitet `hat_eigenen_stich = stichwerte > 0` ab (Spielmacher + je Gegenspieler).
  - **012.5** Dritter Stichwert automatisch = `250 − w1 − w2`, sobald zwei der drei aktiven Werte
    erfasst sind. Tracking via `stichwertReihenfolge` (zwei zuletzt bearbeitete gewinnen);
    `autoStichwertSpieler` ist **read-only** + Hinweis „— automatisch". Negativer Auto-Wert →
    `stichwerte-fehler`-Hinweis + `runde-absenden` gesperrt (`stichwerteNegativ` in `normalGueltig`).
  - **012.7** `doppeltes-abgehen-hinweis`: bei normalem Spiel live, wenn `spielmacherGesamt`
    (M+S) < Reizwert (§16.1 nachvollziehbar).
- **Tests (Vitest, ADR-013):** `RundeForm.spec.ts` — Normal-Test auf Auto-Berechnung umgestellt
  (2 Stichwerte eingegeben, 3. read-only + auto), neue Tests: Ableitung `hat_eigenen_stich=false`
  bei Auto-0-Stichwert (012.3), doppeltes-Abgehen-Hinweis (012.7), Negativ-Stichwert sperrt Runde
  (RD-S3, Werte >250). **34 Tests grün (6 Dateien),
  Build (vue-tsc) grün.** Per curl: Normal-Payload → 201, Punktestände Bernd 190 / Carla 80 /
  Dirk 60 / Anna 0 (200). **Hinweis:** API-Endpunkte brauchen Trailing-Slash; Create-Response liefert
  `id` (nicht `spiel_id`).
- **Offen:** Live-Cut-Over unverändert; nichts committet/gepusht (User: „Commit später").
- **Nächster Schritt:** **TASK-013** (Sterne im Wertungsbereich, Prio vor TASK-014).

## Stand 24.07.2026 (Phase 2b — TASK-012 Häppchen A: Rundenerfassung regelkonform verfeinert)

**Erstes Durchspielen der Rundenerfassung (nach MVP-Loop) → USER-Feedback + Rubber-Duck-Review
→ Phase 2b (TASK-012/013/014) geplant** (siehe `BACKLOG.md`). **Häppchen A von TASK-012
umgesetzt + validiert.**

- **Hausregel verankert:** Reizwert-Minimum **150** (gängige Turnierpraxis) in `rule-set-v1.md` §7
  und `ubiquitous-language.md` §4.14; im UI mit 150 vorbelegt. Domänenkonstanten in
  `src/domain/regeln.ts`: `REIZWERT_MINIMUM = 150`, `ZEHNER_SCHRITT = 10`.
- **`RundeForm.vue` (012.1/012.2/012.4/012.6):**
  - **012.1** „Doppeltes Abgehen" aus der Rundentyp-Auswahl entfernt — wird bei normalem Spiel
    automatisch abgeleitet (M+S < Reizwert, §16.1). `absenden()`-Zweig + `istDoppeltesAbgehen`/
    `istAbgehen` entfernt; Abgehen-Block auf einfaches Abgehen reduziert. **API-Typ
    `RundeDoppeltesAbgehen` bleibt** (Vertrag unberührt).
  - **012.2** Reizwert `min=150 step=10` Default 150 (`reizwertGueltig` prüft `>= 150`);
    Meldepunkte + Stichwerte `step=10`.
  - **012.4** Manuelle Sterne-Checkboxen (`sm-stern`/`gs-stern`) + Refs entfernt — Sterne ergeben
    sich nur aus dem Tausender-Ausgang und werden vom Backend gesetzt (§15.3/§15.5).
  - **012.6 BUG-FIX** Formular-Reset nach Wertung über `watch(() => props.rundennummer)` →
    `resetEingaben()` (typ→`normal`, reizwert→150, Melde/Stich→0). Reset kommt bewusst aus dem
    Parent (RundeForm kennt den POST-Erfolg nicht).
- **Tests (Vitest, ADR-013):** `RundeForm.spec.ts` — doppeltes-Abgehen-Test entfernt, neuer Test
  „bietet Doppeltes Abgehen nicht an", Sterne aus dem Normal-Payload entfernt, neuer Reset-Test.
  **31 Tests grün (6 Dateien), Build (vue-tsc) grün.** Per curl verifiziert: schlanker Normal-Payload
  ohne Stern-Felder → 201, Punktestände Bernd 190 / Carla 80 / Dirk 60 / Anna 0 (200).
- **Rubber-Duck-Entscheide für Häppchen B (offen):** 012.5 Auto-Feld **read-only** („zwei
  bearbeitete gewinnen, drittes berechnet + gesperrt") gegen „unset vs. bewusst 0"-Ambiguität;
  012.3 `hat_eigenen_stich = stichwerte > 0` (Edge-Case „kleiner Stich → 0" irrelevant, kleinster
  Stich = 6). §9.3/§17.2 (1er-genaue Tiebreak-Stichwerte) bleibt bewusster V1-Nachzügler.
- **Offen:** Live-Cut-Over (s. u.) unverändert; nichts committet/gepusht (User: „Commit später").
- **Nächster Schritt:** TASK-012 **Häppchen B** (012.3/012.5/012.7) mit Rubber-Duck-Schleife,
  danach **TASK-013** (Sterne im Wertungsbereich, Prio vor TASK-014).

## Stand 24.07.2026 (Phase 2 Frontend — TASK-011 Sieger anzeigen, UI Slice 6 abgeschlossen — MVP-Loop komplett)

**TASK-011 (Spiel abschließen / Sieger anzeigen, UI, Slice 6) ist abgeschlossen.** Damit ist
der **Phase-2-MVP-Loop komplett**: Spiel anlegen → Runden aller fünf Typen erfassen →
laufender Punktestand → Spielende → Sieger.

- **View** `src/views/SpielendeView.vue` (vorher Platzhalter) — lädt in `onMounted`
  `siegerErmitteln(Number(spielId))` → `SiegerErgebnis` (`{spiel_id, punktestaende, sieger}`).
  Zeigt: Sieger-Banner (einzeln „Sieger: X" oder „Gleichstand – mehrere Sieger: X, Y" bei
  `sieger.length > 1`), absteigenden Endstand (Sieger via `sieger.includes(name)` hervorgehoben),
  `RouterLink` „Neues Spiel" → Route `start`. Lade-/Fehlerzustand analog `SpielView`.
- **Erreichbar** über den „Zur Auswertung"-Link im Beendet-Bereich von `SpielView` (TASK-009.6)
  bzw. direkt via `/spiel/:spielId/ende` (die View lädt eigenständig, kein Store nötig).
- **Tests (Vitest, ADR-013):** `SpielendeView.spec.ts` — alleiniger Sieger + Endstand-Sortierung,
  Gleichstand (mehrere Sieger), Fehlerfall (`vi.mock('../api')` siegerErmitteln, `RouterLinkStub`).
  **30 Tests grün (6 Dateien), Build (vue-tsc) grün.** Per curl verifiziert: Sieger nach 1 Runde
  `["Bernd"]` (200). **Kein neues E2E-Szenario.**
- **Bewusst zurückgestellt (Nachzügler):** UI-Eingabe für **exakte 1er-Stichwerte** (Tiebreak
  bei Gleichstand in der letzten Runde). Das Backend unterstützt `?exakte_stichwerte=Name:Wert,…`
  bereits; der Client-Funktion `siegerErmitteln(spielId, exakteStichwerte?)` ist der Parameter
  schon bekannt. Im UI noch nicht exponiert (lean; kann bei Bedarf ergänzt werden).
- **Offen:** Live-Cut-Over (s. u.) unverändert; nichts committet/gepusht (User: „Commit später").
- **Nächster Schritt:** Durchspielen + Frontend-Feedback (Flow/UX), danach gebündelte visuelle
  Politur über alle Screens; optional der exakte-Stichwerte-Tiebreak.

## Stand 24.07.2026 (Phase 2 Frontend — TASK-010 Spielstand anzeigen, UI Slice 6 Punktestände abgeschlossen)

**TASK-010 (Spielstand anzeigen, UI, Slice 6, Punktestände) ist abgeschlossen.** `SpielView`
zeigt jetzt den laufenden Punktestand.

- **View** `src/views/SpielView.vue` — hält `punktestaende` (`PunktestandMap | null`) und
  `punktestaendeAktualisieren()`; ruft `punktestaendeLaden(spielId)` **beim Öffnen** und
  **nach jeder gewerteten Runde** auf. Ladefehler sind weich (Punktestand ist ergänzende
  Info → blockiert die Rundenerfassung nicht, `punktestaende` fällt auf `null` zurück).
- **Anzeige** — Sektion `data-testid="punktestaende"` zwischen Header und Rundenerfassung
  (also während des Spiels **und** im Beendet-Bereich sichtbar). Computed `sortierteStaende`
  sortiert **absteigend** (höchster Punktestand zuerst → führt zur Siegerlogik in TASK-011);
  Führender hervorgehoben. Einträge `data-testid="punktestand-{name}"`.
- **Tests (Vitest, ADR-013):** `SpielView.spec.ts` um `punktestaendeLaden`-Mock erweitert
  (Default 0/0/0/0 in `beforeEach`) + neuer Test „lädt und zeigt die Punktestände absteigend
  sortiert". **27 Tests grün, Build (vue-tsc) grün.** Per curl verifiziert: nach 1 normalen
  Runde `{Anna:0, Bernd:190, Carla:80, Dirk:60}` (200). **Kein neues E2E-Szenario.**
- **Offen:** Live-Cut-Over (s. u.) unverändert; nichts committet/gepusht (User: „Commit später").
- **Nächster Schritt:** TASK-011 (Spiel abschließen / Sieger anzeigen – UI, Slice 6);
  `siegerErmitteln()` im Client vorhanden, `SpielendeView` noch Platzhalter.

## Stand 24.07.2026 (Phase 2 Frontend — TASK-009 Runde eingeben und auswerten, UI Slices 2–5 abgeschlossen)

**TASK-009 (Runde eingeben und auswerten, UI, Slices 2–5) ist abgeschlossen** (Subtasks
009.1–009.6). Alle fünf Rundentypen sind über die UI erfassbar und werden vom Backend
gewertet; das TASK-008-Schichten-Muster (Store / präsentationsnahe Komponente / View)
wurde konsequent fortgesetzt.

- **Domänenmodule (rein, isoliert getestet):**
  - `src/domain/rotation.ts` — `geberFuerRunde(spieler, rundennummer)` (`(rundennummer-1) %
    n`), `aktiveSpieler(spieler, geber)` (Geber setzt aus), `gegenspielerNamen(aktive,
    spielmacher)`. Normativ rule-set §3: bei 4 Spielern spielen 3 aktiv, der Geber setzt aus.
  - `src/domain/regeln.ts` — `STICHWERT_KONTROLLSUMME = 250` (rule-set §5.3).
- **Präsentationsnahe Komponente** `src/components/RundeForm.vue` — deckt **alle fünf
  Rundentypen** ab (normal, einfaches/doppeltes Abgehen, Tausender gewonnen/verloren).
  Detaileingaben je aktivem Spieler in einer `reactive`-Map (per `watch` an die aktiven
  Spieler gekoppelt); Gegenspieler = aktive minus Spielmacher (computed). Typabhängige
  Felder via `v-if`/`<template v-if>`:
  - **normal:** Reizwert + Spielmacher- und Gegenspieler-Details (Meldepunkte/Stichwerte/
    eigener Stich), **Live-Kontrollsumme muss genau 250 ergeben**, Sterne → `RundeNormal`.
  - **einfaches Abgehen:** nur Gegenspieler-Meldepunkte (kein Stich-Zwang, keine 250er-Summe)
    → `RundeEinfachesAbgehen` (`gegenspieler: [{name, meldepunkte}]`).
  - **doppeltes Abgehen:** volle Gegenspieler-Daten inkl. Stich-Zwang → `RundeDoppeltesAbgehen`.
  - **Tausender:** keine Zahlenfelder → `RundeTausender` (Sterne setzt das Backend).
- **View** `src/views/SpielView.vue` — lädt das Spiel aus dem Store (oder per `spielLaden`,
  falls direkt aufgerufen), zeigt Rundenfortschritt (`Runde X / Y`), Geber (setzt aus),
  aktive Spieler und das letzte Ergebnis; reicht `rundeAuswerten()` durch → `letztesErgebnis`
  + `naechsteRunde()`. Bei Spielende (`rundennummer > rundenanzahl`) erscheint der
  Beendet-Bereich mit `RouterLink` zur Auswertung (`/spiel/:spielId/ende`).
- **Store** `src/stores/spiel.ts` — um `aktuelleRundennummer` + `naechsteRunde()` erweitert;
  `setzeSpiel` setzt die Rundennummer auf 1 zurück.
- **Tests (Vitest, ADR-013):** `rotation.spec.ts`, `RundeForm.spec.ts` (Gegenspieler-
  Ableitung, normal gesperrt/gültig bei Summe 250, einfaches/doppeltes Abgehen, Tausender,
  Fehler), `SpielView.spec.ts` (Store-/API-Laden, Fehler, Spielende-Link via `RouterLinkStub`).
  **26 Tests grün, Build (vue-tsc) grün.** Alle fünf Rundentypen zusätzlich per curl gegen
  das echte Backend geprüft (201). **Kein neues E2E-Szenario** (ADR-013).
- **Fachliche Entscheidung:** Die Backend-API-Tests verwenden teils 3 Gegenspieler inklusive
  Geber; das Frontend folgt der **normativen** `rule-set-v1.md` (Geber setzt aus → 2
  Gegenspieler, Stichwerte-Summe 250). Das Backend erzwingt beides im HTTP-Pfad nicht.
- **Offen:** Live-Cut-Over (s. u.) unverändert; nichts committet/gepusht (User: „Commit später").
- **Nächster Schritt:** TASK-010 (Spielstand anzeigen – UI, Slice 6, Punktestände);
  `SpielendeView` ist noch Platzhalter.

## Stand 24.07.2026 (Phase 2 Frontend — TASK-008 Spiel anlegen, UI Slice 1 abgeschlossen)

**TASK-008 (Spiel anlegen, UI, Slice 1) ist abgeschlossen** — erste echte View auf dem
TASK-007-Fundament; Muster für die folgenden UI-Slices (TASK-009–011) ist etabliert.

- **Schichten-Muster (bewusst getrennt, wird für weitere Slices wiederverwendet):**
  - **Pinia-Store** `src/stores/spiel.ts` — hält das aktuelle Spiel (`aktuellesSpiel`,
    `setzeSpiel`); schlank, wird in späteren Slices um Runden-/Punktestand-State erweitert.
  - **Präsentationsnahe Komponente** `src/components/SpielAnlegenForm.vue` — 4 Spielernamen
    + Rundenanzahl, reine Client-Validierung (alle Namen gefüllt, eindeutig, Rundenanzahl
    positives Vielfaches von 4), Absenden-Button gesperrt bis gültig, meldet gültige Eingabe
    per `absenden`-Event. **Kennt keine API** → isoliert testbar.
  - **View** `src/views/StartView.vue` orchestriert die Seiteneffekte: `spielAnlegen()` →
    Store setzen → `router.push({ name: 'spiel', params: { spielId } })`; `ApiError`-Meldung
    inline, Lade-/Fehlerzustand an das Formular durchgereicht.
- **Tests (Vitest, ADR-013):** `SpielAnlegenForm.spec.ts` (Validierung, Trimmen, Emit-Payload,
  Sperr-/Fehlerzustände) + `StartView.spec.ts` (Integration mit gemocktem API-Client via
  `vi.mock('../api')`, Pinia, Memory-Router: Erfolg → Store+Navigation, Fehler → Meldung +
  keine Navigation). **11 Tests grün, Build (vue-tsc) grün.** Kein neues E2E-Szenario.
- **Offen:** Live-Cut-Over (s. u.) unverändert; nichts committet/gepusht (User: „Commit später").
- **Nächster Schritt:** TASK-009 (Runde eingeben und auswerten – UI, Slices 2–5).

## Stand 23.07.2026 (Phase 2 Frontend — TASK-007 Vue-Fundament abgeschlossen)

**TASK-007 (Vue-Fundament) ist vollständig abgeschlossen** — `frontend/` steht als
lauffähiges, getestetes Gerüst; die UI-Slices (TASK-008–011) können darauf aufsetzen.

- **Gerüst:** Vite + Vue 3.5 + TypeScript; Vue Router (History-Mode) + Pinia; Tailwind
  CSS v4 (`@tailwindcss/vite`, mobil-first). Node via `frontend/.node-version` = `22`
  (fnm, ADR-012) + `engines.node` `>=22 <23`.
- **Route-Struktur (leer, an Slices ausgerichtet):** `start` (Slice 1) /
  `spiel/:spielId` (Slices 2–5) / `spielende` (Slice 6) + 404; Views lazy-geladen.
- **API-Vertrag zuerst:** `frontend/openapi/binokel-api.v1.yaml` — handgeschriebenes
  OpenAPI 3.1 (5 Endpunkte + `/health/`, `oneOf`+Discriminator für die 5 Rundentypen).
  Daraus abgeleitet: TS-Typen (`src/api/types.ts`) + dünner `fetch`-Client
  (`src/api/client.ts`, relative Basis `/api`, `ApiError`).
- **Tests (Testpyramide, ADR-013):** Vitest-Smoke grün; **genau 1** Playwright-E2E-Smoke
  (`e2e/features/smoke.feature`, deutsch) grün. **Verbindliche Teststrategie in ADR-013:**
  Fachlichkeit bleibt auf API-Ebene (18 Django + 28 Behave), E2E-Budget ≤ 3–5 bis MVP,
  kein Ausbau > 1 Szenario ohne Einzelentscheidung.
- **Dev = Prod-Same-Origin:** Vite-Dev-Proxy reicht `/api` + `/health` an Django
  (`127.0.0.1:8000`) weiter (verifiziert: `/health/` 200, `POST /api/spiele/` 201).
  Lokal ansehen: Django (`.venv`) + `npm run dev` → http://localhost:5173/.
- **CI:** neue Jobs `frontend` (npm ci → build inkl. vue-tsc → Vitest) und
  `frontend-e2e` (Chromium + Playwright-Smoke); `actions/setup-node` SHA-gepinnt.
  Die gesamte CI **gatet** den Deploy → Frontend muss grün sein.
- **Doku-Sync:** ADR-013 (Teststrategie), `development-approach-v1.md` §Phase 2
  (Frontend-Zyklus), `glossar.md` (gaten, Testpyramide, playwright-bdd, Dev-Proxy),
  `project-foundation.md` §18/§20.
- **Offen:** Live-Cut-Over (s. u.) unverändert; nichts committet/gepusht.
- **Nächster Schritt:** TASK-008 (Spiel anlegen – UI, Slice 1).

## Stand 23.07.2026 (Phase 2 Frontend gestartet — Same-Origin-Infrastruktur, Coding)

**Phase 2 (Frontend, Vue) ist gestartet.** Erste Teilaufgabe **TASK-007a** (Phase-0-
Infrastruktur) ist umgesetzt: Die Deploy-Konfiguration liefert jetzt SPA **und** API
**Same-Origin** auf einer Domain aus.

- **Entscheidungen (Repo-Eigentümer, aus Plan-Session):** (1) Playwright + playwright-bdd;
  (2) Frontend `binokel.bebe-soft.de`, gleiche VM, Same-Origin (Nginx serviert SPA +
  proxied `/api/`), `api.bebe-soft.de` → 301 auf Primärdomain; (3) Tailwind CSS;
  (4) handgeschriebenes OpenAPI 3.1 jetzt (Auto-Schema = FUTURE-002).
  **Stack:** Vue 3.5 + Vite + TS + Vue Router + Pinia + Vitest; PWA + Capacitor-ready; mobil-first.
- **Umgesetzt (B1–B3):**
  - `deploy/nginx.conf.template`: SPA-Root `/opt/binokel/frontend`, `try_files`-Fallback
    (History-Mode), `/api/`- + `/health/`-Proxy, `/assets/`-Immutable-Cache, `index.html`
    `no-cache`; zweiter 443-Serverblock 301 (API-Domain → Primärdomain); gemeinsames
    SAN-Zertifikat (Lineage der Primärdomain).
  - `deploy/setup-server.sh`: `/opt/binokel/frontend` + `www-data`-rX-ACL (+Default-ACL);
    optionale `API_DOMAIN` (Arg 3) → SAN-Cert (`-d PRIMÄR -d API`) + Zwei-Domain-
    Substitution; Ein-Domain-Modus entfernt Redirect-Block (Sentinel-Marker) + Rest-
    Platzhalter. `bash -n` OK; beide Render-Modi verifiziert.
- **Doku-Sync (PFLICHT-KONVENTION):** ADR-010 (Same-Origin-Deployment), ADR-011
  (Vue-Stack + Playwright + Teststrategie-Leitplanke), ENG-005 (Frontend-Fallstricke),
  `project-foundation.md` §20 (Fragen 5–8 beantwortet), BACKLOG (TASK-007a ✅ + 007–011
  präzisiert).
- **Teststrategie-Leitplanke (WICHTIG, Wunsch des Repo-Eigentümers):** fachliche Abdeckung
  bleibt schwerpunktmäßig auf der API-Ebene (18 Django + 28 Behave); E2E (Playwright)
  bewusst schlank (kritische Journeys/Smoke). **Vor** breitem Ausbau der playwright-bdd-
  Szenarien final abstimmen.
- **Offen (Live-Cut-Over, USER/Betreiber):** DNS `binokel.bebe-soft.de`; einmalige
  Cert-Migration auf gemeinsame SAN-Lineage (api-Domain ist bereits eigene Lineage);
  `cd.yml`-Smoke-Test auf Primärdomain umstellen; `DJANGO_ALLOWED_HOSTS` /
  `DJANGO_CSRF_TRUSTED_ORIGINS` beide Domains.
- **Git:** 2 ältere lokale Doku-Commits (`1a20e55`, `27a9dd1`) noch nicht auf `origin/main`.
- **Nächster Schritt:** TASK-007 — Vite-Scaffold `frontend/`, API-Client + OpenAPI 3.1,
  Tailwind/Router/Pinia, Vitest + Playwright-Grundgerüst.

## Stand 22.07.2026 (TASK-CI-006 ABGESCHLOSSEN — Prod-Deploy live + Smoke-Test automatisiert, Dev/Ops)

**Der erste reale Produktions-Deploy ist erfolgreich.** Die App läuft prod auf
**`https://api.bebe-soft.de`** (echtes Let's-Encrypt-Cert). CD-Läufe **#30/#31 GREEN**
(letzter Commit `e8cd217`, CI-Run 29944409695 + CD-Run 29944433636 alle Checks grün).
Live-Smoke-Test verifiziert: `/health/`=200, `/admin/`=404 (RD-6), HTTP→HTTPS-Redirect=301,
HSTS-Header vorhanden.

**Neu automatisiert (FUTURE-004-Teil):** Post-Deploy-**Smoke-Test-Step in `cd.yml`**
(„Smoke-Test (öffentliches HTTPS-Deployment)", nach dem Healthcheck). Prüft vom Runner via
`curl` end-to-end über öffentliches HTTPS die vier o. g. Zusicherungen; schlägt eine fehl →
Deploy rot. Redirect-Check läuft gegen `/` (nicht `/health/`, da dieses redirect-exempt ist).

**CD-Host-Key-Fallstrick (behoben):** `VM_SSH_KNOWN_HOSTS` muss gegen den **exakten
`VM_HOST`-String** (`api.bebe-soft.de`, nicht die IP) gescannt werden:
`ssh-keyscan -t rsa,ecdsa,ed25519 api.bebe-soft.de` **lokal** ausführen. Der
`ssh-keygen -lf`-Fingerprint dient nur der menschlichen Verifikation, ist **nie** der
Variablen-Inhalt. Falscher Inhalt → `exit 255 / Host key verification failed`.

**Klassifikation Secrets vs. Variables (best-practice, Rubber-Duck-CD-Review GO):**
`VM_SSH_KEY` = Environment **Secret**; `VM_HOST`, `VM_USER`, `VM_SSH_KNOWN_HOSTS` =
Environment **Variables** (Integritäts-, kein Vertraulichkeitsziel). Third-Party- + checkout-
Actions auf Full-Commit-SHA gepinnt (`cd.yml` + `ci.yml`).

**Offen → jetzt als `FUTURE-006` gesichert (Go-Live-Governance/Ops-Nacharbeiten):**
- **Reviewer-Gate erzwingen** (USER, GitHub-UI): Settings → Environments → `production` →
  Required reviewers. Aktuell **nicht** aktiv (Deploy lief ohne Approval-Dialog).
- **Branch Protection `main`** (Phase 5, USER): beide Checks „BDD Akzeptanztests" +
  „Deploy-Skripte prüfen (shellcheck + bash -n)" als Required.
- **IONOS-Ports 8000/8443/8447 schließen** (Blocker #9, USER/Betreiber).
- **Backup-/Restore-Probe automatisieren** (Runbook 6.2 → FUTURE-004-Offenpunkt): SSH-Step +
  `sqlite3 integrity_check` auf zerstörungsfreier Kopie.

Detaillierte Deploy-Historie (Phasen 0–6, alle Blocker) siehe folgende Abschnitte.

---

## Stand 22.07.2026 (TASK-CI-006 — realer Prod-Deploy Phase 0/1 + IONOS-Security-Review, Dev/Ops)

**Realer Produktions-Deploy gestartet** (Agent ohne SSH-Zugang → User führt VM-Kommandos,
paste-sichere Blöcke). Zieldomain **`api.bebe-soft.de`** → `212.132.119.150`, Ubuntu 24.04.

- **Phase 0 (DNS + Admin-Key) ✅** — A-Record verifiziert (beide Resolver, kein AAAA);
  Admin-Key `~/.ssh/binokel_admin` erzeugt.
- **Phase 1 (Erst-Login + sshd-Hardening) ✅ + lockout-sicher verifiziert** — `binokel-admin`
  angelegt (sudo-Gruppe), Key-Login OK, Passwort- + Root-Login abgewiesen.
  **Fallstrick (neu, ENG-004):** cloud-init legt `/etc/ssh/sshd_config.d/50-cloud-init.conf`
  mit `PasswordAuthentication yes` an → überstimmt eine `99-`-Drop-in (sshd „first match wins").
  **Fix:** Hardening als **`00-binokel-hardening.conf`** + Effektivwert-Prüfung via `sshd -T`.
  Runbook Phase 1.3/1.4 korrigiert (realer Login/sudo-Check statt `sudo -n`).

**IONOS-Security-Review (Best-Practice-PDFs → Compliance-Matrix → Rubber-Duck-Audit).**
Matrix: `docs/security/ionos-baseline-check.md` (paraphrasiert; PDFs bleiben lokal/uncommitted).
Ablauf als wiederverwendbares Muster: `pdftotext` → paraphrasierte Matrix (committbar) →
Rubber-Duck-Audit → Dev/Ops-Remediationsplan. Audit-Votum initial **NO-GO** bis Blocker behoben.

**Umgesetztes Go-Live-Gate (Rubber-Duck: GO, nur NIEDRIG-Restpunkte):**
- **#4/#20** SQLite-Backup: `cp` → **`sqlite3 .backup`** + `PRAGMA integrity_check` + atomarer
  `mv` + journald-Logging in neuem `/usr/local/bin/binokel-backup.sh`; cron.d ruft nur noch das
  Skript + separate Retention. Stale-`.tmp`-Cleanup ergänzt. (`deploy/setup-server.sh`)
- **RD-6** `/admin/`-Route in V1 **deaktiviert** (kein Superuser nötig; Reaktivierung nur mit
  Nginx-IP-Allowlist). (`backend/binokel_tracker/urls.py`)
- **RD-8** HSTS `preload` + `includeSubDomains` = **`False`** (host-scoped, reversibel; erst
  nach stabilem TLS scharf schalten). (`backend/binokel_tracker/settings.py`)
- **Restore-Probe** als Runbook-Schritt **6.2** (zerstörungsfrei, Go-Live-Gate).
- Tests GREEN (28 Behave + 19 Django); `bash -n setup-server.sh` OK.

**RD-7** (`@csrf_exempt` auf POST-Views) bewusst akzeptiert/dokumentiert (token-lose JSON-API,
V1 ohne Auth). **Fast-Follow → FUTURE-003:** Offsite-DR (scp-Pull) + IONOS-VM-Snapshot +
periodische Restore-Übung (Backups liegen auf gleicher Platte — in ADR-008/009 akzeptiert).

**Offener Go-Live-Blocker (Betreiber-Aktion):** IONOS-Cloud-Panel-Ports **8000/8443/8447
schließen** (nur 22/80/443).

**Nächste Schritte:** Doc-Änderungen committen (Push-Timing wg. CD beachten — „lokal patchen":
VM erhält gepatchtes `setup-server.sh` per scp, nicht via `curl` aus main) → **Phase 2**
(`setup-server.sh api.bebe-soft.de <repo>`, ohne `CERTBOT_STAGING`) → Phasen 3–6.

---

## Stand 22.07.2026 (TASK-CI-006 — Trockenlauf erfolgreich + Security-Hardening, Dev/Ops)

**Trockenlauf abgeschlossen (GRÜN).** Der komplette Deploy-Pfad wurde real gegen eine
Wegwerf-VM (`staging.bebe-soft.de`, Certbot `--staging`) durchgespielt: `HTTP→HTTPS 301`,
`health-https 200`, sauberes `error.log`, korrekte migrate-/collectstatic-Pfade. Dabei traten
**sechs** weitere reale Blocker auf (gunicorn-Dependency fehlte, Deploy ohne Prod-env → falsche
DB-/Static-Pfade, `/etc/binokel`-Verzeichnis-Traversal, uv-Interpreter im Deploy-Home →
`203/EXEC`, Gunicorn-Control-Server ohne `HOME`, Nginx-Host-Header im 443-`/health/`-Block) —
alle behoben. Commits: `5d6c5e3`, `991c493`, `f486ade`, `c37dc30`, `bbd07e3`, `ded2e13`.

**Security-Review des Rechte-/Zugriffsmodells (Rubber-Duck).** Zwei prod-blockierende Punkte
(K1, K2) + fünf Nachschärfungen (E1–E5), alle umgesetzt; Tests GREEN (28 Behave + 19 Django).

- **K1** – sudoers-Regel `systemctl status` **entfernt** (Pager-Root-Escape via `!sh` aus
  `less`). NOPASSWD nur noch `restart`/`stop`; Statusdiagnose läuft unprivilegiert.
  (`deploy/setup-server.sh`, `.github/workflows/cd.yml`)
- **K2** – fail-open `SECRET_KEY` behoben: bei `DEBUG=False` **harter Abbruch**
  (`ImproperlyConfigured`), wenn der Insecure-Default-Key aktiv ist. `DEBUG`-Default bleibt
  `True` (Test-/Behave-Läufe ohne env). (`backend/binokel_tracker/settings.py`)
- **E1** – `STATIC_DIR` gehört `binokel-deploy`; der exponierte Dienst `binokel-app` hat nur
  noch `rX` (kann ausgeliefertes Static nicht überschreiben). (`deploy/setup-server.sh`)
- **E2** – Security-Header-Ownership entwirrt: Django für proxied Antworten, Nginx exklusiv im
  `/static/`-Block; `Referrer-Policy` vereinheitlicht. (`settings.py`, `nginx.conf.template`)
- **E3** – systemd-Härtung ausgebaut (`ProtectSystem=strict` + `ReadWritePaths`, `ProtectHome`,
  `PrivateDevices`, `SystemCallFilter=@system-service`, `RestrictAddressFamilies` …).
  (`deploy/binokel-tracker.service`)
- **E4** – `server_tokens off;`. (`nginx.conf.template`)
- **E5** – CD liest den echten `SECRET_KEY` nicht mehr: migrate/collectstatic laufen mit einem
  Wegwerf-Schlüssel; nur nicht-geheime Pfad-Variablen werden aus der env gelesen.
  (`.github/workflows/cd.yml`)

**Doku:** ADR-009 (zwei Nachträge: Privilegienmodell „warum root nur fürs Provisioning" +
K1–E5-Zusammenfassung); `ENG-004` (K1/K2-Fallstricke + E1–E5-Abschnitt); `BACKLOG.md`;
`deploy/runbook-task-ci-006.md` (Phase-4-Verifikation an K1 angepasst; env-Perms `640 root:binokel-app`
→ `600 root:root + ACL`).

**Nächste Schritte:** Teardown Wegwerf-VM + Test-DNS entfernen; **realer Produktions-Deploy**
nach Runbook (reale Domain, **ohne** `CERTBOT_STAGING`, IONOS-Ports 8000/8443/8447 schließen).
Danach Phase 2 Frontend (Vue).

---

## Stand 21.07.2026 (TASK-CI-006 — Rubber-Duck-Review + Blocker-Fixes, Dev/Ops)

Der Rubber-Duck-Review der Hardening-/Deploy-Planung ist erfolgt. Ergebnis-Votum war
zunächst **NO-GO**: Die Hardening-Baseline (ADR-009) ist solide, aber der ausführbare
Pfad enthielt 5 Blocker. Diese wurden behoben (Code + Doku), Tests bleiben GREEN
(28 Behave + 19 Django).

**Behobene Blocker:**
- `backend/binokel_tracker/settings.py` — `SECURE_PROXY_SSL_HEADER` + `SECURE_REDIRECT_EXEMPT`
  für `/health/`; `localhost`/`127.0.0.1` immer in `ALLOWED_HOSTS` (Redirect-Loop + Healthcheck).
- `deploy/setup-server.sh` — Nginx/Certbot Henne-Ei gelöst (HTTP-only-Bootstrap → Certbot →
  volles Template); `uv`-Pfad-Fallback (`~/.local/bin`); POSIX-ACLs für gemeinsamen
  Schreibzugriff (`binokel-app` + `binokel-deploy`) auf `data`/`static`; sudoers auf
  `/usr/bin/systemctl`; tägliches SQLite-Backup via `cron.d`; `acl`-Paket ergänzt.
- `deploy/nginx.conf.template` — `location = /health/` im Port-80-Block (HTTP-Healthcheck
  ohne Redirect).
- `.github/workflows/cd.yml` — `VM_SSH_KNOWN_HOSTS` jetzt **Pflicht** (kein
  Laufzeit-`ssh-keyscan`-Fallback mehr; MITM-Schutz).

**Entscheidung:** Betriebssystem-Basis bleibt **Ubuntu 24.04 LTS** (ADR-008 erweitert).

**Neu/aktualisiert:** `docs/engineering-notes/ENG-004-deployment-hardening-fallstricke.md`;
ADR-008 (OS-Basis), ADR-009 (Nachtrag Review); Runbook + `deploy/README.md` angeglichen;
`BACKLOG.md`.

**Nächste Schritte:** Trockenlauf gegen Wegwerf-VM mit Certbot `--staging`, danach realer
Deploy nach Runbook.

---

## Stand 19.07.2026 (TASK-CI-006 geplant — Dev/Ops)

### Erledigt (reine Planung/Dokumentation, KEINE Ausführung auf realer VM)

Für den ersten Produktions-Deploy wurde ein vollständiges Runbook erstellt. Es wurden
**keine** SSH-Verbindungen aufgebaut, **keine** echten Secrets erzeugt und **kein**
Deploy ausgelöst.

- `deploy/runbook-task-ci-006.md` — **neu**: Schritt-für-Schritt-Runbook (Phasen 0–6)
  mit Verifikation + Rollback je Phase, Betriebsrisiken-Tabelle, V2-Migrationsausblick
  (Docker + PostgreSQL) und Rubber-Duck-Review-Punkten.
- `docs/adr/ADR-009-internet-hardening-baseline.md` — **neu**: Internet-Hardening-
  Baseline der VM (SSH-Key-only, sshd-Hardening, UFW, fail2ban, unattended-upgrades,
  chrony, TLS). Ergänzt ADR-008 (deckt SQLite-für-V1 + Docker/PostgreSQL-Pfad ab).
- `deploy/setup-server.sh` — **geändert**: idempotent um `fail2ban`,
  `unattended-upgrades` und `chrony` ergänzt (Schritt 10/10). sshd-Hardening bleibt
  bewusst manuell (Lockout-Risiko, ADR-009).
- `deploy/README.md` — **geändert**: Hardening-Abschnitt + Verweis auf das Runbook.
- `BACKLOG.md` — TASK-CI-006 präzisiert (Status: geplant), ADR-009 ergänzt.

**Nebenbefund:** In diesem Dokument standen unaufgelöste Merge-Konflikt-Marker
(`<<<<<<<`/`>>>>>>>`) im Abschnitt „Engineering-Dokumente" — beim Update bereinigt
(deconflictete `docs/agents/*`-Variante übernommen).

### Nächste Schritte (Dev/Ops)

1. **Rubber-Duck-Review** der Härtungsentscheidungen (Punkte am Ende des Runbooks).
2. **TASK-CI-006 ausführen** auf realer 1&1/IONOS-VM (benötigt Zugangsdaten, Domain,
   DNS). Ablauf strikt nach `deploy/runbook-task-ci-006.md`.

---

## Stand 26.06.2026

### Abgeschlossen
Die Gherkin-Arbeit an den Feature-Dateien ist abgeschlossen.

Alle sechs Feature-Dateien unter `features/` enthalten konkrete Szenarien:
- `spiel_anlegen.feature`
- `runde_normales_spiel.feature`
- `runde_einfaches_abgehen_auswerten.feature`
- `runde_deoppeltes_abgehen.feature`
- `runde_tausender.feature`
- `spielende_und_siegerermittlung.feature`

Zusätzlich wurde `docs/gherkin-step-phrase-reference-v1.md` angelegt.
Sie enthält alle kanonischen Step-Phrasen als Referenz für die spätere Testautomation.

### Wichtige Sprachregeln für Gherkin
- Rundenausgang wird ausschließlich über Zielerreichung des Spielmachers bestimmt.
- Stich-Zwang ist eine Zählregel für Meldepunkte, keine Gewinnbedingung.
- Gegenspieler können fachlich nicht verlieren; sie sammeln nur Punkte.
- Terminologie: "geht ab", nicht "gibt ab".
- Doppeltes Abgehen: Runde wird regulär vollständig ausgespielt.
- Kein Szenario "Spielmacher mit 0 Stichen" in normaler Runde (würde in der Praxis zum einfachen Abgehen führen).

### Offene Todos (Stand 26.06.2026 — inzwischen abgeschlossen, siehe Stand 28.06.2026)

1. ~~Fehlende Szenarien prüfen~~ → erledigt
2. ~~Projektstruktur aufsetzen~~ → noch offen
3. ~~Step-Definitionen schreiben~~ → noch offen
4. ~~Domänenlogik implementieren~~ → noch offen

---

## Stand 19.07.2026 (CI/CD)

### Abgeschlossen

**CI/CD-Pipeline + Dev/Ops-Fundament:**
- `backend/binokel_tracker/settings.py` — produktionsreife Konfiguration via Env-Vars (12-Factor)
  - `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_DB_PATH`,
    `DJANGO_STATIC_ROOT`, `DJANGO_CSRF_TRUSTED_ORIGINS`
  - Automatische HSTS/Secure-Cookie-Aktivierung bei `DEBUG=False`
- `backend/binokel_tracker/urls.py` — `/health/`-Endpunkt für Deployment-Healthchecks
- `.github/workflows/ci.yml` — CI: Django-Check + BDD-Szenarien bei jedem Push/PR
- `.github/workflows/cd.yml` — CD: rsync auf 1&1-VM, Migrationen, Neustart, Healthcheck, Rollback
- `deploy/binokel-tracker.service` — systemd-Unit (Gunicorn)
- `deploy/nginx.conf.template` — Nginx Reverse Proxy mit TLS
- `deploy/setup-server.sh` — einmaliges Server-Initialsetup
- `deploy/README.md` — vollständiges Betriebsrunbook
- `docs/agents/coding-agent.md` — Rollenbeschreibung Coding-Agent
- `docs/agents/rubber-duck-agent.md` — Rollenbeschreibung Rubber-Duck-Agent
- `docs/agents/devops-agent.md` — Rollenbeschreibung Dev/Ops-Agent
- `docs/agents/orchestration.md` — Orchestrierungs-Workflow der 3 Agenten
- `docs/adr/ADR-007-github-actions-ci-cd.md`
- `docs/adr/ADR-008-vm-deployment-strategie.md`
- 28/28 Behave-Szenarien weiterhin GREEN

### Nächste Schritte (Priorität)

1. **TASK-CI-006** VM einrichten und ersten Produktions-Deploy durchführen
   - Benötigt: Zugangsdaten zur 1&1-VM, Domain, GitHub-Secrets
   - Schritte: `deploy/README.md`
2. Weitere Priorisierung siehe `BACKLOG.md` im Repo-Root

---

## Stand 19.07.2026

### Abgeschlossen

**TASK-006: Behave HTTP-Blackbox-Infrastruktur + Slice-1-Migration (19.07.2026):**
- `features/environment.py` — vollständig neu: `setup_databases()` + Migrationen in `before_all`, `context.client` (Django TestClient) in `before_scenario`, `SpielModel.objects.all().delete()` in `after_scenario` (Cascade)
- `features/steps/spiel_anlegen_steps.py` — Slice 1 vollständig auf HTTP migriert: POST /api/spiele/ statt `spiel_anlegen()`, HTTP-400-Checks statt Exception-Fang, `Spiel`-Domänenobjekt aus API-Antwort rekonstruiert (für `geber_in_runde`)
- Slices 2–5: Domain-Steps bleiben bewusst erhalten (testen interne Berechnungsregeln, Stich-Zwang, 250er-Kontrollsumme — nicht über HTTP-Response sichtbar)
- Slice 6: Domain-Steps bleiben (Punktestände werden direkt als Dict gesetzt; kein passender API-Endpunkt)
- 28/28 Behave GREEN, 18/18 Django GREEN

### Nächste Schritte (Priorität)

Alle definierten TASKs abgeschlossen. Keine offenen priorisierten Aufgaben.

→ Vollständiger Backlog: `BACKLOG.md` im Repo-Root

---

## Stand 19.07.2026 (TASK-005)
- `backend/scoring/tests.py` — 18 API-Integrationstests (Django TestCase + TestClient)
  - `SpielAnlegenApiTest` (6 Tests): POST /api/spiele/, GET /api/spiele/{id}/, Fehlerbehandlung
  - `RundeAuswertenApiTest` (8 Tests): alle 5 Rundentypen, Pflichtfeld- und Typ-Validierung
  - `PunktestaendeUndSiegerApiTest` (4 Tests): Punktestände, Sieger, Tiebreaking, 404
- 18/18 Django-Tests GREEN, 28/28 Behave-Szenarien weiterhin GREEN
- Normative Quelle: ADR-006

### Nächste Schritte (Priorität)

1. **TASK-006** Behave-Steps schrittweise auf HTTP umstellen (ADR-006, Slice für Slice)
   - Slice 1: `spiel_anlegen.feature` + `spiel_anlegen_steps.py`
   - Dann Slices 2–6 analog

→ Vollständiger Backlog: `BACKLOG.md` im Repo-Root

---

## Stand 18.07.2026

### Abgeschlossen

**Domänenlogik vollständig — 28/28 Szenarien GREEN (02.07.2026):**
- `backend/scoring/domain.py` — `Spiel` (dataclass), `Rundenausgang` (Enum), Fehlerklassen
- `backend/scoring/use_cases.py` — alle Use Cases für Slices 1–6 implementiert
- `features/steps/` — alle 7 Step-Dateien vollständig implementiert
- `features/environment.py` — Django-Integration (setup_test_environment in before_all)
- `docs/engineering-notes/ENG-001`, `ENG-002` — Implementierungs-Fallstricke dokumentiert

**Persistenzschicht + Workflow-Dokumentation (18.07.2026):**
- `docs/datenmodell-v1.puml` — PlantUML-Klassendiagramm repariert und bereinigt
- `BACKLOG.md` — neues zentrales Steuerungsdokument für Session-Kontinuität angelegt
- `docs/project-foundation.md` §18 — BACKLOG.md und 3-Quellen-Workflow dokumentiert
- `docs/development-approach-v1.md` §8 — neuer Abschnitt „Session-Kontinuität und Backlog-Workflow“
- `backend/scoring/models.py` — 4 Django ORM-Modelle implementiert
  (SpielModel, SpielerModel, RundeModel, GegenspielerRundeModel)
- `backend/scoring/migrations/0001_initial.py` — erzeugt und angewendet
- 28/28 Behave-Szenarien weiterhin GREEN

### Nächste Schritte (Priorität)

1. **TASK-005** API-Integrationstests in `scoring/tests.py` (TestCase + TestClient)
2. **TASK-006** Behave-Steps schrittweise auf HTTP umstellen (ADR-006, Slice für Slice)

→ Vollständiger Backlog: `BACKLOG.md` im Repo-Root

---

## Stand 28.06.2026

### Abgeschlossen

**Gherkin-Nacharbeiten:**
Drei fehlende Szenarien in `features/` ergänzt:
- `spiel_anlegen.feature`: Geberrotation streng reihum
- `runde_normales_spiel.feature`: Validierungsfehler wenn Stichwert-Summe > 250
- `runde_einfaches_abgehen_auswerten.feature` + `runde_deoppeltes_abgehen.feature`: Verlustwert-Darstellung `(-250)` / `(-400)`

Neue Step-Phrasen in `docs/gherkin-step-phrase-reference-v1.md` (Geberrotation, Stichwert-Validierung, Verlustwert-Darstellung).

**Engineering-Dokumentation:**
- `docs/development-approach-v1.md` erstellt: Outside-In, RED-Green-Refactor, Vertikale Slices, Phasenmodell mit ausführlichen Begründungen
- `docs/adr/` angelegt: ADR-001, ADR-002, ADR-003
- `docs/project-foundation.md` §10 (BDD-Entwicklungszyklus) und §18 (Dokumentationsset) aktualisiert

### Offene Todos (nächster Schritt)

1. **Projektstruktur aufsetzen** (technisch)
   - Python-Projektstruktur und `behave` + `behave-django` einrichten
   - Django-Grundgerüst anlegen
   - Step-Stub-Dateien aus `docs/gherkin-step-phrase-reference-v1.md` generieren → `behave` ausführen → alles RED
   - Feature-Reihenfolge: laut `docs/development-approach-v1.md` §5

2. **Step-Definitionen schreiben**
   - Auf Basis von `docs/gherkin-step-phrase-reference-v1.md`
   - Zunächst ohne Domänenlogik (pending)

3. **Domänenlogik implementieren**
   - Feature für Feature als vertikale Slice
   - Normative Quelle: `docs/rule-set-v1.md`
