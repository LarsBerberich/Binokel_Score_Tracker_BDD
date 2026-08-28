# Exploratives Testprotokoll — Binokel Score Tracker

Findings aus manuellen/explorativen Test-Sessions (Tester-Agent). Format je Eintrag:
ID, Datum, Modus, Bereich, Repro-Schritte, Erwartet (Regelbezug), Ist, Schwere, Repro-Test.
Umsetzbare Defekte werden zusätzlich in `BACKLOG.md` gespiegelt und zur Behebung an den Coding-Agenten übergeben.

---

## FND-001 — Auto-Stichwert-Feld bleibt read-only nach Löschen eines manuellen Stichwerts

- **Status:** ✅ BEHOBEN (2026-08-17, TASK-015) — Fix in `RundeForm.vue` (Spieler beim Leeren aus `stichwertReihenfolge` entfernt); Vitest-Repro grün.
- **Datum:** 2026-08-17
- **Modus:** Pairing
- **Bereich:** Rundenerfassung, normales Spiel — Auto-Berechnung 3. Stichwert (`RundeForm.vue`, §8.2 / TASK-012.5, offener Punkt S2)
- **Schwere:** MITTEL (blockiert das Korrigieren einer Fehleingabe innerhalb der Runde; kein Reset-Weg vorhanden)
- **Repro-Test:** noch keiner (Vitest-Repro empfohlen)

**Repro-Schritte:**
1. Neues Spiel, normale Runde. Drei aktive Spieler (Spielmacher + 2 Gegenspieler).
2. Stichwert für Spieler A eintragen, dann Stichwert für Spieler B eintragen → Spieler C wird automatisch berechnet und **read-only** (korrekt).
3. Feststellen, dass B der falsche Mitspieler war → das Stichwert-Feld von B **leeren** (löschen).

**Erwartet (Regelbezug §8.2):**
Nach dem Löschen von B gibt es nur noch **einen** manuell erfassten Stichwert (A). Damit steht der dritte Wert nicht mehr fest → das read-only auf C sollte **aufgehoben** werden, damit man den Wert dem richtigen Spieler zuordnen kann.

**Ist:**
Das read-only auf C bleibt bestehen. Da B geleert (0) und C gesperrt ist, lässt sich die Fehleingabe nicht mehr korrigieren.

**Ursache (Codeanalyse):**
`stichwertErfasst(name)` (in `RundeForm.vue`) wird bei **jedem** `@input` aufgerufen — auch beim Leeren eines Feldes. Der geleerte Spieler bleibt dadurch in `stichwertReihenfolge` als „manuell erfasst" registriert, sodass weiterhin zwei manuelle Werte gelten und `autoStichwertSpieler` unverändert read-only bleibt.

**Vorschlag (Fix beim Coding-Agenten):**
Beim Leeren eines Stichwert-Feldes den Spieler aus `stichwertReihenfolge` entfernen (statt ihn nach vorn zu holen), sodass das dritte Feld wieder frei editierbar wird. Alternativ/zusätzlich ein „Stichwerte zurücksetzen"-Button (S2). Vitest-Repro: A und B setzen → C read-only; B leeren → C wieder editierbar.

---

## FND-002 — Kumulierter Punktestand zeigt Einerstellen (Rundung auf Zehner fehlt)

