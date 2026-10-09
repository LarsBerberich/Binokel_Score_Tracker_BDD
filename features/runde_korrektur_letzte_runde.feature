# language: de
Funktionalität: Korrektur der letzten Runde
  Um Eingabefehler beim Anschreiben zu berichtigen
  möchte ich ausschließlich die zuletzt erfasste Runde nachträglich korrigieren können.

  Regelhintergrund (ADR-015, ADR-017):
  - Nur die höchste (zuletzt erfasste) Rundennummer ist editierbar (ADR-015).
  - Eine Korrektur aktualisiert den kumulierten STAND der Anschreibetabelle.
  - Der Geber wird deterministisch aus der Rundennummer abgeleitet, nicht neu gewählt.
  - Der Versuch, eine frühere Runde zu korrigieren, wird abgelehnt.
  - Bei 3 Spielern spielt der Geber mit und darf in der korrigierten Runde Spielmacher sein.

  Szenariogrundriss: Die letzte Runde wird korrigiert und der STAND aktualisiert
    Angenommen ein neues Spiel mit der Spielerreihenfolge "<spieler>" und <runden> Runden ist angelegt
    Und eine reguläre Runde ist für die Korrektur erfasst
    Wenn die letzte Runde mit einem höheren Spielmacher-Ergebnis korrigiert wird
    Dann wird die Korrektur übernommen
    Und der kumulierte STAND des Spielmachers beträgt 250

    Beispiele:
      | spieler                  | runden |
      | Anna, Bernd, Carla, Dirk | 4      |
      | Anna, Bernd, Carla       | 3      |

  Szenariogrundriss: Eine frühere Runde kann nicht mehr korrigiert werden
    Angenommen ein neues Spiel mit der Spielerreihenfolge "<spieler>" und <runden> Runden ist angelegt
    Und zwei reguläre Runden sind für die Korrektur erfasst
    Wenn versucht wird, die erste Runde zu korrigieren
    Dann wird die Korrektur abgelehnt

    Beispiele:
      | spieler                  | runden |
      | Anna, Bernd, Carla, Dirk | 4      |
      | Anna, Bernd, Carla       | 3      |
