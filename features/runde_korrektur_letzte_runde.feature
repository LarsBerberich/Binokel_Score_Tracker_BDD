# language: de
Funktionalität: Korrektur der letzten Runde
  Um Eingabefehler beim Anschreiben zu berichtigen
  möchte ich ausschließlich die zuletzt erfasste Runde nachträglich korrigieren können.

  Regelhintergrund:
  - Nur die höchste (zuletzt erfasste) Rundennummer ist editierbar (ADR-015).
  - Eine Korrektur aktualisiert den kumulierten STAND der Anschreibetabelle.
  - Der Geber wird deterministisch aus der Rundennummer abgeleitet, nicht neu gewählt.
  - Der Versuch, eine frühere Runde zu korrigieren, wird abgelehnt.

  Szenario: Die letzte Runde wird korrigiert und der STAND aktualisiert
    Angenommen ein neues Spiel mit einer erfassten Runde für die Korrektur ist angelegt
    Wenn die letzte Runde mit einem höheren Spielmacher-Ergebnis korrigiert wird
    Dann wird die Korrektur übernommen
    Und der kumulierte STAND des Spielmachers beträgt 250

  Szenario: Eine frühere Runde kann nicht mehr korrigiert werden
    Angenommen ein neues Spiel mit zwei erfassten Runden für die Korrektur ist angelegt
    Wenn versucht wird, die erste Runde zu korrigieren
    Dann wird die Korrektur abgelehnt
