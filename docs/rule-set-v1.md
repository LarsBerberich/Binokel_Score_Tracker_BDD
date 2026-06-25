# V1-Regelwerk

## 1. Zweck und Geltungsbereich

Dieses Dokument beschreibt das verbindliche Regelwerk für Version 1 des Projekts **Binokel Score Tracker**.

Es legt fest,

- welche Spielvariante in V1 unterstützt wird,
- wie Runden fachlich bewertet werden,
- wie Punktestände geführt werden,
- welche Sonderfälle berücksichtigt werden,
- und welche Regeln ausdrücklich **nicht** Teil von V1 sind.

Dieses Dokument ist normativ für Fachmodell, Gherkin-Spezifikationen, Implementierung und UI-Verhalten.

---

## 2. Unterstützte Spielvariante in V1

V1 unterstützt ausschließlich die folgende Spielvariante:

- **4 Spieler**
- **Einzelwertung**
- **pro Runde ein aussetzender Geber**
- **3 aktive Spieler pro Runde**
- **feste Rundenzahl als Endkriterium**

Nicht Teil von V1 sind:

- Teamwertung,
- andere Spielerzahlen,
- Endbedingungen auf Basis von Zielwerten wie 1000 oder 1500,
- weitere noch nicht spezifizierte Regelvarianten.

---

## 3. Spielerreihenfolge und Geberrotation

### 3.1 Erfassung der Spieler

Die Spieler werden zu Beginn eines Spiels **einmalig in Sitzreihenfolge gegen den Uhrzeigersinn** erfasst.

Diese Reihenfolge ist fachlich relevant und bleibt über das gesamte Spiel unverändert bestehen.

Die Erfassung soll idealerweise beim **ersten Geber** beginnen.

### 3.2 Feste globale Spielerliste

Die Reihenfolge der Spieler wird in der Darstellung **nicht pro Runde umsortiert**.

Stattdessen gibt es eine feste globale Spielerliste, in der pro Runde nur markiert wird, welcher Spieler Geber ist.

### 3.3 Geberrotation

Der Geber rotiert **streng reihum** entlang der einmal festgelegten Spielerreihenfolge.

Da die Reihenfolge gegen den Uhrzeigersinn erfasst wird, erfolgt auch die Geberrotation in dieser Reihenfolge.

---

## 4. Rundenanzahl und Endbedingung

### 4.1 Rundenanzahl

Die Anzahl der Runden ist **frei wählbar**, muss aber immer ein **Vielfaches von 4** sein.

Zulässige Beispiele sind:

- 4
- 8
- 12
- 16

### 4.2 Standardwert

Wenn nicht anders vereinbart wurde, werden **12 Runden** gespielt.

Dies entspricht fachlich **3 Gesamtdurchgängen**, sodass jeder Spieler gleich oft Geber ist.

### 4.3 Endbedingung in V1

V1 unterstützt ausschließlich die Endbedingung **feste Rundenanzahl**.

Die in der Quelldokumentation beschriebenen Endvarianten

- Ausmachen ohne Spiel
- Ausmachen nur mit Spiel

sind **nicht Teil von V1** und können in späteren Ausbaustufen ergänzt werden.

---

## 5. Kartenwerte und Stichwert-Gesamtsumme

### 5.1 Kartenwerte

Für Stichwerte bzw. Augen gelten die folgenden Kartenwerte:

- Ass (Sau): 11 Punkte
- Zehner: 10 Punkte
- König: 4 Punkte
- Ober (Dame): 3 Punkte
- Unter (Bube): 2 Punkte
- letzter Stich: 10 Punkte zusätzlich für den Gewinner des letzten Stichs

### 5.2 Gesamtsumme regulärer Stichwerte

In einer regulär ausgespielten Runde gilt:

- die Summe aus allen durch Stiche gewonnenen Kartenaugen,
- zuzüglich der gedrückten Karten des Spielmachers,
- zuzüglich der 10 Punkte für den letzten Stich

ergibt insgesamt **genau 250 Punkte**.

Dies dient als fachliche Kontrollsumme.

---

## 6. Dapp und gedrückte Karten

### 6.1 Dapp

Der **Dapp** sind die 4 verdeckten Karten, um die gereizt wird.

Bei 40 Karten erhalten die 3 aktiven Spieler, also ohne Geber, zunächst zusammen 36 Karten. Die verbleibenden 4 Karten bilden den Dapp.

