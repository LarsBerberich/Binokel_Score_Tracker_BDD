
# Regeln mit 4 Spielern, wenn der Geber jeweils aussetzt und technisch agnostischer Tabellenaufbau

## Binokel-Regelwerk und Abrechnungssystem
Variante: 4 Spieler (Geber setzt aus, 3 Spieler aktiv)
------------------------------
## 1. Kartenwerte, Meldebilder und Punktlimits
Gespielt wird mit 40 Karten (ohne 7er).
## 1.1 Kartenwerte (Stichpunkte / Augen)

* Ass (Sau): 11 Punkte
* Zehner: 10 Punkte
* König: 4 Punkte
* Ober (Dame): 3 Punkte
* Unter (Bube): 2 Punkte
* Letzter Stich: +10 Punkte für den Gewinner des Stichs.

## 1.2 Absolutes Punktlimit pro Runde
In jedem regulär ausgespielten Spiel gibt es ein mathematisch fixes Limit für die Stichpunkte:

* Stiche & gedrückte Karten: Zusammen genau 240 Punkte.
* Letzter Stich: 10 Punkte.
* Gesamtlimit: In einer Runde können von allen aktiven Spielern zusammen maximal 250 Stichpunkte erspielen. Dieses Limit dient als Kontrollsumme bei der Abrechnung.

## 1.3 Meldebilder und Punktwerte

* Paar (König + Ober in Fehlfarbe): 20 Punkte
* Trumpf-Paar (König + Ober in Trumpf): 40 Punkte
* Binokel (Karo-Unter + Pik-Ober): 40 Punkte
* 4 Unter / 4 Ober / 4 Könige / 4 Asse (je einer pro Farbe): 40 / 60 / 80 / 100 Punkte
* Familie (Ass, 10, König, Ober, Unter in Fehlfarbe): 100 Punkte
* Trumpf-Familie (Ass, 10, König, Ober, Unter in Trumpf): 150 Punkte
* Rundlauf (Familie in allen vier Farben): 240 Punkte
* Doppelter Binokel (2x Karo-Unter + 2x Pik-Ober): 300 Punkte
* Höchstbild: Alle 8 Karten eines Typs (z. B. alle 8 Asse): 1000 Punkte

------------------------------
## 2. Grundsatz: Stich-Zwang für Meldungen
Ein Spieler muss mindestens einen Stich gewinnen, damit seine Meldepunkte zählen.

* Normalfall: Hat ein Spieler ≥ 1 Stich, zählen seine Meldepunkte (M).
* Schneider-Fall: Hat ein Spieler 0 Stiche, verfallen seine Meldepunkte (Wert wird auf 0 gesetzt).
* Ausnahme (Abgehen des Spielmachers): Geht der Spielmacher einfach oder doppelt ab, entfällt der Stich-Zwang für die Gegner. Die Gegner behalten ihre Meldepunkte immer, auch bei 0 eigenen Stichen.

------------------------------
## 3. Endkriterien des Spiels
Vor dem Spiel wird eine der drei Optionen vereinbart:

* Option 1 (Ausmachen ohne Spiel): Das Spiel endet in der Runde, in der der erste aktive Spieler die Zielzahl (1000 oder 1500) erreicht oder überschreitet. Der aussetzende Geber kann nicht ausmachen.
* Option 2 (Ausmachen nur mit Spiel): Erreicht ein Spieler die Zielzahl, gewinnt er nur, wenn er in dieser Runde der erfolgreiche Spielmacher war. Andernfalls wird solange weitergespielt, bis ein Spieler über dem Limit liegt und das Spiel als Spielmacher gewinnt.
* Option 3 (Feste Rundenanzahl): Es wird eine feste, durch 4 teilbare Rundenanzahl gespielt (Default: 12 Runden). Es gewinnt der Spieler mit dem höchsten Endstand.

------------------------------
## 4. Abrechnungsszenarien## Szenario A: Spiel gewonnen
Der Spielmacher erreicht mit Meldung (M) und Stich (S) inklusive Dapp mindestens seinen Reizwert.

* Spielmacher: Schreibt seine tatsächlichen Punkte (M + S) gut.
* Gegner: Schreiben ihre Punkte (M + S) gut (sofern Stich-Zwang erfüllt).
* Mit-Punkte: Keine (0).

