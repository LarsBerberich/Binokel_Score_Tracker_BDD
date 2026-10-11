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

V1 unterstützt zwei Spielvarianten, die sich **ausschließlich** in der Rolle des Gebers
und in der zulässigen Rundenzahl unterscheiden (ADR-017). Die Variante ergibt sich aus der
Anzahl der beim Anlegen erfassten Spieler — es gibt keine separate Auswahl.

| | **4 Spieler** | **3 Spieler** |
|---|---|---|
| Wertung | Einzelwertung | Einzelwertung |
| Geber | **setzt aus** | **spielt mit** |
| Aktive Spieler pro Runde | 3 (alle außer dem Geber) | 3 (alle) |
| Rundenzahl | Vielfaches von **4** | Vielfaches von **3** |
| Endkriterium | feste Rundenzahl | feste Rundenzahl |

In beiden Varianten spielen pro Runde **genau 3 Spieler aktiv**. Die gesamte Wertung (Reizwert,
Meldepunkte, Stichwerte, Mitpunkte, Stich-Zwang, 250er-Kontrollsumme, Tausender) ist daher in
beiden Varianten identisch; nur die Frage, *wer* aktiv ist, hängt von der Spielerzahl ab (§3.4).

Nicht Teil von V1 sind:

- Teamwertung,
- andere Spielerzahlen als 3 oder 4,
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

Die Rotationsformel ist in beiden Varianten dieselbe (Geber in Runde *n* = Spieler an Position
`(n − 1) mod Spielerzahl`); nur die Länge eines Durchgangs ändert sich (3 bzw. 4 Runden).

### 3.4 Aktive Spieler einer Runde

Wer in einer Runde aktiv mitspielt, hängt von der Spielerzahl ab:

- **4 Spieler:** Der Geber **setzt aus**. Aktiv sind die drei übrigen Spieler. Der Spielmacher
  darf nie der Geber sein.
- **3 Spieler:** Der Geber **spielt mit**. Alle drei Spieler sind aktiv; der Geber kann
  Spielmacher oder Gegenspieler sein.

Die **Gegenspieler** sind in beiden Varianten die aktiven Spieler ohne den Spielmacher — also
immer genau zwei.

---

## 4. Rundenanzahl und Endbedingung

### 4.1 Rundenanzahl

Die Anzahl der Runden ist **frei wählbar**, muss aber immer ein **Vielfaches der Spielerzahl**
sein, damit jeder Spieler gleich oft Geber ist:

- **4 Spieler:** Vielfaches von 4 — zulässig sind z. B. 4, 8, 12, 16.
- **3 Spieler:** Vielfaches von 3 — zulässig sind z. B. 3, 6, 9, 12, 15.

### 4.2 Standardwert

Wenn nicht anders vereinbart wurde, werden **12 Runden** gespielt. 12 ist ein Vielfaches von
3 **und** von 4 und deshalb für beide Varianten gültig.

Dies entspricht fachlich **3 Gesamtdurchgängen bei 4 Spielern** bzw. **4 Gesamtdurchgängen bei
3 Spielern**, sodass jeder Spieler gleich oft Geber ist.

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

### 5.2 Blatt und Konsequenz für Stiche (württembergisches Blatt)

V1 wird mit dem **württembergischen Blatt** gespielt: Es enthält nur **Siebener** (keine Achter oder Neuner), und die **Siebener werden vor dem Spiel aussortiert**, weil sie für das Spiel irrelevant sind. Gespielt wird also **ohne Siebener**.

Daraus folgt: Es gibt **keine 0-Augen-Karte**. Die niedrigstwertige Karte im Spiel ist der Unter (2 Punkte). Jeder gewonnene Stich enthält daher zwangsläufig Augen — der **kleinstmögliche Stich beträgt 6 Punkte** (drei Unter). Ein „Nuller-Stich" (ein realer Stich mit 0 Augen) ist damit **ausgeschlossen**.

Diese Eigenschaft ist die fachliche Grundlage dafür, dass „hat mindestens einen eigenen Stich" (§10) zuverlässig aus einem **Stichwert > 0** abgeleitet werden kann (siehe §10.3).

