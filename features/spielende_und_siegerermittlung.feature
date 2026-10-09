# language: de
Funktionalität: Spielende und Siegerermittlung
  Um ein Spiel im V1-Regelrahmen korrekt abzuschließen
  möchte ich nach der letzten Runde den oder die Sieger bestimmen können.

  Regelhintergrund:
  - V1 verwendet eine feste Rundenzahl als Endbedingung.
  - Die Rundenzahl muss ein Vielfaches der Spielerzahl sein (4 bzw. 3, ADR-017).
  - Wenn nichts anderes vereinbart wurde, werden 12 Runden gespielt.
  - Sieger ist, wer nach der letzten Runde den höchsten numerischen Punktestand hat.
  - Sterne aus Tausender-Runden beeinflussen den Gesamtsieg nicht.
  - Bei möglichem Gleichstand in der letzten Runde werden zusätzlich exakte 1er-Werte berücksichtigt.
  - Bleibt danach Gleichstand bestehen, gibt es mehrere Sieger.

  Szenario: Sieger nach höchstem numerischen Punktestand
    Angenommen die letzte Runde ist ausgewertet
    Und die Punktestände sind Anna 580, Bernd 620, Carla 610 und Dirk 540
    Wenn das Spiel abgeschlossen wird
    Dann ist Bernd alleiniger Sieger

  Szenario: Sterne aus Tausender-Runden beeinflussen den Gesamtsieg nicht
    Angenommen die letzte Runde ist ausgewertet
    Und Anna und Bernd haben denselben numerischen Punktestand
    Und Anna hat mehr Sterne aus Tausender-Runden als Bernd
    Wenn das Spiel abgeschlossen wird
    Dann wird der Gesamtsieg nicht über die Sterne entschieden

  Szenario: Exakte 1er-Werte entscheiden bei möglichem Gleichstand in der letzten Runde
    Angenommen in der letzten Runde ist ein Gleichstand um den Gesamtsieg möglich
    Und für die betroffenen Spieler liegen exakte 1er-Stichwerte vor
    Wenn das Spiel abgeschlossen wird
    Dann wird die Siegerermittlung mit den exakten 1er-Werten durchgeführt

  Szenario: Mehrere Sieger bei verbleibendem Gleichstand
    Angenommen die letzte Runde ist ausgewertet
    Und nach Berücksichtigung exakter 1er-Werte besteht weiterhin Gleichstand
    Wenn das Spiel abgeschlossen wird
    Dann gibt es mehrere Sieger

  Szenariogrundriss: Endrunden-Gleichstand in Zehnern wird per 1er-Tiebreak entschieden
    Angenommen ein neues Spiel mit der Spielerreihenfolge "<spieler>" und <runden> Runden ist angelegt
    Und die letzte Runde führt zu einem Gleichstand in Zehnern zwischen <gegenspieler_1> und <gegenspieler_2>
    Wenn der Sieger mit exakten 1er-Stichwerten <gegenspieler_1> 78 und <gegenspieler_2> 72 ermittelt wird
    Dann ist <gegenspieler_1> der alleinige Sieger des Spiels

    Beispiele:
      | spieler                  | runden | gegenspieler_1 | gegenspieler_2 |
      | Anna, Bernd, Carla, Dirk | 4      | Bernd          | Carla          |
      | Anna, Bernd, Carla       | 3      | Bernd          | Carla          |
  