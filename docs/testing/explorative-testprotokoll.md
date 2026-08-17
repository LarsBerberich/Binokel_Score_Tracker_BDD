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


