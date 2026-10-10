# language: de
Funktionalität: Abrechnung bei Spielende
  Um zu wissen, was am Ende des Spiels zu zahlen wäre
  möchte ich zu jedem Zeitpunkt sehen, wie viel jeder Spieler zahlen müsste,
  wenn das Spiel jetzt zu Ende wäre.

  Regelhintergrund (rule-set §20):
  - Basis ist der Spieler mit dem höchsten numerischen Punktestand.
  - Jeder Spieler zahlt 5 Cent je 10 Punkte Differenz zum Höchststand.
  - Der Spitzenreiter zahlt nichts; bei Gleichstand an der Spitze zahlen alle Spitzenreiter nichts.
  - Sterne aus Tausender-Runden fließen nicht ein.
  - Die Abrechnung ist eine reine Anzeige und verändert den Punktestand nicht.
  - Sie gilt unverändert für 3 und 4 Spieler.

  Szenariogrundriss: Der Spitzenreiter zahlt nichts, alle anderen 5 Cent je 10 Punkte Differenz
    Angenommen ein neues Spiel mit der Spielerreihenfolge "<spieler>" und <runden> Runden ist angelegt
    Wenn eine reguläre Runde mit Spielmacher <spielmacher> und Geber <geber> gespielt wird
    Dann zahlen die Spieler "<erwartet>"

    Beispiele:
      | spieler                  | runden | spielmacher | geber | erwartet                                                    |
      | Anna, Bernd, Carla, Dirk | 4      | Bernd       | Anna  | Anna 1,25 €; Bernd 0,00 €; Carla 0,80 €; Dirk 0,95 €       |
      | Anna, Bernd, Carla       | 3      | Bernd       | Anna  | Anna 0,80 €; Bernd 0,00 €; Carla 0,95 €                     |
      | Anna, Bernd, Carla       | 3      | Anna        | Anna  | Anna 0,00 €; Bernd 0,80 €; Carla 0,95 €                     |

  Szenariogrundriss: Zu Spielbeginn zahlt niemand etwas
    Angenommen ein neues Spiel mit der Spielerreihenfolge "<spieler>" und <runden> Runden ist angelegt
    Dann zahlen die Spieler "<erwartet>"

    Beispiele:
      | spieler                  | runden | erwartet                                                |
      | Anna, Bernd, Carla, Dirk | 4      | Anna 0,00 €; Bernd 0,00 €; Carla 0,00 €; Dirk 0,00 €    |
      | Anna, Bernd, Carla       | 3      | Anna 0,00 €; Bernd 0,00 €; Carla 0,00 €                 |

  Szenariogrundriss: Bei Gleichstand an der Spitze zahlen alle Spitzenreiter nichts
    Angenommen ein neues Spiel mit der Spielerreihenfolge "<spieler>" und <runden> Runden ist angelegt
    Wenn <spielmacher> bei Geber <geber> einfach abgeht und die Gegenspieler je 40 Meldepunkte haben
    Dann zahlen die Spieler "<erwartet>"

    Beispiele:
      | spieler                  | runden | spielmacher | geber | erwartet                                                    |
      | Anna, Bernd, Carla, Dirk | 4      | Bernd       | Anna  | Anna 0,35 €; Bernd 1,10 €; Carla 0,00 €; Dirk 0,00 €       |
      | Anna, Bernd, Carla       | 3      | Bernd       | Anna  | Anna 0,00 €; Bernd 1,10 €; Carla 0,00 €                    |

  Szenariogrundriss: Ein Tausender ändert die Abrechnung nicht
    Angenommen ein neues Spiel mit der Spielerreihenfolge "<spieler>" und <runden> Runden ist angelegt
    Wenn <spielmacher> bei Geber <geber> einen Tausender verliert
    Dann zahlen die Spieler "<erwartet>"

    Beispiele:
      | spieler                  | runden | spielmacher | geber | erwartet                                                |
      | Anna, Bernd, Carla, Dirk | 4      | Bernd       | Anna  | Anna 0,00 €; Bernd 0,00 €; Carla 0,00 €; Dirk 0,00 €    |
      | Anna, Bernd, Carla       | 3      | Bernd       | Anna  | Anna 0,00 €; Bernd 0,00 €; Carla 0,00 €                 |