### 5.3 Gesamtsumme regulärer Stichwerte

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

Bei 40 Karten erhalten die 3 aktiven Spieler zunächst zusammen 36 Karten (bei 4 Spielern ohne den aussetzenden Geber, bei 3 Spielern alle Spieler). Die verbleibenden 4 Karten bilden den Dapp.

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
- **Reizwerte** starten bei einem Minimum von **150** (Hausregel; entspricht gängiger Turnierpraxis) und werden im Erfassungs-UI mit 150 vorbelegt
- **Mitpunkte** sind immer volle 10er-Werte
- **Stichwerte** werden für den STAND ebenfalls in vollen 10er-Werten erfasst (Zehner-Eingabe, §9.1); 1er-genaue Stichwerte gibt es nur in der letzten Runde für den Gleichstand-Tiebreak (§9.4)
- beim Spielmacher umfassen die Stichwerte auch die gedrückten Karten

### 7.1 Plausibilitätsgrenze der Meldepunkte

Die **Meldepunkte eines einzelnen Spielers** können einen fachlich begründeten Höchstwert nicht überschreiten. In V1 gilt als obere Plausibilitätsgrenze:

> **Meldepunkte ≤ 1800** je Spieler und Runde. Negative Meldepunkte sind ebenfalls unzulässig (Untergrenze 0).

Herleitung des theoretischen Maximums (württembergisches Doppelblatt, vgl. §5.1/§5.2):

- **Doppelte Familie** einer Farbe (alle zehn Karten einer Farbe außer den beiden Siebenern) = **1500 Punkte**
- zusätzlich **doppelter Binokel** (zwei Schellen-Unter + zwei Blatt-Ober) = **300 Punkte**; die beiden Blatt-Ober sind bereits Teil der doppelten Familie in Blatt und dürfen zugleich für den Binokel gewertet werden (eine Karte darf mehrfach für Meldungen verwendet werden)

Daraus ergibt sich die Summe **1500 + 300 = 1800**.

Diese Grenze dient als **Eingabe-Plausibilitätsprüfung** (Schutz vor Tippfehlern, z. B. 1300 statt 130) und wird sowohl im Erfassungs-UI (Absenden gesperrt) als auch serverseitig bei der Rundenerfassung durchgesetzt. Ein höherer oder negativer Wert wird abgelehnt.

---

## 8. Eingabe und Bedeutung der Stichwerte

### 8.1 Eingegebene Stichwerte

Die erfassten Stichwerte enthalten den Bonus für den letzten Stich bereits.

Die Spieler müssen diesen Bonus beim Auszählen ihrer Stiche selbst berücksichtigen.

### 8.2 Flexible Erfassung

Da die Gesamtsumme der regulären Stichwerte genau 250 beträgt, reicht es aus, wenn die exakten Stichwerte von **zwei der drei aktiven Spieler** vorliegen. Der fehlende dritte Wert kann dann automatisch berechnet werden.

Dies soll in der UI flexibel möglich sein, unabhängig davon, von welchen zwei Spielern die Werte zuerst erfasst wurden.

---

## 9. Erfassung der Stichwerte und STAND-Rundung

### 9.1 Grundregel — Zehner-Eingabe

Normale Runden werden in **vollen Zehnern** erfasst (Eingabeschritt 10). Alle Werte,
die in den kumulierten **STAND** (Zwischen- und Endstand) einfließen — Stichwerte,
Meldepunkte und Reizwert —, sind stets Vielfache von 10.

Damit wird der STAND ausschließlich in Zehnern geführt und zeigt nie eine Einerstelle
(vgl. Anschreibetabelle §5, alle STAND-Werte auf Zehner). Der Spieler rundet Grenzfälle
bereits **bei der Eingabe** sauber auf Zehner (z. B. real 95/95/60 → 100/90/60), sodass
die 250er-Kontrollsumme (§5.3) trivial auf Zehnern gilt und nie überschritten wird.

