# language: de
Funktionalität: Rollen einer Runde je nach Spielerzahl
  Um zu dritt und zu viert korrekt anzuschreiben
  möchte ich, dass die Rolle des Gebers von der Spielerzahl abhängt,
  sodass der Geber zu viert aussetzt und zu dritt wie jeder andere Spieler mitspielt.

  Regelhintergrund (rule-set §3.4, ADR-017):
  - Bei 4 Spielern setzt der Geber aus: keine Punkte, kein Stern, Rolle "geber".
  - Bei 3 Spielern spielt der Geber mit: Er ist Spielmacher oder Gegenspieler.
  - Die Gegenspieler sind die aktiven Spieler ohne den Spielmacher – immer genau zwei.
  - Die Wertung selbst ist in beiden Varianten identisch.

  Szenariogrundriss: Ein verlorener Tausender gibt den aktiven Gegenspielern je einen Stern
    Angenommen ein neues Spiel mit der Spielerreihenfolge "<spieler>" und <runden> Runden ist angelegt
    Wenn <spielmacher> bei Geber <geber> einen Tausender verliert
    Dann erhalten genau <sternempfaenger> je einen Stern

    Beispiele:
      | spieler                  | runden | spielmacher | geber | sternempfaenger |
      | Anna, Bernd, Carla, Dirk | 4      | Bernd       | Anna  | Carla, Dirk     |
      | Anna, Bernd, Carla       | 3      | Bernd       | Anna  | Anna, Carla     |
      | Anna, Bernd, Carla       | 3      | Anna        | Anna  | Bernd, Carla    |

  Szenariogrundriss: Die Rundenhistorie weist dem Geber seine Rolle zu
    Angenommen ein neues Spiel mit der Spielerreihenfolge "<spieler>" und <runden> Runden ist angelegt
    Wenn eine reguläre Runde mit Spielmacher <spielmacher> und Geber <geber> gespielt wird
    Dann hat <geber> in der Rundenhistorie die Rolle "<rolle>" und ist als Geber gekennzeichnet

    Beispiele:
      | spieler                  | runden | spielmacher | geber | rolle        |
      | Anna, Bernd, Carla, Dirk | 4      | Bernd       | Anna  | geber        |
      | Anna, Bernd, Carla       | 3      | Anna        | Anna  | spielmacher  |
      | Anna, Bernd, Carla       | 3      | Bernd       | Anna  | gegenspieler |

  Szenariogrundriss: Der Geber wird nur gewertet, wenn er mitspielt
    Angenommen ein neues Spiel mit der Spielerreihenfolge "<spieler>" und <runden> Runden ist angelegt
    Wenn eine reguläre Runde mit Spielmacher <spielmacher> und Geber <geber> gespielt wird
    Dann hat <geber> den Punktestand <punkte>

    Beispiele:
      | spieler                  | runden | spielmacher | geber | punkte |
      | Anna, Bernd, Carla, Dirk | 4      | Bernd       | Anna  | 0      |
      | Anna, Bernd, Carla       | 3      | Bernd       | Anna  | 90     |
      | Anna, Bernd, Carla       | 3      | Anna        | Anna  | 250    |