### 6.2 Spielmacher

Der Spieler, der das Reizen für sich entscheidet, ist der **Spielmacher**. Er nimmt den Dapp auf.

### 6.3 Gedrückte Karten

Da der Spielmacher dennoch nur mit 12 Karten spielt, muss er anschließend 4 Karten wieder ablegen. Diese Karten heißen **gedrückte Karten**.

### 6.4 Fachliche Abgrenzung

Dapp und gedrückte Karten stehen in fachlichem Zusammenhang, sind aber **nicht zwingend dieselben Karten**. Nur ihre Anzahl ist gleich.

Umgangssprachlich werden gedrückte Karten teilweise ebenfalls als Dapp bezeichnet, fachlich ist diese Gleichsetzung jedoch nicht korrekt.

### 6.5 Relevanz für die Wertung

Für die Rundenauswertung zählen die **gedrückten Karten** zum Stichwert des Spielmachers.

---

## 7. Fachlich relevante Wertarten

In V1 werden insbesondere die folgenden Wertarten unterschieden:

- Reizwert
- Meldepunkte
- Stichwerte bzw. Stichaugen
- Mitpunkte
- Verlustwert
- Punktestand
- Sterne bei Tausender-Runden

Dabei gilt:

- **Reizwerte** sind immer volle 10er-Werte
- **Mitpunkte** sind immer volle 10er-Werte
- **nur Stichwerte** können 1er-genaue Werte enthalten
- beim Spielmacher umfassen die Stichwerte auch die gedrückten Karten

---

## 8. Eingabe und Bedeutung der Stichwerte

### 8.1 Eingegebene Stichwerte

Die erfassten Stichwerte enthalten den Bonus für den letzten Stich bereits.

Die Spieler müssen diesen Bonus beim Auszählen ihrer Stiche selbst berücksichtigen.

### 8.2 Flexible Erfassung

Da die Gesamtsumme der regulären Stichwerte genau 250 beträgt, reicht es aus, wenn die exakten Stichwerte von **zwei der drei aktiven Spieler** vorliegen. Der fehlende dritte Wert kann dann automatisch berechnet werden.

Dies soll in der UI flexibel möglich sein, unabhängig davon, von welchen zwei Spielern die Werte zuerst erfasst wurden.

---

## 9. Rundung der Stichwerte

### 9.1 Grundregel

Nur die Stichwerte bzw. Stichaugen können 1er-genau sein.

Diese Werte werden bereits beim Eintragen auf volle 10 gerundet.

Die Speicherung darf im Standardfall ebenfalls bereits in dieser gerundeten Form erfolgen.

### 9.2 Geltungsbereich der Rundung

Die Rundung betrifft die Stichwerte,

- bei Gegenspielern auf Basis ihrer gewonnenen Stiche,
- beim Spielmacher auf Basis seiner gewonnenen Stiche einschließlich der gedrückten Karten.

### 9.3 Ausnahme bei möglichem Gleichstand am Spielende

In der letzten Runde müssen bei möglichem Gleichstand um den Gesamtsieg zusätzlich die exakten 1er-Werte berücksichtigt werden, damit eine punktgenaue Siegerermittlung möglich ist.

Nur wenn danach weiterhin Gleichstand besteht, gibt es mehrere Sieger.

---

## 10. Meldepunkte und Stich-Zwang

### 10.1 Grundregel

Ein aktiver Spieler muss mindestens **einen Stich** gewinnen, damit seine **Meldepunkte** zählen.

### 10.2 Normalfall

Hat ein aktiver Spieler mindestens einen Stich gewonnen, zählen seine Meldepunkte.

### 10.3 Kein eigener Stich

Hat ein aktiver Spieler keinen Stich gewonnen, verfallen seine Meldepunkte und werden für diese Runde mit 0 gewertet.

### 10.4 Geltung des Stich-Zwangs

Der Stich-Zwang gilt im Normalfall für **alle aktiven Spieler**, also auch für den Spielmacher.

Ausnahmen werden in den Regelungen zu den Verlustszenarien ausdrücklich benannt.

---

## 11. Rundenausgänge in V1

Eine Runde kann in V1 fachlich genau einen der folgenden Ausgänge haben:

- gewonnenes Spiel
- einfaches Abgehen
- doppeltes Abgehen
- Tausender gewonnen
- Tausender verloren

---

## 12. Gewonnenes normales Spiel