Die Zehner-Eingabe wird erzwungen: Das Erfassungs-UI sperrt das Absenden bei einem Wert,
der kein Vielfaches von 10 ist (Modulo-10-Prüfung), und die API weist solche Werte im
Rundentyp `normal` und `doppeltes_abgehen` mit HTTP 400 ab.

### 9.2 Geltungsbereich

Die Zehner-Eingabe betrifft die Stichwerte,

- bei Gegenspielern auf Basis ihrer gewonnenen Stiche,
- beim Spielmacher auf Basis seiner gewonnenen Stiche einschließlich der gedrückten Karten,

sowie Meldepunkte und Reizwert. Der automatisch berechnete dritte Stichwert
(`250 − w1 − w2`, §8.2) ergibt sich aus zwei Zehner-Werten und ist daher selbst ein Zehner.

### 9.3 Ausnahme bei möglichem Gleichstand am Spielende

In der letzten Runde werden bei möglichem Gleichstand um den Gesamtsieg zusätzlich die
**exakten 1er-Werte** der Stiche berücksichtigt, damit eine punktgenaue Siegerermittlung
möglich ist. Der Tiebreak wirkt über die **aktiven Spieler der letzten Runde**. Bei 4 Spielern bringt der in der
letzten Runde aussetzende Geber keinen Endrunden-Stich ein und nimmt am 1er-Tiebreak
nicht teil; bei 3 Spielern sind alle Spieler aktiv und damit tiebreak-fähig.

Nur wenn danach weiterhin Gleichstand besteht, gibt es mehrere Sieger.

### 9.4 1er-Werte nur für den Endrunden-Tiebreak

Die 1er-genauen Stichwerte werden **ausschließlich in der letzten Runde** und **ausschließlich
für den Gleichstand-Tiebreak** (§9.3) erfasst. Sie fließen **nicht** in den STAND ein: Der STAND
bleibt in Zehnern, die 1er-Werte entscheiden nur bei einem Gleichstand in Zehnern über den
Einzelsieger.

Technisch werden die 1er-Werte der letzten Runde vom Erfassungs-UI getrennt von den
Zehner-Stichfeldern aufgenommen und bei der Siegerermittlung als Tiebreak-Kriterium
(`?exakte_stichwerte=Name:Wert,…`) übergeben.

---

## 10. Meldepunkte und Stich-Zwang

### 10.1 Grundregel

Ein aktiver Spieler muss mindestens **einen Stich** gewinnen, damit seine **Meldepunkte** zählen.

### 10.2 Normalfall

Hat ein aktiver Spieler mindestens einen Stich gewonnen, zählen seine Meldepunkte.

### 10.3 Kein eigener Stich

Hat ein aktiver Spieler keinen Stich gewonnen, verfallen seine Meldepunkte und werden für diese Runde mit 0 gewertet.

**Ableitung im Erfassungs-UI:** „Hat einen eigenen Stich" wird nicht separat erfasst, sondern aus dem erfassten **Stichwert > 0** abgeleitet. Das ist fachlich zulässig, weil es im württembergischen Blatt ohne Siebener keinen 0-Augen-Stich gibt (§5.2): Ein Stichwert von 0 bedeutet zwingend „kein Stich", jeder reale Stich ergibt mindestens 6 Augen.

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

Bei 4 Spielern erhält der aussetzende Geber keinen Stern, da er an der Runde nicht aktiv beteiligt
ist. Bei 3 Spielern spielt der Geber mit: Ist er Spielmacher, gilt die Regel für den Spielmacher;
ist er Gegenspieler, erhält er bei verlorenem Tausender einen Stern.

### 15.4 Speicherung und Darstellung der Sterne

Sterne sollen intern als numerischer Wert gespeichert werden.

In der UI dürfen sie symbolisch, zum Beispiel als `★`, dargestellt werden. Das verwendete Symbol kann später angepasst werden.

### 15.5 Ermittlung des Tausender-Ausgangs

Der Ausgang einer Tausender-Runde wird **nicht automatisch aus Punktwerten berechnet**.

Stattdessen wird bei angesagtem Tausender der Ausgang explizit ausgewählt:

