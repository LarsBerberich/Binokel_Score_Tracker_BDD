# Gemeinsame Fachsprache

## 1. Zweck

Dieses Dokument definiert die gemeinsame fachliche Sprache für das Projekt **Binokel Score Tracker**.

Ziel ist es, sicherzustellen, dass Fachgespräche, Dokumentation, Gherkin-Szenarien, Domänenmodell, UI-Bezeichnungen und Code dieselben Begriffe in derselben Bedeutung verwenden.

Ein fachlicher Begriff, der unklar oder mehrdeutig ist, soll hier geklärt werden, bevor er in Implementierung, Tests oder Benutzeroberfläche übernommen wird.

---

## 2. Geltungsbereich

Diese Fachsprache gilt für:

- Produkt- und Regeldiskussionen,
- funktionale Anforderungen,
- BDD- und Gherkin-Spezifikationen,
- Domänenmodell und fachnahe Backend-Logik,
- UI-Terminologie im Frontend,
- fachnahe Persistenzbenennung, wo sinnvoll.

Das Dokument ist bewusst fachlich ausgerichtet und soll framework-spezifische oder rein technische Begriffe vermeiden, wenn ein passender Fachbegriff existiert.

## Sprachliche Anwendung im Projekt

Die in diesem Dokument definierte gemeinsame Fachsprache wird durch die Sprachkonventionen in `docs/language-conventions.md` ergänzt.

Während dieses Dokument die fachlich bevorzugten Begriffe beschreibt, legt `docs/language-conventions.md` fest, wie diese Begriffe in Dokumentation, Gherkin, Domänenmodell, technischer Infrastruktur und sonstigen Code-Artefakten verwendet werden sollen.

---

## 3. Grundprinzipien der Modellierung

1. Fachbegriffe haben Vorrang vor technischen Abkürzungen.
2. Ein Begriff soll möglichst genau ein Konzept bezeichnen.
3. Synonyme sollen in Code, Tests und Dokumentation vermieden werden, wenn sie dasselbe meinen.
4. Wenn ein Begriff im Alltag mehrere Bedeutungen hat, gilt die projektspezifische Definition aus diesem Dokument.
5. Wenn sich lokale Binokel-Begriffe und allgemeine Softwarebegriffe unterscheiden, wird der Binokel-Begriff bevorzugt und bei Bedarf erläutert.

---

## 4. Kernbegriffe

### 4.1 Spiel

Ein **Spiel** ist eine vollständige Binokel-Partie vom Anfang bis zum Ende.

Ein Spiel umfasst:
- die teilnehmenden Spieler,
- das gewählte Regelwerk,
- eine Folge von Runden,
- die aktuellen Punktestände,
- ein Endergebnis.

**Bevorzugte Verwendung im Code:** `Spiel`

**Nicht verwechseln mit:**
- einer einzelnen Runde,
- einem einzelnen Blatt,
- einer technischen Anwendungssitzung.

---

### 4.2 Runde

Eine **Runde** ist ein Wertungszyklus innerhalb eines Spiels.

Eine Runde erfasst das wertungsrelevante Ergebnis eines gespielten Gebens oder einer ausgewerteten Spieleinheit – abhängig vom gewählten Binokel-Regelwerk.

Eine Runde kann enthalten:
- Informationen zum Geber,
- aktive Spieler,
- Reizenden bzw. Spielmacher,
- Reizwert,
- Meldewerte,
- Stichpunkte,
- Mitpunkte,
- besondere Ausgänge wie gewonnenes Spiel, einfaches Abgehen, doppeltes Abgehen oder Tausender.

**Bevorzugte Verwendung im Code:** `Runde`

**Nicht verwechseln mit:**
- einem UI-Schritt,
- einem vollständigen Spiel.

---

### 4.3 Spieler

Ein **Spieler** ist eine Person, die an einem Spiel teilnimmt.

Im MVP ist ein Spieler primär ein fachlicher Wertungsteilnehmer. Persistente Spielerprofile können später ergänzt werden, ohne den Fachbegriff zu verändern.

**Bevorzugte Verwendung im Code:** `Spieler`

**Nicht verwechseln mit:**
- einem Benutzerkonto,
- einem authentifizierten Systemnutzer.

---

### 4.4 Geber

Der **Geber** ist der Spieler, der in einer Runde die Karten gibt.

In der derzeit dokumentierten 4-Spieler-Auslegung setzt der Geber in der Runde aus, während die drei anderen Spieler aktiv sind.

