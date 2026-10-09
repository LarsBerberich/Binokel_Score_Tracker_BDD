# language: de
Funktionalität: Tausender laufen außer Konkurrenz
  Um die Spielrunden korrekt zu zählen
  möchte ich, dass ein Tausender nicht als gespielte Runde zählt,
  sodass Rundenzähler und Geber erst durch eine reguläre Runde weiterrücken.

  Regelhintergrund (rule-set §15, FND-006, ADR-017):
  - Ein Tausender wird als eigene Runde mit eindeutiger Sequenz gespeichert.
  - Er zählt nicht als gespielte Runde: die gezählte Spielrunde bleibt stehen.
  - Der numerische Punktestand friert bei einem Tausender ein.
  - Das gilt unverändert für 4 Spieler (Geber setzt aus) und 3 Spieler (Geber spielt mit).

  Szenariogrundriss: Ein Tausender erhöht die gezählte Spielrunde nicht
    Angenommen ein neues Spiel mit der Spielerreihenfolge "<spieler>" und <runden> Runden ist angelegt
    Und die erste reguläre Runde ist gespielt
    Wenn in derselben gezählten Runde ein Tausender ausgewertet wird
    Dann trägt die Tausender-Runde keine gezählte Rundennummer
    Und der numerische Punktestand ändert sich durch den Tausender nicht
    Und die gezählte Rundennummer rückt erst durch die nächste reguläre Runde weiter

    Beispiele:
      | spieler                  | runden |
      | Anna, Bernd, Carla, Dirk | 4      |
      | Anna, Bernd, Carla       | 3      |