- gewonnen
- verloren

### 15.6 Tausender läuft außer Konkurrenz (Rundenzählung)

Ein Tausender **zählt nicht als gespielte Runde**. Er läuft außer Konkurrenz:

- Die **gezählte Spielrunde** (Runde X von Y) erhöht sich durch einen Tausender **nicht**.
- Der **Geber wechselt nicht**: die anschließend zu spielende Runde wird mit
  **demselben Geber** und derselben gezählten Spielrunde erneut gespielt.
- Es wird so lange erneut gespielt, **bis kein Tausender mehr** angesagt wird. Erst
  eine reguläre Runde (gewonnenes Spiel, einfaches oder doppeltes Abgehen) rückt
  Zähler **und** Geber weiter.
- Das **Spielende** richtet sich ausschließlich nach der Anzahl **gezählter** Runden;
  Tausender-Runden werden dabei nicht mitgezählt.
- Die Tausender-Sterne (§15.3) bleiben erhalten und werden weiterhin angezeigt.

Zur Nachvollziehbarkeit wird jede erfasste Runde – auch ein Tausender – als eigene
Runde mit einer eindeutigen fortlaufenden **Erfassungs-Sequenz** gespeichert und ist
im Rahmen der Korrektur der letzten Runde (§17 / ADR-015) editierbar. In der
Anschreibetabelle erscheint eine Tausender-Zeile mit `★` und der Kennzeichnung
**„außer Konkurrenz"** ohne gezählte Rundennummer (vgl. docs/Anschreibetabelle_3_und_4_Spieler.md).

> Herleitung: siehe FND-006 (docs/testing/explorative-testprotokoll.md) und ADR-016.


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

Da der STAND in vollen Zehnern geführt wird (§9.1), kann in der letzten Runde ein Gleichstand in Zehnern auftreten. Dann gilt:

Wenn um den Gesamtsieg ein Gleichstand möglich ist, werden zusätzlich die exakten 1er-Werte der Stiche berücksichtigt, um den Sieger punktgenau zu bestimmen. Das Erfassungs-UI bietet dafür in der letzten Runde separate, optionale 1er-Felder je aktivem Spieler an (§9.4); die Zehner-Stichfelder bleiben für den STAND unverändert.

Nur wenn danach weiterhin Gleichstand besteht, gibt es mehrere Sieger.

---

## 18. Darstellung in der Tabelle

### 18.1 Geber

**Nur bei 4 Spielern** wird in der Spalte des Gebers in der Rundenzeile ein **Strich** eingetragen.

Dies macht sichtbar, dass der Geber aussetzt und in dieser Runde weder Punkte noch Sterne erhält.
Bei 3 Spielern spielt der Geber mit und trägt wie jeder andere aktive Spieler seine Werte ein; er
ist dort lediglich über die Spalte „Geber" erkennbar.

### 18.2 Verlustwerte

Negative Verlustwerte werden zur besseren Lesbarkeit mit **Minuszeichen und in Klammern** dargestellt.

Beispiele:

- `(-250)` für einfaches Abgehen bei Reizwert 250
- `(-400)` für doppeltes Abgehen bei Reizwert 200

Diese Darstellung dient der besseren Lesbarkeit der Tabelle. Fachlich handelt es sich um einen negativen Verlustwert.

### 18.3 STAND-Zeile

Der Punktestand wird in einer separaten **STAND-Zeile** als kumulierter Gesamtstand geführt.

### 18.4 Sternesumme in der Endabrechnung

In der **Endabrechnung** zeigt die Anschreibetabelle unter der letzten STAND-Zeile eine Zeile
**„Sterne (Summe)"** mit den aufsummierten Tausender-Sternen je Spieler (§15). Sie steht **zwischen**
der STAND-Zeile und der Abrechnung (§20).

