# language: de
Funktionalität: Einfaches Abgehen auswerten
  Um den Verlustfall vor dem ersten Stich korrekt abzurechnen
  möchte ich einfaches Abgehen als eigenen Rundenausgang behandeln.

  Regelhintergrund:
  - Einfaches Abgehen liegt vor, wenn der Spielmacher nach Sicht des Dapps und vor dem ersten Stich abgeht.
  - Der Spielmacher erhält den negativen einfachen Reizwert als Verlustwert.
  - Eigene Meldepunkte und Stichwerte des Spielmachers verfallen.
  - Die Gegenspieler behalten ihre Meldepunkte auch ohne eigenen Stich.
  - Die Gegenspieler erhalten jeweils +30 Mitpunkte.

  Szenario: Spielmacher geht vor dem ersten Stich einfach ab
    Gegeben der Spielmacher hat den Dapp gesehen
    Und es wurde noch kein Stich gespielt
    Wenn der Spielmacher einfach abgeht
    Dann ist der Rundenausgang "einfaches Abgehen"

  Szenario: Spielmacher erhält den negativen einfachen Reizwert als Verlustwert
    Gegeben der Rundenausgang ist "einfaches Abgehen"
    Und der Reizwert des Spielmachers ist 250
    Wenn die Runde ausgewertet wird
    Dann wird beim Spielmacher der Verlustwert "-250" eingetragen
    Und die Meldepunkte des Spielmachers werden mit 0 gewertet
    Und die Stichwerte des Spielmachers werden mit 0 gewertet

  Szenario: Gegenspieler behalten Meldepunkte ohne eigenen Stich
    Gegeben der Rundenausgang ist "einfaches Abgehen"
    Und ein Gegenspieler hat 40 Meldepunkte
    Und der Gegenspieler hat 0 eigene Stiche
    Wenn die Runde ausgewertet wird
    Dann werden die Meldepunkte des Gegenspielers gewertet

  Szenario: Gegenspieler erhalten jeweils 30 Mitpunkte
    Gegeben der Rundenausgang ist "einfaches Abgehen"
    Wenn die Runde ausgewertet wird
    Dann erhält jeder aktive Gegenspieler 30 Mitpunkte

  Szenario: Verlustwert wird mit Minuszeichen und in Klammern dargestellt
    Gegeben der Rundenausgang ist "einfaches Abgehen"
    Und der Reizwert des Spielmachers ist 250
    Wenn die Runde ausgewertet wird
    Dann wird der Verlustwert als "(-250)" in der Tabelle dargestellt