Ein normales Spiel ist gewonnen, wenn der Spielmacher nach regulärem Ausspielen seinen Reizwert erreicht oder überschreitet.

Für diese Prüfung zählt die Summe aus:

- Meldepunkten des Spielmachers
- exakten Stichwerten des Spielmachers einschließlich gedrückter Karten

Ist diese Summe **größer oder gleich dem Reizwert**, ist die Runde ein **gewonnenes Spiel**.

### 12.1 Stich-Zwang im gewonnenen Spiel

Der Stich-Zwang gilt in diesem Fall für **alle aktiven Spieler**, einschließlich des Spielmachers.

### 12.2 Wertung bei gewonnenem Spiel

- Der Spielmacher erhält seine tatsächlichen Punkte aus Meldepunkten und Stichwerten gutgeschrieben.
- Die Gegenspieler erhalten ihre tatsächlichen Punkte aus Meldepunkten und Stichwerten gutgeschrieben, sofern sie den Stich-Zwang erfüllen.
- Mitpunkte werden nicht vergeben.

---

## 13. Einfaches Abgehen

### 13.1 Definition

Einfaches Abgehen liegt vor, wenn der Spielmacher das Spiel **nach Sicht des Dapps und vor dem ersten Stich** aufgibt.

### 13.2 Wertung des Spielmachers

Beim Spielmacher gilt:

- eigene Meldepunkte verfallen vollständig
- Stichwerte sind 0
- Mitpunkte sind 0
- stattdessen wird der **negative einfache Reizwert** als Verlustwert eingetragen

### 13.3 Wertung der Gegenspieler

Für die Gegenspieler gilt:

- ihre Meldepunkte bleiben erhalten
- ihre Stichwerte sind 0
- sie erhalten zusätzlich **+30 Mitpunkte**

### 13.4 Ausnahme vom Stich-Zwang

Beim einfachen Abgehen entfällt der Stich-Zwang für die Gegenspieler.

Die Gegenspieler behalten ihre Meldepunkte daher auch dann, wenn sie keinen eigenen Stich gemacht haben.

---

## 14. Doppeltes Abgehen

### 14.1 Definition

Doppeltes Abgehen liegt vor, wenn

- kein einfaches Abgehen vorliegt,
- die Runde regulär ausgespielt wird,
- und der Spielmacher seinen Reizwert nicht erreicht.

Fachlich ist dies genau dann der Fall, wenn die Summe aus

- Meldepunkten des Spielmachers
- exakten Stichwerten des Spielmachers einschließlich gedrückter Karten

**kleiner** als der Reizwert ist.

### 14.2 Wertung des Spielmachers

Beim Spielmacher gilt:

- die im Spiel gemachten Stichwerte verfallen
- die eigenen Meldepunkte werden gestrichen
- stattdessen wird der **negative doppelte Reizwert** als Verlustwert eingetragen

### 14.3 Wertung der Gegenspieler

Für die Gegenspieler gilt:

- ihre Stichwerte zählen
- sie erhalten zusätzlich **+30 Mitpunkte**
- ihre Meldepunkte zählen **nur**, wenn sie den normalen Stich-Zwang erfüllen

### 14.4 Stich-Zwang beim doppelten Abgehen

Beim doppelten Abgehen gilt für die Gegenspieler weiterhin der normale Stich-Zwang.

Ein Gegenspieler mit 0 eigenen Stichen verliert daher seine Meldepunkte, kann aber dennoch seine Mitpunkte erhalten.

---

## 15. Tausender

### 15.1 Grundsatz

Der Tausender ist ein Sonderspiel und Teil von V1.

Er gehört jedoch **nicht** zur normalen Punktewertung.

### 15.2 Wertung beim Tausender

Bei einer Tausender-Runde gilt:

- keine Meldepunkte
- keine Stichwerte
- keine Mitpunkte
- der numerische Punktestand bleibt für alle Spieler unverändert

### 15.3 Sternvergabe

Statt numerischer Punkte werden Sterne vergeben:

- gewinnt der Spielmacher den Tausender, erhält **nur der Spielmacher** einen Stern
- verliert der Spielmacher den Tausender, erhalten die **beiden aktiven Gegenspieler** jeweils einen Stern

Der Geber erhält keinen Stern, da er an der Runde nicht aktiv beteiligt ist.

### 15.4 Speicherung und Darstellung der Sterne