- **Status:** ✅ BEHOBEN (2026-08-17, TASK-016, Option 1 + 2b) — Zehner-Eingabe (step=10) + modulo-10-Validierung (Frontend + Backend-Guard); STAND immer Zehner; Endrunden-1er nur für §9.3-Tiebreak. Verifiziert: Suiten grün (30 Django/29 Behave/44 Vitest) + Live-curl (99/91/60→400, Stand nur Zehner).
- **Datum:** 2026-08-17
- **Modus:** Pairing
- **Bereich:** Punktestand-/Standberechnung (`repositories.py::punktestaende_laden`); Regel-Präzisierung `rule-set §9` / Anschreibetabelle §5
- **Schwere:** HOCH (verletzt die Anschreibe-Kernregel „STAND immer auf Zehner"; betrifft Zwischen- und Endstand)
- **Repro-Test:** noch keiner (Django-Repro empfohlen)

**Repro-Schritte:**
1. Normale Runde mit 1er-genauem Stichwert erfassen (z. B. ein Gegenspieler mit **99** statt 100).
2. Punktestand ansehen.

**Erwartet (Regelbezug — USER-Präzisierung 2026-08-17):**
Die 1er-genaue Erfassung dient nur dem exakten Auszählen knapper Spiele bzw. dem Gleichstand-Tiebreak in der letzten Runde (§9.3). Im **summierten Zwischen- und Endstand** wird immer nur der **sauber auf Zehner gerundete** Punktestand aufaddiert. Der STAND darf keine Einerstellen zeigen (vgl. Anschreibetabelle §5, alle STAND-Werte auf Zehner).

**Ist:**
`punktestaende_laden` summiert die Stichwerte exakt (1er-genau) → der angezeigte Stand hat Einerstellen (Beispiel: 189 statt 190).

**Konkreter Beleg (Endstand, Pairing 2026-08-17):** Endstand zeigte `Bernd 260, Dirk 239 ★, Carla 230 ★, Anna −550 ★` — der Wert **Dirk 239** endet auf 9, betrifft also auch den **Endstand** (`SpielendeView`), nicht nur den laufenden Punktestand. Sieger/Sortierung/Sterne (§15) waren dabei korrekt.

**Ursache (Codeanalyse):**
`repositories.py::punktestaende_laden` addiert `gs.stichwerte` (und für den Spielmacher analog) ungerundet. Es gibt keine Zehner-Rundung beim Aggregieren.

**Offene Regel-Entscheidung (eskaliert an USER, siehe Rückfrage):**
1. Rundungsmethode (kaufmännisch nächste Zehner / immer abrunden / immer aufrunden)?
2. Was wird gerundet — nur der Stichwert S je Spieler und Runde (M und Mit sind bereits Zehner)?
3. Exakte 1er-Werte bleiben **gespeichert** (für §9.3-Tiebreak); nur Anzeige/Aggregation rundet — bestätigen?

**USER-Entscheidung (2026-08-17):**
1. **Kaufmännisch** auf nächste Zehner (`.5` auf, also 99→100, 94→90, 95→100).
2. Gerundet wird der **Stichwert S je Spieler und Runde** (M und Mit sind bereits Zehner). **Pro Runde runden, dann aufaddieren** (jede Rundenzeile auf Zehner, analog Anschreibetabelle §5).
3. **Ja** — Rohdaten bleiben 1er-genau gespeichert; nur der kumulierte STAND rundet. Der Gleichstand-Tiebreak (§9.3) nutzt weiterhin die exakten Werte.

**Randfall für Rubber-Duck-Review (vor Umsetzung):**
Unabhängiges kaufmännisches Runden der drei Stichwerte je Runde kann die 250-Kontrollsumme verletzen (z. B. 95+95+60 → 100+100+60 = 260). Das betrifft nur die gerundeten STAND-Beiträge (die exakte Erfassung bleibt bei 250). Klären, ob das akzeptiert wird oder eine Ausgleichsregel nötig ist.

**Vorschlag (Fix beim Coding-Agenten, nach Rubber-Duck-Review):**
`punktestaende_laden` rundet den Stichwert-Anteil je Spieler/Runde kaufmännisch auf Zehner; Rohdaten bleiben 1er-genau; Tiebreak nutzt weiterhin exakte Werte. `rule-set §9` um Aggregations-/STAND-Rundung (§9.4 neu) ergänzen; Django-Repro + Anpassung bestehender Punktestand-Tests; OpenAPI-Beispiele prüfen. **PFLICHT-KONVENTION:** Regeländerung → rule-set + ubiquitous-language + Handover.

**Rubber-Duck-Review-Ergebnis (2026-08-17): CONDITIONAL GO** — Fachplan bestätigt, Umsetzung nachgeschärft:
- 🔴 **HOCH-1:** `sieger_ermitteln` MUSS weiter auf dem **exakten** Kumulativstand rechnen (§9.3), sonst Regression (234 vs. 232 → beide 230 → künstlicher Gleichstand). Nur die **Anzeige** rundet. `sieger_view`: exakt → `sieger_ermitteln`; gerundet → `punktestaende`-Response.
- 🔴 **HOCH-2:** „Pro Runde runden" ist aus dem exakten Endstand NICHT ableitbar (`round(∑S) ≠ ∑round(S)`). → **Neue** Funktion `punktestaende_gerundet_laden` (rundet je Runde/Spieler, summiert dann); `punktestaende_laden` bleibt **unverändert exakt**.
- 🟡 **MITTEL-1:** Half-up explizit als `((wert + 5) // 10) * 10` (nicht `round()` → Banker's Rounding 85→80). Nur auf S-tragende Beiträge; `verlustwert`-Zweig unberührt.
- 🟡 **MITTEL-2:** 250-Divergenz **akzeptiert** (unabhängige Konten); in §9.4 explizit als gewollt dokumentieren (kein späteres „Reparieren").
- 🟢 TASK-014 keine Vorbedingung (M ≡ 0 mod 10 → `round₁₀(M+S)=M+round₁₀(S)`); bestehende Tests bleiben grün; optional kurzes ADR (Sieger-auf-exakt + akzeptierte 250-Divergenz).
- 🟢 **Residualrisiko (NIEDRIG):** Endstand kann gerundet 230/230 zeigen, Banner aber Einzelsieger (exakt 234>232) — regelkonform (§9.3), optisch erklärungsbedürftig; für V1 akzeptiert.
- **Pflicht-Tests:** (a) S=99 → STAND 100; (b) 95+95+60 → STAND-Summe 260 dokumentiert; (c) 234 vs. 232 → Anzeige 230/230 aber `sieger`=Einzelsieger; (d) 85→90 half-up-Guard.

**USER-KORREKTUR (2026-08-17) — ÜBERSTEUERT die akzeptierte 250-Divergenz (MITTEL-2):**
Die 250 muss **auch im Rundungsfall exakt eingehalten** werden — keine 260-Summe. Nach gemeinsamer Erarbeitung
gewählt: **Option 1 — Zehner-Rundung an der EINGABE** (nicht bei der Aggregation).
- Die 250-Kontrollsumme prüft künftig die **auf Zehner gerundeten** Stichwerte (Summe der gerundeten Werte = 250);
  ersetzt die bisherige Prüfung auf exakt 250 der Rohwerte. Absenden gesperrt, solange gerundete Summe ≠ 250.
- **Grenzfälle löst der Mensch bei der Eingabe** auf (z. B. real 95/95/60 → gerundet 260 → Nutzer gibt 100/90/60 ein).
  Damit entfällt die Größte-Rest-Methode und die Tie-Break-Regel bei der Aggregation.
- **Verlust-Runden:** USER-Entscheidung = **Spielmacher-Stich zusätzlich speichern** (Schema-Änderung/Migration),
  damit alle Runden gleich behandelt werden und die Rundung auch dort greift.
- Der Aggregations-Weg (neue `punktestaende_gerundet_laden`) aus dem ersten Review ist damit **hinfällig**;
  `punktestaende_laden` summiert dann bereits Zehner-konsistente, auf 250 normierte Werte.

**Offene Design-Punkte (für erneuten Rubber-Duck-Design-Review von Option 1):**
1. Auto-3.-Stichwert (012.5) muss so rechnen, dass die **gerundete** Summe 250 ergibt (bisher exakt 250 − w1 − w2).
2. §9.3-Tiebreak: Bleiben 1er-genaue Rohwerte erhalten (dann Eingabe weiter step=1 + exakt speichern), oder wird
   Stichwert-Eingabe im Normalfall auf Zehner umgestellt (step=10) und 1er nur für die letzte Runde?
3. Schema: neues Feld `spielmacher_stichwerte` (+ ggf. `spielmacher_meldepunkte`, Nähe zu TASK-014) + Migration.
4. Bestehende `RundeForm`-Kontrollsummenlogik (`stichwerteGueltig === 250`) auf gerundete Summe umstellen; Vitest + Django + Behave anpassen.
5. Regel: rule-set §9.4 (Rundung an der Eingabe, 250 auf gerundeten Werten) statt „Aggregations-Rundung + akzeptierte Divergenz".

**USER-Entscheidung Punkt 2 (2026-08-17): Variante 2b** — normale Runden in **Zehnern** (step=10) erfassen;
1er-genau **nur in der letzten Runde** für den §9.3-Tiebreak. Damit vereinfacht sich TASK-016 erheblich:
- Normale Stichwerte step=10 → Kontrollsumme = 250 gilt trivial auf Zehnern; **keine** Rundungsfunktion nötig,
  keine 260-Divergenz möglich. FND-002 ist damit im Kern durch `step=10` behoben (STAND automatisch Zehner).
- §9.3-Tiebreak nutzt den **bereits vorhandenen** Backend-Mechanismus `sieger_ermitteln(exakte_stichwerte=…)`
  (= exakte 1er der letzten Runde). UI muss diese nur in der letzten Runde erfassen + durchreichen
  (der „exakte-Stichwerte"-Nachzügler aus TASK-011/012 wird hier eingelöst).
- **Offene Punkte damit reduziert:** (1) entfällt (Auto-3. rechnet in Zehnern, Summe 250 trivial);
  (3) `spielmacher_stichwerte`-Schema für TASK-016 vermutlich NICHT nötig (nur relevant für TASK-014
  M|S-Aufschlüsselung) — im Review bestätigen; (5) rule-set §9.1 („durchgängig 1er") + neuer §9.4 an 2b anpassen.

**Rest-Umsetzung TASK-016 (nach Rubber-Duck-Design-Review):**
- Frontend `RundeForm.vue`: Stichwert-Felder normal step=10; letzte Runde optional 1er-Eingabe für Tiebreak;
  Auto-3.-Stichwert in Zehnern. Vitest anpassen.
- Frontend `SpielendeView`: exakte 1er der letzten Runde an `siegerErmitteln` durchreichen (nur bei Zehner-Gleichstand relevant).
- Regel/Doku: rule-set §9.1/§9.4 (2b), ubiquitous-language, ggf. datenmodell (nur falls SM-Stich doch gespeichert wird), Handover.
- Tests: Django (Stände sind Zehner), Behave (Fixtures bereits Zehner → grün), Vitest (step=10, Tiebreak-Durchreichung).

**Rubber-Duck-Design-Review Option 1 + 2b (2026-08-17): CONDITIONAL GO** — These korrigiert:
- 🔴 **HOCH-1:** `step=10` allein reicht NICHT — getipptes `99` (99+91+60=250) rutscht durch, da `stichwerteGueltig` nur Summe=250 prüft. **Eigentlicher Fix = explizite modulo-10-Validierung** (Absperr-Bedingung + Hinweis), idealerweise für Stichwerte (und Meldepunkte/Reizwert).
- 🔴 **HOCH-2:** Endrunden-1er sind NICHT persistiert (nur Zehner gehen in `runde_persistieren`); `SpielendeView` ist eigene Route → **State-Plumbing über Pinia-`spiel`-Store** nötig (1er der letzten Runde ablegen → `SpielendeView` baut `"Name:Wert,…"` für `siegerErmitteln`). Backend-Mechanik selbst reicht.
- 🟡 **MITTEL-1:** Letzte Runde behält step=10 für den STAND + **separate optionale 1er-„Tiebreak"-Felder** je aktivem Spieler (nicht das Stich-Feld auf step=1 umschalten).
- 🟡 **MITTEL-2:** Echte Regeländerung → **ADR-014** empfohlen; §9.1 (Zehner normal), neuer §9.4 (1er nur Endrunde/Tiebreak), §9.3-Klarstellung; stale BACKLOG-Einträge (TASK-011-Nachzügler, TASK-012.2) korrigieren.
- 🟡 **MITTEL-3:** 250-Prüfung ist aktuell **Frontend-only** (`stichwerte_validieren` wird im HTTP-Pfad nicht aufgerufen) — Spannung zu ADR-006/013. Empfehlung: modulo-10 (+250) im Backend erzwingen + im `runden_view` aufrufen (normal + doppeltes_abgehen).
- ✅ **Bestätigt:** SM-Stich-Schema für TASK-016 **nicht** nötig (nur TASK-014); TASK-015 bleibt nötig; `hat_eigenen_stich = stichwerte>0` bleibt korrekt.
- **Bündelung:** TASK-015 + TASK-016 gemeinsam (gleicher Code in RundeForm), getrennte Commits (015 zuerst).
- Volltext des Reviews: siehe Session-/Chat-Ergebnis (Coding-Agent-Brief enthält Testliste + 5-Schritte-Plan).

---

## FND-003 — Schneider-Annotation „(0 Stiche)" erscheint fälschlich bei einfachem Abgehen

- **Status:** ✅ BEHOBEN (2026-08-26) — Wurzel war ein Format-Mismatch: Backend liefert `rundenausgang` als Klartext (`"einfaches Abgehen"`), Frontend verglich gegen den Slug `'einfaches_abgehen'`. Fix: zentrale `RUNDENAUSGANG`-Klartext-Konstanten in `api/types.ts`; `Anschreibetabelle.vue` vergleicht gegen `RUNDENAUSGANG.EINFACHES_ABGEHEN`; Frontend-Tests von Slug auf Klartext korrigiert (der bestehende „KEINE Schneider-Annotation"-Test ist damit erst aussagekräftig). Vitest 58 grün + Live-Browser bestätigt (Carla `40 | 0 | 30`, kein `(0 Stiche)`).
- **Datum:** 2026-08-26
- **Modus:** Pairing
- **Bereich:** Anschreibetabelle (`frontend/src/components/Anschreibetabelle.vue`, §2 Stich-Zwang / §5 Darstellung)
- **Schwere:** MITTEL (fachlich irreführende Darstellung; Regelwidrigkeit in der Anzeige, keine Fehlberechnung des STAND)
- **Repro-Test:** noch keiner (Vitest-Repro empfohlen)

**Repro-Schritte:**
1. Neues Spiel anlegen. Erste Runde als normales Spiel werten (damit der Geber rotiert).
2. Nächste Runde als **einfaches Abgehen** werten; die Gegenspieler behalten Meldepunkte, haben aber **keine eigenen Stiche** (Stichwerte 0).
3. Anschreibetabelle ansehen: Rundenzeile der Gegenspieler.

**Erwartet (Regelbezug §2 / §5):**
Bei einfachem Abgehen entfällt der Stich-Zwang für die Gegner — sie behalten ihre Meldepunkte **ohne** Schneider-Hinweis. Die normative §5-Vorlage (Szenario B, Beispielrunde 2) zeigt `40 | 0 | 30` bzw. `20 | 0 | 30` **ohne** „(0 Stiche)".

**Ist:**
Die Gegenspielerzellen zeigen `40 | 0 | 30 (0 Stiche)` bzw. `20 | 0 | 30 (0 Stiche)` — die Schneider-Annotation erscheint, obwohl bei einfachem Abgehen kein Schneider vorliegt.

**Ursache (Codeanalyse, per API bestätigt):**
`Anschreibetabelle.vue::zellDarstellung` schließt die Schneider-Annotation über `runde.rundenausgang !== 'einfaches_abgehen'` aus. Die API (`GET /api/spiele/{id}/runden/`) liefert `rundenausgang` aber als **`"einfaches Abgehen"`** (Klartext mit Leerzeichen, Groß-A) — nicht als `'einfaches_abgehen'`. Der Vergleich greift daher nie, die Annotation wird fälschlich angezeigt.

**Vorschlag (Fix beim Coding-Agenten):**
Frontend und Backend auf einen **konsistenten Ausgangs-Bezeichner** bringen (entweder Backend liefert einen stabilen Slug/Enum-Wert, oder Frontend vergleicht gegen den tatsächlichen Klartext). Bevorzugt: stabiler maschinenlesbarer Wert in der API (siehe auch FND-005). Vitest-Repro: einfaches Abgehen mit Gegenspieler ohne Stich → keine `(0 Stiche)`-Annotation.

---

## FND-004 — Korrektur einer verlorenen Runde (doppeltes Abgehen) blockiert: Spielmacher-Stichwert nicht vorbelegt

- **Status:** ✅ BEHOBEN (2026-08-26, Rubber-Duck GO Option A) — Bei doppeltem Abgehen werden die roh erfassten Spielmacher-`M | S` jetzt persistiert (Backend `views.py`, else-Zweig „doppeltes Abgehen“). Die Invariante `spielmacher_punkte == M + S` gilt damit nur bei gewonnenem Spiel; einfaches Abgehen/Tausender bleiben `0 | 0`. Anschreibetabelle (`(-x)|0|0`) und STAND (`verlustwert`) unberührt. Korrektur-Vorbelegung erfüllt automatisch die 250-Kontrollsumme (kein Frontend-Code-Change). Doku: models.py-Docstring + datenmodell-v1.puml (Invariante neu formuliert), ubiquitous-language §4.25, ADR-015-Nachtrag. Tests: `test_doppeltes_abgehen_ms_roh_persistiert` + `test_doppeltes_abgehen_roh_ermoeglicht_korrektur` (Django) + Vitest-Reprotest (SpielView Vorbelegung 250 / Button aktiv). Verifiziert: 55 Django + 31 Behave + 59 Vitest + Build grün; Live-curl (GET SM-Stichwert 60 statt 0).
- **Datum:** 2026-08-26
- **Modus:** Pairing
- **Bereich:** Korrektur der letzten Runde (`frontend/src/components/RundeForm.vue` Vorbelegung + Backend-Persistenz `spielmacher_stichwerte`, ADR-015 / §16.1)
- **Schwere:** MITTEL–HOCH (Korrektur einer als doppeltes Abgehen gewerteten Runde ist ohne erneute Eingabe des SM-Stichwerts nicht speicherbar)
- **Repro-Test:** noch keiner (Vitest- + Django-Repro empfohlen)

**Repro-Schritte:**
1. Spiel anlegen. Als letzte (höchste) Runde ein **normales Spiel** erfassen, bei dem der Spielmacher den Reizwert verfehlt (z. B. Reizwert 200, SM S=60, Gegner S=100/90 → Summe 250) → wird als **doppeltes Abgehen** gewertet (-400).
2. „Letzte Runde korrigieren" klicken.
3. Vorbelegung der Form ansehen.

**Erwartet:**
Die Form ist mit den ursprünglich erfassten Stichwerten vorbelegt, sodass die Kontrollsumme **250/250** ergibt und die Runde ohne erneute Eingabe wieder speicherbar ist (bzw. gezielt einzelne Werte änderbar sind).

**Ist:**
Der **Spielmacher-Stichwert ist mit 0 vorbelegt** (statt 60). Die Kontrollsumme steht auf **190/250**, „Korrektur speichern" bleibt gesperrt. Erst nach manueller Neueingabe des SM-Stichwerts (60) wird die Runde wieder speicherbar.

**Ursache (Hypothese, Codeanalyse):**
Bei doppeltem Abgehen verfallen die Spielmacher-Stiche fachlich; `spielmacher_stichwerte` wird offenbar als **0** persistiert. Die Korrektur-Vorbelegung liest die persistierten (gestrichenen) Werte → der Roh-Stichwert für die 250-Kontrollsumme fehlt.

**Vorschlag (Fix beim Coding-Agenten — Rubber-Duck-Review zuerst):**
Roh-Stichwert des Spielmachers **auch bei doppeltem Abgehen persistieren** (verfallen betrifft nur die STAND-Wertung, nicht die Rohdaten für die Korrektur) — analog zur getrennten M|S-Persistenz aus TASK-014. Alternativ die Korrektur-Vorbelegung so gestalten, dass eine verlorene Runde wieder editierbar ist. Regel-/Modell-Auswirkung prüfen (`datenmodell-v1.puml`, ADR-015). Repro-Tests: Vitest (Vorbelegung Summe 250 nach doppeltem Abgehen) + Django (PUT-Korrektur einer verlorenen Runde).

---

## FND-005 — Rundenausgang fehlt in der Anschreibetabelle (Spalte „Gereizt bis")

- **Status:** ✅ BEHOBEN (2026-08-26) — `Anschreibetabelle.vue` zeigt jetzt je Runde ein Ausgangs-Label unter „Gereizt bis" (`ausgangLabel`, `data-testid=ausgang-{nr}`): „gewonnen" / „einfaches Abgehen" / „doppeltes Abgehen" / bei Tausender „gewonnen"|„verloren". Basiert auf denselben `RUNDENAUSGANG`-Klartext-Konstanten wie FND-003. Vitest-Regressionstest ergänzt; Live-Browser bestätigt.
- **Datum:** 2026-08-26
- **Modus:** Pairing
- **Bereich:** Anschreibetabelle (`frontend/src/components/Anschreibetabelle.vue`, §5 Darstellung)
- **Schwere:** NIEDRIG (Norm-/Lesbarkeitsabweichung; STAND und Werte sind korrekt)
- **Repro-Test:** noch keiner

**Repro-Schritte:**
1. Mehrere Runden unterschiedlicher Ausgänge werten (gewonnen, einfaches/doppeltes Abgehen, Tausender).
2. Anschreibetabelle ansehen, Spalte „Gereizt bis".

**Erwartet (Regelbezug §5):**
Die normative §5-Vorlage annotiert in der „Gereizt bis"-Spalte zusätzlich den **Rundenausgang**, z. B. `180 / B (Gewonnen)`, `250 / C (A) - Einfach`, `200 / A (V) - Doppelt`, `Tausender / D (Gewonnen)`. So ist auf einen Blick erkennbar, wie eine Runde ausging.

**Ist:**
Die Zelle zeigt nur `<Reizwert> / <Spielmacher>` (z. B. `150 / Bernd`) bzw. `Tausender / <Spielmacher>`. Der Rundenausgang ist nicht ausgewiesen; bei Verlust erkennt man ihn nur indirekt am eingeklammerten `(-x)`-Wert, gewonnene Runden sind nicht gekennzeichnet.

**Vorschlag (Fix beim Coding-Agenten):**
Ausgangs-Annotation in der „Gereizt bis"-Spalte ergänzen (gewonnen / einfaches Abgehen / doppeltes Abgehen / Tausender gewonnen/verloren), analog §5. Voraussetzung: stabiler maschinenlesbarer `rundenausgang`-Wert in der API (Synergie mit FND-003).

---

## FND-006 — Tausender-Runden zählen fälschlich als reguläre Runde (Rundenzähler + Geberrotation)

- **Status:** ✅ BEHOBEN (2026-08-27, ADR-016) — Entkopplung Erfassungs-Sequenz (`rundennummer`, backend-vergeben) von der gezählten Spielrunde (`zaehlrunde`, aus der Historie abgeleitet, Tausender = `null`). Geber der Korrektur via `geber_fuer_sequenz`; Frontend leitet Fortschritt/Geber/Spielende aus der Historie ab; Anschreibetabelle zeigt Tausender „außer Konkurrenz" ohne Nummer. **Keine Migration.** Verifiziert: 61 Django (+6) / 32 Behave (+1) / 61 Vitest (+2) grün, Build/TSC grün, Live-Browser (Spiel 23: „Runde 4 / 4", Geber Volker bleibt, Tausender-Zeile außer Konkurrenz).
- **Datum:** 2026-08-27
- **Modus:** Pairing
- **Bereich:** Rundenzählung / Geberrotation / Persistenz / Spielende — `stores/spiel.ts` (`naechsteRunde`), `views/SpielView.vue` (`rundennummer`/`geber`/`istBeendet`), `domain/rotation.ts` (`geberFuerRunde`), `backend/scoring/models.py` (`RundeModel` `UniqueConstraint(spiel, rundennummer)`), `views.py`/`repositories.py` (Persistenz + Historie + Korrektur).
- **Schwere:** HOCH (verfälscht Rundenzahl, Geberrotation und Spielende; ganzes Spiel läuft aus dem Takt)
- **Repro-Test:** noch keiner (Django + Vitest + ggf. Behave nach Design-Entscheidung)

**Repro-Schritte:**
1. Spiel mit fester Rundenanzahl anlegen (z. B. 4).
2. Runden regulär spielen; in Runde 4 (letzte Runde) einen **Tausender** erfassen (gewonnen oder verloren).
3. Rundenfortschritt und Spielstatus beobachten.

**Erwartet (Regelbezug — USER-Präzisierung 2026-08-27):**
Ein Tausender läuft **außer Konkurrenz** und zählt **nicht** als gespielte Runde:
- Der Rundenzähler (`Runde X / Y`) erhöht sich durch einen Tausender **nicht**.
- Der **Geber wechselt nicht** — die (dann folgende) Runde wird mit **demselben Geber** und derselben Rundennummer erneut gespielt.
- Es wird so lange erneut gespielt, **bis kein Tausender mehr** angesagt wird; erst eine reguläre Runde (gewonnen / einfaches / doppeltes Abgehen) zählt und rückt Zähler + Geber weiter.
- Die Tausender-Sterne (§15) bleiben erhalten und müssen weiterhin sichtbar sein.

**Ist:**
Ein Tausender wird wie eine reguläre Runde behandelt: `naechsteRunde()` erhöht den Rundenzähler, der Geber rotiert, und bei einem Tausender in der letzten Runde gilt das Spiel als **beendet** — obwohl die außer-Konkurrenz-Runde nicht zählen dürfte.

**Ursache (Codeanalyse):**
- Frontend koppelt Rundennummer → Geber → Spielende deterministisch: `geberFuerRunde(spieler, rn) = spieler[(rn-1) % 4]`, `istBeendet = rn > rundenanzahl`. `rundeAbsenden` ruft nach **jedem** Rundentyp `spielStore.naechsteRunde()` (auch bei Tausender).
- Backend `RundeModel` erzwingt `UniqueConstraint(spiel, rundennummer)` — mehrere Ereignisse (Tausender + Wiederholung) mit gleicher Rundennummer sind aktuell **nicht** persistierbar. Rundenzählung ist strukturell an die Persistenz gekoppelt.

**Offene Design-Fragen (vor Fix mit USER zu klären):**
1. Anschreibetabelle: Tausender-Runde weiterhin als eigene Zeile (mit ★) zeigen, als „außer Konkurrenz" markiert? Nummerierung (keine fortlaufende Nummer / Kennzeichnung)?
2. Persistenz-Modell: separates fortlaufendes Sequenzfeld (DB-Identität) entkoppelt von der „gezählten" Rundennummer (Geber/Fortschritt)? Oder `UniqueConstraint` lockern?
3. Korrektur (PUT letzte Runde): Ist ein Tausender korrigierbar? Was ist „die letzte Runde", wenn zuletzt Tausender → dann reguläre Runde gespielt wurde?

**Nächster Schritt:**
Design-Entscheidung mit USER → Rubber-Duck-Design-Review (Datenmodell/Migration/Korrektur) → dann Umsetzung Backend+Frontend + vollständige Doku (rule-set §15, ADR-016, datenmodell-v1.puml, ubiquitous-language, ggf. Behave-Szenario).



---

## FND-006-Nachprüfung + 3 kleine Darstellungs-Findings (2026-08-28, Pairing)

- **Modus:** Pairing (Durchspielen im geteilten Browser, Spiel 24: Anna/Bernd/Carla/Dirk, 4 Runden).
- **Ergebnis FND-006:** ✅ In allen drei Edge-Cases korrekt:
  1. **Mehrere Tausender hintereinander:** Zähler bleibt „1 / 4", Geber bleibt Anna;
     Sterne korrekt (SM bei „gewonnen", aktive Gegenspieler bei „verloren", nie der Geber);
     Sidebar-Aggregation korrekt (Bernd ★★, Dirk ★). STAND unverändert.
  2. **Korrektur eines Tausenders (PUT):** „Letzte Runde korrigieren" belegt korrekt vor;
     Ausgang „verloren"→„gewonnen" berechnet Sterne neu; Zähler bleibt 1 / 4.
  3. **Endrunde mit Tausender:** Tausender in Runde 4 / 4 beendet das Spiel NICHT;
     erst die 4. gezählte Normalrunde beendet es; Sieger rein nach Punkten (Anna 600).

**Drei kleine Findings (alle NIEDRIG, keine Blocker) → BACKLOG TASK-017/018/019:**

- **FND-007 (Kosmetik, aus TASK-014):** `Anschreibetabelle.vue` — Spaltenkopf „Wert" steht
  über der Zeilen-Label-Spalte, deren Zellen aber „Runde"/„STAND" enthalten → semantisch
  unpassend. → TASK-017.
- **FND-008 (UX, NIEDRIG/MITTEL):** Korrektur-Dialog-Kopf zeigt „Runde 2" (= Erfassungs-Sequenz
  `rundennummer`) für einen Tausender, der überall sonst als „außer Konkurrenz" ohne Nummer
  erscheint → potenziell verwirrend. → TASK-018.
- **FND-009 (UX, NIEDRIG):** Nach allen gezählten Runden zeigt die Überschrift „Runde 5 / 4"
  (abgeleitet `gezählteRunden + 1`), begleitet von „Alle 4 Runden gespielt." → Zähler wirkt
  falsch; auf „4 / 4 – beendet" o. ä. kappen. → TASK-019.