**Bevorzugte Verwendung im Code:** `Geber`

**Hinweis:** Dieses Verhalten gehört zum gewählten Regelwerk und darf nicht pauschal für alle künftigen Varianten angenommen werden.

---

### 4.5 Aktiver Spieler

Ein **aktiver Spieler** ist ein Spieler, der in der aktuellen Runde direkt mitspielt.

In der derzeit dokumentierten 4-Spieler-Auslegung gilt:
- 3 Spieler sind aktiv,
- 1 Spieler ist Geber und in dieser Runde nicht aktiv.

**Bevorzugte Verwendung im Code:** `AktiverSpieler` oder fachlich über Rollenmodell

---

### 4.6 Regelwerk

Ein **Regelwerk** ist die ausdrücklich festgelegte Spiel- und Wertungslogik, die für ein Spiel gilt.

Es bestimmt zum Beispiel:
- den Spielmodus,
- Wertungsregeln,
- Folgen des Reizens,
- Endbedingungen,
- Sonderfälle,
- variantenspezifische Begriffe.

**Bevorzugte Verwendung im Code:** `Regelwerk`

**Wichtig:** Regeln dürfen nicht versteckt in verstreuten Bedingungsblöcken liegen, sondern gehören fachlich in ein klar benanntes Regelwerk.

---

### 4.7 Wertungseintrag

Ein **Wertungseintrag** ist die strukturierte Eingabe, die für eine Runde und einen Spieler erfasst wird.

Er enthält die wertungsrelevanten Angaben, die benötigt werden, um das Rundenresultat auszuwerten und darzustellen.

Je nach Regelwerk kann ein Wertungseintrag enthalten:
- Meldepunkte,
- Stichpunkte,
- Mitpunkte,
- Strafwerte,
- Sterne,
- erläuternde Statusinformationen.

**Bevorzugte Verwendung im Code:** `Wertungseintrag`

**Nicht verwechseln mit:**
- dem kumulierten Punktestand,
- dem rohen Zustand eines Eingabeformulars.

---

### 4.8 Meldung

Eine **Meldung** ist eine angesagte Kartenkombination, die gemäß Regelwerk Punkte bringt.

Beispiele aus den dokumentierten Regeln sind:
- Paar,
- Trumpf-Paar,
- Binokel,
- Familie,
- Rundlauf,
- Doppelter Binokel.

**Bevorzugte Verwendung im Code:** `Meldung`

**Zugehöriger Begriff:** `Meldepunkte`

---

### 4.9 Meldepunkte

**Meldepunkte** sind die Punkte, die für gültige Meldungen in einer Runde vergeben werden.

In den bisherigen Wertungsbeispielen entspricht dies der Spalte **M**.

**Bevorzugte Verwendung im Code:** `meldepunkte`

**Wichtig:** Ob Meldepunkte tatsächlich zählen, kann von Regeln wie dem Stich-Zwang oder besonderen Verlustfällen abhängen.

---

### 4.10 Stichpunkte

**Stichpunkte** sind die Punkte, die durch gewonnene Stiche erzielt werden.

In den bisherigen Wertungsbeispielen entspricht dies der Spalte **S**.

**Bevorzugte Verwendung im Code:** `stichpunkte`

**Nicht verwechseln mit:**
- Meldepunkten,
- dem kumulierten Punktestand.

---

### 4.11 Mitpunkte

**Mitpunkte** sind Zusatzpunkte, die Gegner in bestimmten Verlustfällen des Spielmachers erhalten.

In den dokumentierten Regeln entspricht dies der Spalte **Mit** und ist derzeit als `+30` für die Gegner bei einfachem und doppeltem Abgehen beschrieben.

**Bevorzugte Verwendung im Code:** `mitpunkte`

**Wichtig:** Dies ist ein fachlich geprägter Begriff und sollte nicht unklar in generische Wörter wie `Bonus` übersetzt werden.

---

### 4.12 Punktestand

Der **Punktestand** ist der kumulierte Wertungsstand eines Spielers innerhalb eines laufenden oder abgeschlossenen Spiels.

Er bildet den aufaddierten Stand nach jeder Runde ab.

In den dokumentierten Tabellenbeispielen entspricht dies der Zeile **STAND**.

**Bevorzugte Verwendung im Code:** `Punktestand`

