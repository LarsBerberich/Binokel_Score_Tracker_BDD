# language: de
Funktionalität: Tausender auswerten
  Um das Sonderspiel Tausender korrekt zu behandeln
  möchte ich Tausender-Runden getrennt von normalen Runden auswerten.

  Regelhintergrund:
  - Der Tausender gehört nicht zur normalen Punktewertung.
  - Es werden keine Meldepunkte, keine Stichwerte und keine Mitpunkte gewertet.
  - Der numerische Punktestand bleibt unverändert.
  - Der Ausgang wird explizit als gewonnen oder verloren erfasst.
  - Bei Gewinn erhält der Spielmacher einen Stern.
  - Bei Verlust erhalten die beiden aktiven Gegenspieler jeweils einen Stern.
  - Der Geber erhält keinen Stern.

  Szenario: Tausender gewonnen
    Gegeben eine Runde ist als Tausender angesagt
    Und der Tausender-Ausgang ist "gewonnen"
    Wenn die Runde ausgewertet wird
    Dann erhält nur der Spielmacher einen Stern
    Und die aktiven Gegenspieler erhalten keinen Stern

  Szenario: Tausender verloren
    Gegeben eine Runde ist als Tausender angesagt
    Und der Tausender-Ausgang ist "verloren"
    Wenn die Runde ausgewertet wird
    Dann erhalten die beiden aktiven Gegenspieler jeweils einen Stern
    Und der Spielmacher erhält keinen Stern

  Szenario: Bei Tausender werden Meldepunkte, Stichwerte und Mitpunkte nicht erfasst
    Gegeben eine Runde ist als Tausender angesagt
    Wenn die Runde ausgewertet wird
    Dann werden keine Meldepunkte erfasst
    Und es werden keine Stichwerte erfasst
    Und es werden keine Mitpunkte erfasst

  Szenario: Numerischer Punktestand bleibt bei Tausender unverändert
    Gegeben eine Runde ist als Tausender angesagt
    Und der numerische Punktestand vor der Runde ist bekannt
    Wenn die Runde ausgewertet wird
    Dann bleibt der numerische Punktestand für alle Spieler unverändert
  