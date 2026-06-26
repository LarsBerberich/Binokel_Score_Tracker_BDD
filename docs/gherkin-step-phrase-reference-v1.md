# Gherkin Step Phrase Reference V1

Zweck: Einheitliche, wiederverwendbare Step-Phrasen fuer die Testautomation.

Hinweise:
- Gleiches Fachkonzept immer gleich formulieren.
- Variablen stehen in spitzen Klammern.
- Diese Liste orientiert sich an den Feature-Dateien unter features/.

## Standard-Trigger

### Runde auswerten
- Wenn die Runde ausgewertet wird

### Spiel abschliessen
- Wenn das Spiel abgeschlossen wird

## Rundenausgang

### Einfaches Abgehen
- Gegeben der Rundenausgang ist "einfaches Abgehen"
- Dann ist der Rundenausgang "einfaches Abgehen"

### Doppeltes Abgehen
- Gegeben der Rundenausgang ist "doppeltes Abgehen"
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
- Gegeben eine Runde ist als Tausender angesagt
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
- Gegeben es wird ein neues V1-Spiel angelegt
- Wenn die Spielerreihenfolge "<spieler_1>, <spieler_2>, <spieler_3>, <spieler_4>" gegen den Uhrzeigersinn erfasst wird
- Und keine abweichende Rundenzahl angegeben wird
- Und als Rundenzahl <rundenanzahl> angegeben wird
- Dann wird das Spiel mit <rundenanzahl> Runden angelegt
- Und die Spielerreihenfolge bleibt als "<spieler_1>, <spieler_2>, <spieler_3>, <spieler_4>" gespeichert
- Dann wird das Spiel nicht angelegt

## Spielende und Siegerermittlung
- Gegeben die letzte Runde ist ausgewertet
- Dann ist <spielername> alleiniger Sieger
- Dann wird der Gesamtsieg nicht über die Sterne entschieden
- Dann wird die Siegerermittlung mit den exakten 1er-Werten durchgeführt
- Dann gibt es mehrere Sieger