- Die Zeile erscheint **nur, wenn mindestens ein Tausender gespielt wurde**; sonst entfällt sie ganz.
- Sie erscheint **nur in der Endabrechnung**, nicht im laufenden Spiel.
- Ein Spieler ohne Sterne bekommt eine leere Zelle; Sterne werden als ★ je Stern dargestellt.
- Sterne beeinflussen weder Punktestand noch Sieger noch Abrechnung (§15.3, §17, §20.2).

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

## 20. Abrechnung (Einsatz pro Punkt)

### 20.1 Zweck

Die Abrechnung zeigt zu jedem Zeitpunkt, **wie viel jeder Spieler zahlen müsste, wenn das Spiel
jetzt zu Ende wäre**. Sie ist eine rein abgeleitete Anzeige: Sie verändert weder den Punktestand
noch die Siegerermittlung.

### 20.2 Berechnung

- **Basis** ist der Spieler mit dem höchsten numerischen Punktestand (STAND).
- Der **Betrag** je Spieler ist **5 Cent je 10 Punkte** Differenz zum höchsten STAND, also
  `(höchster STAND − eigener STAND) / 10 × 5 Cent`.
- Der Spitzenreiter zahlt **0,00 €**. Bei Gleichstand an der Spitze zahlen **alle** Spitzenreiter 0,00 €.
- Maßgeblich ist ausschließlich der numerische STAND; **Sterne** aus Tausender-Runden (§15) fließen
  nicht ein.
- Gerechnet wird in **ganzen Cent**, sodass kein Rundungsfehler entsteht. Da der STAND in Zehnern
  geführt wird (§9.1), ist die Differenz ein Vielfaches von 10 und jeder Betrag ein Vielfaches von
  5 Cent – ohne Rundung. Nur bei Altbestand mit Einerstellen (vor der Zehner-Regel) wird
  kaufmännisch auf ganze Cent gerundet (halbe Cent aufrunden).
- Die Berechnung gilt unverändert für 3 und 4 Spieler (ADR-017).

Beispiel (4 Spieler, STAND Bernd 250, Carla 90, Dirk 60, Anna 0): Bernd zahlt 0,00 €; Carla
160 Punkte Differenz = 16 × 5 Cent = **0,80 €**; Dirk 190 Punkte = **0,95 €**; Anna 250 Punkte =
**1,25 €**.

### 20.3 Darstellung

Beträge werden in **Euro mit Euro-Zeichen** im deutschen Format dargestellt, mit höchstens zwei
Nachkommastellen (z. B. `0,80 €`, `1,25 €`). Die Anschreibetabelle zeigt sie in einer eigenen
Zeile **unter der letzten STAND-Zeile**.

- **Nur Zahlende werden angezeigt:** Beim Spitzenreiter – bei Gleichstand an der Spitze bei allen
  Spitzenreitern – bleibt die Zelle leer; ein Betrag erscheint nur bei Mitspielern mit weniger
  Punkten. Muss niemand etwas zahlen (z. B. zu Spielbeginn), entfällt die ganze Zeile.
- Das ist eine reine Darstellungsregel: Die Berechnung (§20.2) und die API liefern für den
  Spitzenreiter weiterhin 0 Cent.
- **Beschriftung:** Im laufenden Spiel „zu zahlen, wenn das Spiel jetzt endet“, in der Endabrechnung
  „Wer zahlt was in die Kasse“.

---

## 21. Verhältnis zu anderen Dokumenten

- `docs/ubiquitous-language.md` definiert die gemeinsame Fachsprache.
- `docs/language-conventions.md` beschreibt die Sprachkonventionen des Projekts.
- `docs/Anschreibetabelle_3_und_4_Spieler.md` enthält die tabellarische Herleitung und Beispiele.
- `features/` enthält die normative Gherkin-Spezifikation, die dieses Regelwerk in ausführbare BDD-Szenarien übersetzt.
- `docs/gherkin-step-phrase-reference-v1.md` enthält die kanonischen Step-Phrasen zur Implementierung der Szenarien.
- `docs/development-approach-v1.md` benennt dieses Dokument als normative Quelle für alle Domänenlogik-Implementierungen.
- Dieses Dokument definiert das verbindliche **V1-Regelwerk** für Produkt, Modell und Implementierung.
