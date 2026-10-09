# language: de
Funktionalität: Spiel anlegen
  Um ein Binokel-Spiel im unterstützten V1-Regelrahmen zu beginnen
  möchte ich ein neues Spiel mit gültiger Spielerreihenfolge und gültiger Rundenzahl anlegen können.

  Regelhintergrund (ADR-017):
  - V1 unterstützt die 4-Spieler-Variante (Geber setzt aus) und die 3-Spieler-Variante (Geber spielt mit).
  - Die Variante ergibt sich aus der Anzahl der erfassten Spieler.
  - Die Spieler werden einmalig gegen den Uhrzeigersinn erfasst.
  - Die Reihenfolge bleibt über das gesamte Spiel konstant.
  - Der Geber rotiert später entlang genau dieser Reihenfolge.
  - Die Rundenzahl muss ein Vielfaches der Spielerzahl sein (4 bzw. 3).
  - Wenn nichts anderes vereinbart wurde, werden 12 Runden gespielt (gültig für beide Varianten).

  Szenariogrundriss: Spiel mit gültiger Spielerzahl und Standardrundenzahl anlegen
    Angenommen es wird ein neues V1-Spiel angelegt
    Wenn die Spielerreihenfolge "<spieler>" gegen den Uhrzeigersinn erfasst wird
    Und keine abweichende Rundenzahl angegeben wird
    Dann wird das Spiel mit 12 Runden angelegt
    Und die Spielerreihenfolge bleibt als "<spieler>" gespeichert

    Beispiele:
      | spieler                  |
      | Anna, Bernd, Carla, Dirk |
      | Anna, Bernd, Carla       |

  Szenariogrundriss: Spiel mit gültiger Rundenzahl als Vielfaches der Spielerzahl anlegen
    Angenommen es wird ein neues V1-Spiel angelegt
    Wenn die Spielerreihenfolge "<spieler>" gegen den Uhrzeigersinn erfasst wird
    Und als Rundenzahl <runden> angegeben wird
    Dann wird das Spiel mit <runden> Runden angelegt

    Beispiele:
      | spieler                  | runden |
      | Anna, Bernd, Carla, Dirk | 4      |
      | Anna, Bernd, Carla, Dirk | 16     |
      | Anna, Bernd, Carla       | 3      |
      | Anna, Bernd, Carla       | 9      |
      | Anna, Bernd, Carla       | 15     |

  Szenariogrundriss: Spiel mit ungültiger Spielerzahl ablehnen
    Angenommen es wird ein neues V1-Spiel angelegt
    Wenn nur die Spieler "<spieler>" erfasst werden
    Dann wird das Spiel nicht angelegt
    Und es wird ein Fehler zur ungültigen Spielerzahl angezeigt

    Beispiele:
      | spieler                        |
      | Anna, Bernd                    |
      | Anna, Bernd, Carla, Dirk, Emil |

  Szenariogrundriss: Spiel mit Rundenzahl, die kein Vielfaches der Spielerzahl ist, ablehnen
    Angenommen es wird ein neues V1-Spiel angelegt
    Wenn die Spielerreihenfolge "<spieler>" gegen den Uhrzeigersinn erfasst wird
    Und als Rundenzahl <runden> angegeben wird
    Dann wird das Spiel nicht angelegt
    Und es wird ein Fehler angezeigt, dass die Rundenzahl ein Vielfaches von <teiler> sein muss

    Beispiele:
      | spieler                  | runden | teiler |
      | Anna, Bernd, Carla, Dirk | 10     | 4      |
      | Anna, Bernd, Carla, Dirk | 6      | 4      |
      | Anna, Bernd, Carla       | 4      | 3      |
      | Anna, Bernd, Carla       | 10     | 3      |

  Szenariogrundriss: Geber rotiert streng reihum entlang der festgelegten Spielerreihenfolge
    Angenommen das Spiel wurde mit der Spielerreihenfolge "<spieler>" angelegt
    Dann ist <geber_runde_1> Geber in Runde 1
    Und <geber_runde_2> ist Geber in Runde 2
    Und <geber_runde_3> ist Geber in Runde 3
    Und <geber_runde_4> ist Geber in Runde 4
    Und <geber_runde_5> ist Geber in Runde 5

    Beispiele:
      | spieler                  | geber_runde_1 | geber_runde_2 | geber_runde_3 | geber_runde_4 | geber_runde_5 |
      | Anna, Bernd, Carla, Dirk | Anna          | Bernd         | Carla         | Dirk          | Anna          |
      | Anna, Bernd, Carla       | Anna          | Bernd         | Carla         | Anna          | Bernd         |

  Szenariogrundriss: Aktive Spieler einer Runde hängen von der Spielerzahl ab
    Angenommen das Spiel wurde mit der Spielerreihenfolge "<spieler>" angelegt
    Dann spielen in Runde 1 "<aktive>" aktiv mit
    Und der Geber in Runde 1 <setzt_aus_oder_spielt_mit>

    Beispiele:
      | spieler                  | aktive             | setzt_aus_oder_spielt_mit |
      | Anna, Bernd, Carla, Dirk | Bernd, Carla, Dirk | setzt aus                 |
      | Anna, Bernd, Carla       | Anna, Bernd, Carla | spielt mit                |
