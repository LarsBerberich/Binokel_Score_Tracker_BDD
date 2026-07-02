# language: de
Funktionalität: Doppeltes Abgehen auswerten
  Um einen ausgespielten, aber verlorenen Reiz korrekt abzurechnen
  möchte ich doppeltes Abgehen als eigenen Rundenausgang behandeln.

  Regelhintergrund:
  - Doppeltes Abgehen liegt vor, wenn der Spielmacher ausspielt, aber den Reizwert nicht erreicht.
  - Der Spielmacher erhält den negativen doppelten Reizwert als Verlustwert.
  - Eigene Meldepunkte und Stichwerte des Spielmachers verfallen.
  - Die Gegenspieler erhalten ihre Stichwerte und jeweils +30 Mitpunkte.
  - Für die Meldepunkte der Gegenspieler gilt weiterhin der normale Stich-Zwang.

  Szenario: Spielmacher geht nach vollständig ausgespielter Runde doppelt ab
    Angenommen eine regulär vollständig ausgespielte Runde mit Reizwert 220
    Und der Spielmacher hat 70 Meldepunkte und 140 Stichwerte einschließlich gedrückter Karten
    Wenn die Runde ausgewertet wird
    Dann ist der Rundenausgang "doppeltes Abgehen"
    Und der Spielmacher erreicht mit 210 Punkten den Reizwert nicht

  Szenario: Spielmacher erhält den negativen doppelten Reizwert als Verlustwert
    Angenommen der Rundenausgang ist "doppeltes Abgehen"
    Und der Reizwert des Spielmachers ist 200
    Wenn die Runde ausgewertet wird
    Dann wird beim Spielmacher der Verlustwert "-400" eingetragen
    Und die Meldepunkte des Spielmachers werden mit 0 gewertet
    Und die Stichwerte des Spielmachers werden mit 0 gewertet

  Szenario: Gegenspieler erhalten Stichwerte und jeweils 30 Mitpunkte
    Angenommen der Rundenausgang ist "doppeltes Abgehen"
    Und ein Gegenspieler hat 120 Stichwerte
    Wenn die Runde ausgewertet wird
    Dann werden die 120 Stichwerte des Gegenspielers gewertet
    Und jeder aktive Gegenspieler erhält 30 Mitpunkte

  Szenario: Meldepunkte der Gegenspieler unterliegen normalem Stich-Zwang
    Angenommen der Rundenausgang ist "doppeltes Abgehen"
    Und ein Gegenspieler hat 40 Meldepunkte
    Und der Gegenspieler hat 0 eigene Stiche
    Wenn die Runde ausgewertet wird
    Dann werden die Meldepunkte des Gegenspielers mit 0 gewertet

  Szenario: Verlustwert wird mit Minuszeichen und in Klammern dargestellt
    Angenommen der Rundenausgang ist "doppeltes Abgehen"
    Und der Reizwert des Spielmachers ist 200
    Wenn die Runde ausgewertet wird
    Dann wird der Verlustwert als "(-400)" in der Tabelle dargestellt