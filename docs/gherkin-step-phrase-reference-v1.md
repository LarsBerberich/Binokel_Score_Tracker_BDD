# Gherkin Step Phrase Reference V1

Zweck: Einheitliche, wiederverwendbare Step-Phrasen fuer die Testautomation.

Hinweise:
- Gleiches Fachkonzept immer gleich formulieren.
- Variablen stehen in spitzen Klammern.
- Diese Liste orientiert sich an den Feature-Dateien unter features/.

Normative Quellen:
- `docs/rule-set-v1.md` – verbindliches V1-Regelwerk; Grundlage für alle fachlichen Step-Formulierungen
- `docs/development-approach-v1.md` – beschreibt, wie diese Phrasen als Step-Stubs zur RED-Phase verwendet werden

## Standard-Trigger

### Runde auswerten
- Wenn die Runde ausgewertet wird

### Spiel abschliessen
- Wenn das Spiel abgeschlossen wird

## Rundenausgang

### Einfaches Abgehen
- Angenommen der Rundenausgang ist "einfaches Abgehen"
- Dann ist der Rundenausgang "einfaches Abgehen"

### Doppeltes Abgehen
- Angenommen der Rundenausgang ist "doppeltes Abgehen"
- Dann ist der Rundenausgang "doppeltes Abgehen"

### Gewonnenes Spiel
- Dann ist der Rundenausgang "gewonnenes Spiel"

## Reizwert und Zielerreichung des Spielmachers
- Und der Reizwert des Spielmachers ist <reizwert>
- Und der Spielmacher hat <meldepunkte> Meldepunkte und <stichwerte> Stichwerte einschliesslich gedrueckter Karten
- Und der Spielmacher erreicht mit <summe> Punkten den Reizwert
- Und der Spielmacher erreicht mit <summe> Punkten den Reizwert nicht

## Verlustwert und Verfall beim Spielmacher
- Dann wird beim Spielmacher der Verlustwert "<verlustwert>" eingetragen
- Und die Meldepunkte des Spielmachers werden mit 0 gewertet
- Und die Stichwerte des Spielmachers werden mit 0 gewertet

## Stich-Zwang als Zaehlregel

### Allgemein
- Und der <rolle> hat 0 eigene Stiche

### Gegenspieler
- Und ein Gegenspieler hat <meldepunkte> Meldepunkte
- Dann werden die Meldepunkte des Gegenspielers mit 0 gewertet
- Dann werden die Meldepunkte des Gegenspielers gewertet

### Aktiver Spieler
- Und ein aktiver Spieler hat <meldepunkte> Meldepunkte gemeldet
- Dann werden seine Meldepunkte mit 0 gewertet

## Stichwerte und Mitpunkte bei Gegenspielern
- Und ein Gegenspieler hat <stichwerte> Stichwerte
- Dann werden die <stichwerte> Stichwerte des Gegenspielers gewertet
- Dann erhält jeder aktive Gegenspieler 30 Mitpunkte

## Tausender
- Angenommen eine Runde ist als Tausender angesagt
- Und der Tausender-Ausgang ist "gewonnen"
- Und der Tausender-Ausgang ist "verloren"
- Dann erhält nur der Spielmacher einen Stern
- Und der Spielmacher erhält keinen Stern
- Dann erhalten die beiden aktiven Gegenspieler jeweils einen Stern
- Und die aktiven Gegenspieler erhalten keinen Stern
- Dann werden keine Meldepunkte erfasst
- Und es werden keine Stichwerte erfasst
- Und es werden keine Mitpunkte erfasst
- Dann bleibt der numerische Punktestand für alle Spieler unverändert

## Spiel anlegen
Die Spielerzahl (3 oder 4) bestimmt die Variante (ADR-017). Szenarien, die für beide Varianten
gelten, werden als **Szenariogrundriss** mit einer `Beispiele`-Tabelle formuliert (Spalte `spieler`).
- Angenommen es wird ein neues V1-Spiel angelegt
- Wenn die Spielerreihenfolge "<spieler>" gegen den Uhrzeigersinn erfasst wird
- Wenn nur die Spieler "<spieler>" erfasst werden
- Und keine abweichende Rundenzahl angegeben wird
- Und als Rundenzahl <runden> angegeben wird
- Dann wird das Spiel mit <runden> Runden angelegt
- Und die Spielerreihenfolge bleibt als "<spieler>" gespeichert
- Dann wird das Spiel nicht angelegt
- Und es wird ein Fehler zur ungültigen Spielerzahl angezeigt
- Und es wird ein Fehler angezeigt, dass die Rundenzahl ein Vielfaches von <teiler> sein muss

