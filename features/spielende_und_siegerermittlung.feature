# language: de
Funktionalität: Spielende und Siegerermittlung
  Um ein Spiel im V1-Regelrahmen korrekt abzuschließen
  möchte ich nach der letzten Runde den oder die Sieger bestimmen können.

  Regelhintergrund:
  - V1 verwendet eine feste Rundenzahl als Endbedingung.
  - Die Rundenzahl muss ein Vielfaches von 4 sein.
  - Wenn nichts anderes vereinbart wurde, werden 12 Runden gespielt.
  - Sieger ist, wer nach der letzten Runde den höchsten numerischen Punktestand hat.
  - Sterne aus Tausender-Runden beeinflussen den Gesamtsieg nicht.
  - Bei möglichem Gleichstand in der letzten Runde werden zusätzlich exakte 1er-Werte berücksichtigt.
  - Bleibt danach Gleichstand bestehen, gibt es mehrere Sieger.

  Szenario: Sieger nach höchstem numerischen Punktestand
    Gegeben die letzte Runde ist ausgewertet
    Und die Punktestände sind Anna 580, Bernd 620, Carla 610 und Dirk 540
    Wenn das Spiel abgeschlossen wird
    Dann ist Bernd alleiniger Sieger

  Szenario: Sterne aus Tausender-Runden beeinflussen den Gesamtsieg nicht
    Gegeben die letzte Runde ist ausgewertet
    Und Anna und Bernd haben denselben numerischen Punktestand
    Und Anna hat mehr Sterne aus Tausender-Runden als Bernd
    Wenn das Spiel abgeschlossen wird
    Dann wird der Gesamtsieg nicht über die Sterne entschieden

  Szenario: Exakte 1er-Werte entscheiden bei möglichem Gleichstand in der letzten Runde
    Gegeben in der letzten Runde ist ein Gleichstand um den Gesamtsieg möglich
    Und für die betroffenen Spieler liegen exakte 1er-Stichwerte vor
    Wenn das Spiel abgeschlossen wird
    Dann wird die Siegerermittlung mit den exakten 1er-Werten durchgeführt

  Szenario: Mehrere Sieger bei verbleibendem Gleichstand
    Gegeben die letzte Runde ist ausgewertet
    Und nach Berücksichtigung exakter 1er-Werte besteht weiterhin Gleichstand
    Wenn das Spiel abgeschlossen wird
    Dann gibt es mehrere Sieger
  