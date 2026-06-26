# Copilot-Handover für V1

## Ziel
Dieses Repository modelliert fachlich einen Binokel Score Tracker auf Basis von BDD.

## Führende Dokumente
Die folgende Priorität gilt bei Unklarheiten:

1. `docs/rule-set-v1.md`
2. `docs/ubiquitous-language.md`
3. `docs/language-conventions.md`
4. `docs/Anschreibetabelle_4_Spieler.md`

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

### Offene Todos (nächster Schritt)

1. **Fehlende Szenarien prüfen** (optional, fachlich)
   - Geberrotation über mehrere Runden
   - 250er-Kontrollsumme als Validierungsfehler bei falschen Eingaben
   - Verlustwert-Darstellung mit Klammern

2. **Projektstruktur aufsetzen** (technisch)
   - BDD-Toolchain für Python/Django einrichten (z. B. `behave`)
   - Projektgerüst anlegen
   - Step-Definitionen als leere Stubs aus der Referenzdatei generieren

3. **Step-Definitionen schreiben**
   - Auf Basis von `docs/gherkin-step-phrase-reference-v1.md`
   - Zunächst ohne Domänenlogik (pending)

4. **Domänenlogik implementieren**
   - Fachklassen für Rundenauswertung, Stich-Zwang, Punktestand
   - Normative Quelle: `docs/rule-set-v1.md`