**Nicht verwechseln mit:**
- einem einzelnen Rundenergebnis,
- einer Rangliste über mehrere Spiele hinweg.

---

### 4.13 Endergebnis

Das **Endergebnis** ist das persistierte Ergebnis eines abgeschlossenen Spiels.

Es umfasst mindestens:
- die endgültigen Punktestände,
- den Gewinner bzw. die Gewinnbedingung,
- das verwendete Regelwerk,
- die abgeschlossene Folge von Runden.

**Bevorzugte Verwendung im Code:** `Endergebnis`

---

### 4.14 Reizwert

Der **Reizwert** ist der angesagte Wert, den ein Spieler als Spielmacher erfüllen muss.

In Quellen und Tabellen kann auch von:
- `gereizt bis`
- `Wert`

gesprochen werden.

Im Projekt wird fachlich **Reizwert** bevorzugt.

**Bevorzugte Verwendung im Code:** `reizwert`

---

### 4.15 Spielmacher

Der **Spielmacher** ist der Spieler, der das Reizen gewinnt und das Spiel erfüllen muss.

**Bevorzugte Verwendung im Code:** `Spielmacher`

---

### 4.16 Gewonnenes Spiel

Ein **gewonnenes Spiel** liegt vor, wenn der Spielmacher das geforderte Ziel erreicht und die Runde gemäß Regelwerk erfolgreich abschließt.

In diesem Fall gilt:
- der Spielmacher erhält sein tatsächliches Rundenergebnis,
- die Gegner erhalten ihre zulässigen Punkte,
- es werden keine Mitpunkte vergeben.

**Bevorzugte Verwendung im Code:** `GewonnenesSpiel` oder Ausprägung des Rundenausgangs

---

### 4.17 Einfaches Abgehen

**Einfaches Abgehen** ist der Fall, in dem der Spielmacher das Spiel nach Sicht des Dapps vor dem ersten Stich aufgibt.

**Bevorzugte Verwendung im Code:** `EinfachesAbgehen`

---

### 4.18 Doppeltes Abgehen

**Doppeltes Abgehen** ist der Fall, in dem der Spielmacher ausspielt, aber den Reizwert nicht erreicht.

**Bevorzugte Verwendung im Code:** `DoppeltesAbgehen`

---

### 4.19 Tausender

Ein **Tausender** ist ein besonderer angesagter Spielausgang gemäß dem gewählten Regelwerk.

In der derzeit dokumentierten Fassung gilt:
- normale Punktewertung wird eingefroren,
- keine Meldepunkte werden gezählt,
- keine Stichpunkte werden gezählt,
- keine Mitpunkte werden gezählt,
- je nach Erfolg oder Misserfolg wird ein Stern vergeben.

**Bevorzugte Verwendung im Code:** `Tausender`

Da dies ein stark fachgeprägter Begriff ist, soll er nicht ohne guten Grund übersetzt werden.

---

### 4.20 Stern

Ein **Stern** ist ein nicht-numerischer Erfolgsmarker im Zusammenhang mit dem Tausender.

In den dokumentierten Regeln wird er als `★` dargestellt.

**Bevorzugte Verwendung im Code:** `Stern`

**Wichtig:** Ein Stern ist nicht dasselbe wie normale Punkte und darf fachlich nicht als gewöhnlicher Zahlenwert modelliert werden.

---

### 4.21 Stich-Zwang

Der **Stich-Zwang** ist die Regel, dass ein Spieler mindestens einen Stich gewinnen muss, damit seine Meldepunkte zählen.

In den dokumentierten Regeln gilt:
- normalerweise verfallen Meldepunkte bei 0 Stichen,
- bei Verlustfällen des Spielmachers können Gegner ihre Meldepunkte auch ohne eigenen Stich behalten.

**Bevorzugte Verwendung im Code:** `StichZwang`

---

### 4.22 Spielstatus

Der **Spielstatus** beschreibt den Lebenszykluszustand eines Spiels.

Erste Kandidaten sind:
- `geplant`
- `aktiv`
- `abgeschlossen`
- `abgebrochen`

**Bevorzugte Verwendung im Code:** `Spielstatus`

---

### 4.23 Rundenausgang

Der **Rundenausgang** beschreibt die fachlich klassifizierte Ergebnisart einer Runde.

Erste Kandidaten auf Basis der bisherigen Dokumentation sind:
- `gewonnenes_spiel`
- `einfaches_abgehen`
- `doppeltes_abgehen`
- `tausender_gewonnen`
- `tausender_verloren`