Sterne sollen intern als numerischer Wert gespeichert werden.

In der UI dürfen sie symbolisch, zum Beispiel als `★`, dargestellt werden. Das verwendete Symbol kann später angepasst werden.

### 15.5 Ermittlung des Tausender-Ausgangs

Der Ausgang einer Tausender-Runde wird **nicht automatisch aus Punktwerten berechnet**.

Stattdessen wird bei angesagtem Tausender der Ausgang explizit ausgewählt:

- gewonnen
- verloren

Das System leitet daraus den fachlichen Rundenausgang und die Sternvergabe ab.

---

## 16. Automatische und manuelle Ermittlung des Rundenausgangs

### 16.1 Normale Runden

Bei normalen Runden soll das System den Rundenausgang automatisch ermitteln, sobald alle erforderlichen Werte vorliegen.

Automatisch ableitbar sind insbesondere:

- gewonnenes Spiel
- doppeltes Abgehen
- fehlender dritter Stichwert aus der 250-Punkte-Regel
- numerische Auswirkungen auf den Punktestand

### 16.2 Explizit zu erfassende Sonderfälle

Die folgenden Informationen werden nicht aus den normalen Punktwerten abgeleitet, sondern explizit erfasst:

- ob ein einfaches Abgehen vorliegt
- ob ein Tausender angesagt wurde
- ob ein angesagter Tausender gewonnen oder verloren wurde

---

## 17. Sieger des gesamten Spiels

Nach Abschluss aller Runden gewinnt der Spieler mit dem höchsten **numerischen Punktestand**.

Sterne aus Tausender-Runden beeinflussen die Siegerermittlung nicht. Sie sind reine Zusatzinformation.

### 17.1 Gleichstand

Grundsätzlich bleibt Gleichstand Gleichstand.

Mehrere Spieler können daher gemeinsam Sieger sein.

### 17.2 Punktgenaue Entscheidung in der letzten Runde

Da Stichwerte im Regelfall auf volle 10 gerundet werden, gilt für die letzte Runde:

Wenn um den Gesamtsieg ein Gleichstand möglich ist, müssen zusätzlich die exakten 1er-Werte berücksichtigt werden, um den Sieger punktgenau zu bestimmen.

Nur wenn danach weiterhin Gleichstand besteht, gibt es mehrere Sieger.

---

## 18. Darstellung in der Tabelle

### 18.1 Geber

In der Spalte des Gebers wird in der Rundenzeile ein **Strich** eingetragen.

Dies macht sichtbar, dass der Geber aussetzt und in dieser Runde weder Punkte noch Sterne erhält.

### 18.2 Verlustwerte

Negative Verlustwerte werden zur besseren Lesbarkeit mit **Minuszeichen und in Klammern** dargestellt.

Beispiele:

- `(-250)` für einfaches Abgehen bei Reizwert 250
- `(-400)` für doppeltes Abgehen bei Reizwert 200

Diese Darstellung dient der besseren Lesbarkeit der Tabelle. Fachlich handelt es sich um einen negativen Verlustwert.

### 18.3 STAND-Zeile

Der Punktestand wird in einer separaten **STAND-Zeile** als kumulierter Gesamtstand geführt.

---

## 19. Rechenregel für den Punktestand

### 19.1 Gewonnenes Spiel und reguläre Gegenspielerwertung

Wenn ein Spieler in einer Runde regulär Punkte erhält, berechnet sich der neue Punktestand als:

`Neuer STAND = Vorheriger STAND + Meldepunkte + Stichwerte + Mitpunkte`

### 19.2 Verlustszenarien des Spielmachers

Bei einfachem oder doppeltem Abgehen des Spielmachers berechnet sich der neue Punktestand des Spielmachers als:

`Neuer STAND = Vorheriger STAND + Verlustwert`

Der Verlustwert ist dabei bereits negativ.

### 19.3 Tausender

Beim Tausender bleibt der numerische Punktestand unverändert.

---

## 20. Verhältnis zu anderen Dokumenten

- `docs/ubiquitous-language.md` definiert die gemeinsame Fachsprache.
- `docs/language-conventions.md` beschreibt die Sprachkonventionen des Projekts.
- `docs/Anschreibetabelle_4_Spieler.md` enthält die tabellarische Herleitung und Beispiele.
- Dieses Dokument definiert das verbindliche **V1-Regelwerk** für Produkt, Modell und Implementierung.