## Spielende und Siegerermittlung
- Angenommen die letzte Runde ist ausgewertet
- Dann ist <spielername> alleiniger Sieger
- Dann wird der Gesamtsieg nicht über die Sterne entschieden
- Dann wird die Siegerermittlung mit den exakten 1er-Werten durchgeführt
- Dann gibt es mehrere Sieger

## Geberrotation und aktive Spieler
- Angenommen das Spiel wurde mit der Spielerreihenfolge "<spieler>" angelegt
- Dann ist <spielername> Geber in Runde <rundennummer>
- Und <spielername> ist Geber in Runde <rundennummer>
- Dann spielen in Runde <rundennummer> "<aktive>" aktiv mit
- Und der Geber in Runde <rundennummer> setzt aus
- Und der Geber in Runde <rundennummer> spielt mit

Hinweis: „setzt aus" gilt nur bei 4 Spielern, „spielt mit" nur bei 3 (rule-set-v1.md §3.4).
Die frühere Phrase „… ist erneut Geber in Runde …" entfällt; die Rotation über einen vollen
Durchgang hinaus wird in der `Beispiele`-Tabelle für jede Runde einzeln geprüft.

## Stichwert-Validierung
- Und die Stichwerte aller drei aktiven Spieler sind <wert_1>, <wert_2> und <wert_3>
- Dann wird die Eingabe abgelehnt
- Und es wird ein Fehler angezeigt, dass die Stichwerte in der Summe 250 ergeben müssen

## Verlustwert-Darstellung in der Tabelle
- Dann wird der Verlustwert als "<darstellungswert>" in der Tabelle dargestellt

## Korrektur der letzten Runde
Läuft für 3 und 4 Spieler; der Given-Schritt „ein neues Spiel mit der Spielerreihenfolge …" ist
unter „HTTP-Szenarien für beide Varianten" beschrieben.
- Angenommen eine reguläre Runde ist für die Korrektur erfasst
- Angenommen zwei reguläre Runden sind für die Korrektur erfasst
- Wenn die letzte Runde mit einem höheren Spielmacher-Ergebnis korrigiert wird
- Wenn versucht wird, die erste Runde zu korrigieren
- Dann wird die Korrektur übernommen
- Und der kumulierte STAND des Spielmachers beträgt <punkte>
- Dann wird die Korrektur abgelehnt

## HTTP-Szenarien für beide Varianten (ADR-017)
Gemeinsamer Ausgangsschritt der HTTP-Blackbox-Szenarien (Tausender außer Konkurrenz, Korrektur,
Endrunden-Tiebreak, Rollen je Spielerzahl):
- Angenommen ein neues Spiel mit der Spielerreihenfolge "<spieler>" und <runden> Runden ist angelegt

Rollen je Spielerzahl (`runde_rollen_je_spielerzahl.feature`):
- Wenn <spielmacher> bei Geber <geber> einen Tausender verliert
- Dann erhalten genau <sternempfaenger> je einen Stern
- Wenn eine reguläre Runde mit Spielmacher <spielmacher> und Geber <geber> gespielt wird
- Dann hat <geber> in der Rundenhistorie die Rolle "<rolle>" und ist als Geber gekennzeichnet
- Dann hat <spielername> den Punktestand <punkte>

Endrunden-Tiebreak:
- Und die letzte Runde führt zu einem Gleichstand in Zehnern zwischen <gegenspieler_1> und <gegenspieler_2>
- Wenn der Sieger mit exakten 1er-Stichwerten <gegenspieler_1> <wert_1> und <gegenspieler_2> <wert_2> ermittelt wird
- Dann ist <spielername> der alleinige Sieger des Spiels

## Abrechnung (`abrechnung.feature`, rule-set §20)
Läuft für 3 und 4 Spieler. Beträge liefert die API in ganzen Cent; die Szenarien nennen sie im
Euro-Format, mehrere Spieler getrennt durch `;`.
- Wenn <spielmacher> bei Geber <geber> einfach abgeht und die Gegenspieler je 40 Meldepunkte haben
- Dann zahlen die Spieler "<name> <betrag>; <name> <betrag>; …"