**Bevorzugte Verwendung im Code:** `Rundenausgang`

Dies hilft dabei, fachliche Bedeutung von bloßen Zahlenwerten zu trennen.

---

## 5. Bevorzugte Begriffsmappings

Im Projekt können deutsche Begriffe, Quellbegriffe und informelle Begriffe nebeneinander vorkommen. Für die gemeinsame Fachsprache gelten die folgenden bevorzugten Zuordnungen:

| Quell- oder Alltagsbegriff | Bevorzugter Projektbegriff |
| --- | --- |
| Match | Spiel |
| Session | Spiel, nur wenn wirklich eine Spielsession gemeint ist |
| Spiel | Spiel |
| Runde | Runde |
| Anschreiben | Punkteerfassung oder Wertungseintrag, je nach Kontext |
| Spielmacher | Spielmacher |
| Gereizt bis | Reizwert |
| Wert | Reizwert, wenn fachlich der Reizwert gemeint ist |
| M | Meldepunkte |
| S | Stichpunkte |
| Mit | Mitpunkte |
| Stand | Punktestand |
| Abgehen einfach | Einfaches Abgehen |
| Abgehen doppelt | Doppeltes Abgehen |
| Stich-Zwang | Stich-Zwang |

---

## 6. Begriffe, die vermieden oder vorsichtig verwendet werden sollen

### 6.1 Session

**Session** soll nur vorsichtig verwendet werden.

In der Software kann Session bedeuten:
- Browser-Session,
- Login-Session,
- Laufzeit-Session,
- Spiel-Session.

Für die Fachdomäne sind in der Regel präziser:
- **Spiel** für eine vollständige Partie,
- **Runde** für einen Wertungszyklus.

---

### 6.2 Score

**Score** soll nur verwendet werden, wenn der Kontext absolut eindeutig ist.

Der Begriff kann sonst meinen:
- Rundenergebnis,
- kumulierten Punktestand,
- Meldepunkte,
- Stichpunkte,
- Endergebnis.

Präziser sind je nach Kontext:
- Meldepunkte
- Stichpunkte
- Punktestand
- Endergebnis
- Wertungseintrag

---

### 6.3 Benutzer

**Benutzer** soll nicht als Synonym für **Spieler** verwendet werden, es sei denn, es geht tatsächlich um Authentifizierung oder technische Identität.

Ein Spieler ist eine fachliche Rolle. Ein Benutzerkonto ist ein technisches Anwendungskonzept.

---

## 7. Erste fachliche Kandidaten für Aufzählungstypen

Dies sind noch keine endgültigen Implementierungsdetails, aber nützliche sprachliche Anker.

### 7.1 Spielstatus

- geplant
- aktiv
- abgeschlossen
- abgebrochen

### 7.2 Rundenausgang

- gewonnenes_spiel
- einfaches_abgehen
- doppeltes_abgehen
- tausender_gewonnen
- tausender_verloren

### 7.3 Rollen in einer Runde

- geber
- aktiver_spieler
- spielmacher

---

## 8. Offene Fragen zur Fachsprache

Die folgenden Punkte sollten gemeinsam geklärt werden, bevor die Begriffe zu fest in Implementierung und Tests verankert werden:

1. Soll das MVP konsequent deutsch benannt bleiben – auch in fachnahen Code-Artefakten?
2. Soll `Punktestand` der bevorzugte Begriff bleiben oder soll in einzelnen Kontexten weiterhin `Stand` verwendet werden?
3. Soll `Wertungseintrag` der dauerhafte Begriff sein oder ist `Anschreibeeintrag` in dieser Domäne näher an der Fachpraxis?
4. Brauchen wir für das MVP bereits explizite Fachbegriffe für Teams oder ist Einzelwertung die einzige V1-Zielausprägung?
5. Welche Begriffe aus dem aktuellen Regelwerk müssen vor der Implementierung noch weiter präzisiert werden?

---

## 9. Anwendungsregel

Bevor ein neuer fachlicher Begriff in:
- Code,
- Tests,
- Gherkin,
- UI-Texten,
- Architektur- oder Regeldokumenten

eingeführt wird, ist zu prüfen, ob das zugrunde liegende Konzept bereits in diesem Dokument definiert ist.

Falls nicht, soll der Begriff hier ergänzt oder präzisiert werden, wenn er für die Domäne zentral ist.
