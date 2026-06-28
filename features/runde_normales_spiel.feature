# language: de
Funktionalität: Normale Runde auswerten
  Um den Ausgang einer regulär ausgespielten Runde korrekt zu bestimmen
  möchte ich normale Runden auf Basis von Reizwert, Meldepunkten und Stichwerten auswerten können.

  Regelhintergrund:
  - Ein normales Spiel ist gewonnen, wenn der Spielmacher seinen Reizwert erreicht oder überschreitet.
  - Für die Prüfung zählen Meldepunkte und exakte Stichwerte des Spielmachers einschließlich gedrückter Karten.
  - Der Stich-Zwang gilt im Normalfall für alle aktiven Spieler.
  - Meldepunkte zählen nur bei mindestens einem eigenen Stich.
  - Mitpunkte werden in einem gewonnenen normalen Spiel nicht vergeben.

  Szenario: Spielmacher gewinnt durch Erreichen des Reizwerts
    Gegeben eine regulär ausgespielte Runde mit Reizwert 180
    Und der Spielmacher hat 60 Meldepunkte und 130 Stichwerte einschließlich gedrückter Karten
    Wenn die Runde ausgewertet wird
    Dann ist der Rundenausgang "gewonnenes Spiel"
    Und der Spielmacher erreicht mit 190 Punkten den Reizwert
    Und es werden keine Mitpunkte vergeben

  Szenario: Spielmacher verfehlt den Reizwert nach regulärem Ausspielen
    Gegeben eine regulär ausgespielte Runde mit Reizwert 220
    Und der Spielmacher hat mindestens einen eigenen Stich
    Und der Spielmacher hat 80 Meldepunkte und 130 Stichwerte einschließlich gedrückter Karten
    Wenn die Runde ausgewertet wird
    Dann ist der Rundenausgang "doppeltes Abgehen"
    Und der Spielmacher erreicht mit 210 Punkten den Reizwert nicht

  Szenario: Meldepunkte eines aktiven Spielers verfallen ohne eigenen Stich
    Gegeben eine regulär ausgespielte Runde
    Und ein aktiver Spieler hat 40 Meldepunkte gemeldet
    Und der aktive Spieler hat 0 eigene Stiche
    Wenn die Runde ausgewertet wird
    Dann werden seine Meldepunkte mit 0 gewertet

  Szenario: Fehlender dritter Stichwert wird aus der 250er-Kontrollsumme ermittelt
    Gegeben eine regulär ausgespielte Runde
    Und die Stichwerte zweier aktiver Spieler sind 90 und 100
    Wenn die Runde ausgewertet wird
    Dann wird der fehlende dritte Stichwert mit 60 ermittelt
    Und die Summe der drei Stichwerte beträgt 250

  Szenario: Eingabe wird abgelehnt wenn die Summe aller drei Stichwerte die Kontrollsumme 250 überschreitet
    Gegeben eine regulär ausgespielte Runde
    Und die Stichwerte aller drei aktiven Spieler sind 90, 100 und 70
    Wenn die Runde ausgewertet wird
    Dann wird die Eingabe abgelehnt
    Und es wird ein Fehler angezeigt, dass die Stichwerte in der Summe 250 ergeben müssen
