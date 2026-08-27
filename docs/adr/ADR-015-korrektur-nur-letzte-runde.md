# ADR-015 – Korrektur: nur die letzte Runde bearbeitbar

## Status

Angenommen (25.08.2026)

## Kontext

Mit der tabellarischen Anschreibetabelle (TASK-014, `docs/Anschreibetabelle_4_Spieler.md` §5)
wird der komplette Rundenverlauf sichtbar. Damit entsteht der berechtigte Nutzerwunsch,
eine **falsch erfasste Runde korrigieren** zu können, ohne das ganze Spiel neu anzulegen.

Eine Korrektur beliebiger Runden aus der Mitte ist fachlich riskant:

- Der **Geber** ergibt sich deterministisch aus der Rundennummer (feste Rotation, §3). Das
  Verschieben/Löschen einer mittleren Runde würde die Sequenz und damit die Geber-/Spielmacher-
  Zuordnung aller Folgerunden brechen.
- Der **STAND** wird bei jedem Aufruf aus **allen** Runden neu aggregiert
  (`repositories.punktestaende_laden`, gemeinsamer Pro-Runde-Beitrag, ADR-004). Eine Lücke in der
  Rundennummer-Sequenz erzeugt inkonsistente Zwischenstände.

Zwei Optionen standen zur Wahl: (a) die letzte Runde nur **löschen** und neu eingeben, oder
(b) die letzte Runde **bearbeiten** (in-place korrigieren). Der Repo-Eigentümer hat (a) als zu
umständlich verworfen (kompletter Neu-Eintrag).

## Entscheidung

**Es ist ausschließlich die zuletzt erfasste Runde (höchste Rundennummer) bearbeitbar.**

- Endpunkt `PUT /api/spiele/{id}/runden/{nr}/` ersetzt die Runde transaktional (alte
  `RundeModel`- + `GegenspielerRundeModel`-Zeilen weg, neu mit **gleicher** Rundennummer).
- Der **Geber bleibt fix** und wird deterministisch aus der Rundennummer abgeleitet (nicht vom
  Client übernommen). Die Rundennummer selbst ändert sich nicht → Sequenz und Rotation bleiben intakt.
- Der Nutzer darf **alle übrigen Werte** ändern: Reizwert, Spielmacher, Ausgangstyp (inkl.
  Wechsel z. B. `gewonnen` ↔ `tausender`) und alle M|S|Mit-Werte.
- PUT durchläuft **denselben** Body-Dispatch und **dieselbe** Validierung wie das Anlegen
  (Modulo-10, 250-Kontrollsumme, Meldepunkte-Maximum 1800, Spielmacher ≠ Geber, Spielmacher ∈
  aktive Spieler). Dispatch und Validierung sind in einer **gemeinsamen** Funktion gebündelt, die
  POST und PUT teilen — keine Duplikation, kein Drift.
- Der STAND wird **nicht** separat nachgerechnet, sondern ergibt sich automatisch aus der
  Aggregation über den gemeinsamen Pro-Runde-Beitrag (ADR-004/TASK-014).

### Statuscodes

- Korrektur einer **Nicht-letzten** Runde → **409 Conflict**.
- Korrektur einer **nicht existierenden** Runde → **404 Not Found**.
- Validierungsfehler → **400** (bestehendes `_fehler`-Schema).

## Konsequenzen

- **Positiv:** Deutlich bessere Bedienbarkeit (Korrektur statt Neu-Eingabe) bei minimalem Risiko;
  Sequenz/Rotation strukturell unangreifbar; STAND bleibt Single-Source-konsistent.
- **Positiv:** Der Typwechsel (z. B. `tausender` → `normal`) funktioniert korrekt, weil PUT den
  vollständigen Dispatch durchläuft: Gegenspieler-Zeilen und Sterne werden passend umgeschaltet.
- **Einschränkung (bewusst):** Fehler in weiter zurückliegenden Runden erfordern das Zurückkehren
  über mehrere Korrekturen bzw. sind in V1 nicht direkt editierbar. Für den typischen
  Live-Anschreibe-Fall (der letzte Eintrag war falsch) ist das ausreichend.

## Bezug

- TASK-014 (Rundenhistorie, Anschreibetabelle, Korrektur)
- ADR-004 (Repository Pattern, STAND-Aggregation), ADR-006/013 (fachliche Wahrheit auf API-Ebene)
- `docs/rule-set-v1.md` §3 (Geberrotation), `docs/Anschreibetabelle_4_Spieler.md` §5

## Nachtrag (26.08.2026) – Roh-Persistenz der Spielmacher-M|S bei doppeltem Abgehen (FND-004)

Beim manuellen Durchspielen fiel auf, dass die Korrektur einer als **doppeltes Abgehen** gewerteten
Runde blockiert war: Im Korrekturformular war der Spielmacher-Stichwert mit 0 vorbelegt, sodass die
250-Kontrollsumme nicht erfüllt war und „Korrektur speichern“ gesperrt blieb (FND-004,
`docs/testing/explorative-testprotokoll.md`).

Ursache war die ursprüngliche TASK-014-Invariante `spielmacher_punkte == M + S`, die bei jedem
Verlust `M | S = 0 | 0` erzwang. Bei doppeltem Abgehen hat der Spielmacher jedoch **real
ausgespielt** – die Stichwerte existieren fachlich, sie zählen nur nicht (§4 Szenario C: sie
„verfallen“ = fließen nicht in den STAND, das Tabellenfeld zeigt `(-x) | 0 | 0`).

**Entscheidung:** Bei **doppeltem Abgehen** werden die roh erfassten `M | S` des Spielmachers
persistiert (als Korrektur-/Nachvollziehbarkeits-Beleg). Die Invariante gilt damit nur noch bei
**gewonnenem Spiel**; bei **einfachem Abgehen** (SM geht vor dem ersten Stich ab → S=0) und
**Tausender** bleiben `M | S = 0 | 0`.

- **Regelkonform:** „Verfallen“ ist auf Wertungs-/Darstellungsebene definiert. Anschreibetabelle
  (Verlustdarstellung `(-x) | 0 | 0`) und STAND (`_runde_beitrag` über `verlustwert`) bleiben
  wörtlich unverändert – die roh persistierten Werte werden dort nicht gelesen.
- **Migrationsfrei:** Die Felder `spielmacher_meldepunkte` / `spielmacher_stichwerte` existieren
  bereits (Default 0). Kein Backfill für Altbestand nötig (nur die letzte Runde ist korrigierbar).
- Die Korrektur-Vorbelegung (`SpielView.korrekturVorbelegung`) funktioniert dadurch automatisch;
  kein Frontend-Code-Change nötig.

