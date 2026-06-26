# language: de
Funktionalität: Spiel anlegen
  Um ein Binokel-Spiel im unterstützten V1-Regelrahmen zu beginnen
  möchte ich ein neues Spiel mit gültiger Spielerreihenfolge und gültiger Rundenzahl anlegen können.

  Regelhintergrund:
  - V1 unterstützt ausschließlich die 4-Spieler-Variante.
  - Die Spieler werden einmalig gegen den Uhrzeigersinn erfasst.
  - Die Reihenfolge bleibt über das gesamte Spiel konstant.
  - Der Geber rotiert später entlang genau dieser Reihenfolge.
  - Die Rundenzahl muss ein Vielfaches von 4 sein.
  - Wenn nichts anderes vereinbart wurde, werden 12 Runden gespielt.

  Szenario: Spiel mit 4 Spielern und Standardrundenzahl anlegen
    Gegeben es wird ein neues V1-Spiel angelegt
    Wenn die Spielerreihenfolge "Anna, Bernd, Carla, Dirk" gegen den Uhrzeigersinn erfasst wird
    Und keine abweichende Rundenzahl angegeben wird
    Dann wird das Spiel mit 12 Runden angelegt
    Und die Spielerreihenfolge bleibt als "Anna, Bernd, Carla, Dirk" gespeichert

  Szenario: Spiel mit gültiger Rundenzahl als Vielfaches von 4 anlegen
    Gegeben es wird ein neues V1-Spiel angelegt
    Wenn die Spielerreihenfolge "Anna, Bernd, Carla, Dirk" gegen den Uhrzeigersinn erfasst wird
    Und als Rundenzahl 16 angegeben wird
    Dann wird das Spiel mit 16 Runden angelegt

  Szenario: Spiel mit ungültiger Spielerzahl ablehnen
    Gegeben es wird ein neues V1-Spiel angelegt
    Wenn nur die Spieler "Anna, Bernd, Carla" erfasst werden
    Dann wird das Spiel nicht angelegt
    Und es wird ein Fehler zur ungültigen Spielerzahl angezeigt

  Szenario: Spiel mit ungültiger Rundenzahl ablehnen
    Gegeben es wird ein neues V1-Spiel angelegt
    Wenn die Spielerreihenfolge "Anna, Bernd, Carla, Dirk" gegen den Uhrzeigersinn erfasst wird
    Und als Rundenzahl 10 angegeben wird
    Dann wird das Spiel nicht angelegt
    Und es wird ein Fehler angezeigt, dass die Rundenzahl ein Vielfaches von 4 sein muss