## Szenario B: Freiwilliges Abgehen (Einfaches Abgehen)
Der Spielmacher gibt das Spiel nach Sicht des Dapps vor dem ersten Stich verloren.

* Spielmacher: Die eigenen Meldepunkte verfallen komplett. Stich- und Mitpunkte sind 0. Stattdessen wird der einfache Reizwert als negativer Verlustwert in Klammern (z. B. (-250)) direkt in das erste Spaltenfeld eingetragen und vom Gesamtkonto abgezogen.
* Gegner: Behalten ihre Meldepunkte (M). Stichpunkte (S) sind 0. Erhalten zusätzlich +30 Punkte für das „Mit“.

## Szenario C: Im Spiel verloren (Doppeltes Abgehen)
Der Spielmacher spielt aus, erreicht seinen Reizwert aber nicht.

* Spielmacher: Die im Spiel gemachten Stichpunkte verfallen, die eigenen Meldepunkte werden gestrichen. Stattdessen wird der doppelte Reizwert als negativer Verlustwert in Klammern (z. B. (-400)) direkt in das erste Spaltenfeld eingetragen und vom Gesamtkonto abgezogen.
* Gegner: Schreiben ihre Meldepunkte (M) und Stichpunkte (S) gut. Erhalten zusätzlich +30 Punkte für das „Mit“.

## Sonderspiel: Der „Tausender“
Der Spielmacher sagt nach dem Dapp den „Tausender“ an.

* Wertung: Keine Meldepunkte, keine Stichpunkte, kein „Mit“. Der numerische STAND friert für alle Spieler ein.
* Abrechnung: Gewinnt der Spielmacher, erhält er einen Stern (★). Verliert er, erhalten die beiden aktiven Gegner jeweils einen Stern (★).

------------------------------
## 5. Tabellenstruktur (Agnostisch)
Jedes Spiel belegt zwei Zeilen: Die Rundenzeile zur getrennten Erfassung von M | S | Mit und die STAND-Zeile für den kumulierten Kontostand. Bei Spielverlust des Spielmachers entfallen dessen M- und S-Werte; an die Stelle des ersten Feldes rückt direkt der eingeklammerte Verlustwert.


| Runde | Geber | Gereizt bis | Wert | Spieler A | Spieler B | Spieler C | Spieler D |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| | | | | **M** \| **S** \| **Mit** | **M** \| **S** \| **Mit** | **M** \| **S** \| **Mit** | **M** \| **S** \| **Mit** |
| **1** | **A** | **180** / B <br>*(Gewonnen)* | Runde | *— (setzt aus)* | 100 \| 120 \| 0 | 40 \| 130 \| 0 | 40 \| 0 \| 0 *(0 Stiche)* |
| | | | **STAND** | *—* | **220** | **170** | **0** *(M gestrichen)* |
| **2** | **B** | **250** / C <br>**(A) - Einfach** | Runde | 40 \| 0 \| **30** | *— (setzt aus)* | **(-250)** \| 0 \| 0 | 20 \| 0 \| **30** |
| | | | **STAND** | **240** | **220** | **-80** | **50** *(M zählt)* |
| **3** | **C** | **Tausender** / D <br>*(Gewonnen)* | Runde | 0 \| 0 \| 0 | 0 \| 0 \| 0 | *— (setzt aus)* | **★** |
| | | | **STAND** | **240** | **220** | *—* | **50** |
| **4** | **D** | **200** / A <br>**(V) - Doppelt** | Runde | **(-400)** \| 0 \| 0 | 30 \| 250 \| **30** | 0 \| 0 \| 0 | *— (setzt aus)* |
| | | | **STAND** | **-160** | **530** *(M zählt)* | **-80** | *—* |

Rechenformel für die STAND-Zeile:

* Gewonnenes Spiel & alle Gegner:
$$\text{Neuer STAND} = \text{Vorheriger STAND} + M + S + \text{Mit}$$ 
* Verlierender Spielmacher (Szenario B & C):
$$\text{Neuer STAND} = \text{Vorheriger STAND} + \text{negativer Verlustwert in Klammern}$$ 







