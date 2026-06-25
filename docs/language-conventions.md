# Sprachkonventionen

## 1. Zweck

Dieses Dokument beschreibt die verbindlichen Sprachkonventionen für das Projekt **Binokel Score Tracker**.

Ziel ist es, eine konsistente Benennung über Fachgespräche, Dokumentation, Gherkin-Szenarien, Domänenmodell, Benutzeroberfläche und Code hinweg sicherzustellen.

Die Sprachkonventionen ergänzen die gemeinsame Fachsprache in `docs/ubiquitous-language.md` und konkretisieren, wie diese Fachsprache im Code, in technischen Artefakten und in der Dokumentation verwendet wird.

---

## 2. Geltungsbereich

Diese Konventionen gelten für:

- Fachdokumentation,
- Gherkin- und BDD-Spezifikationen,
- Domänenmodell und fachnahe Anwendungslogik,
- technische Adapter und Infrastruktur,
- API-Benennung,
- Persistenzbenennung,
- UI-Texte,
- Beiträge zum Repository.

---

## 3. Grundprinzip

Die Sprache folgt der Bedeutungsebene.

- **Fachdomäne / Geschäftslogik:** Deutsch
- **Technische Infrastruktur / Framework / Plattform:** überwiegend Englisch bzw. framework-üblich
- **Dokumentation:** Deutsch
- **Gherkin / BDD-Szenarien:** Deutsch
- **Dateinamen:** dürfen Englisch bleiben, wenn sie konsistent und verständlich sind

Entscheidend ist nicht eine dogmatische Sprachreinheit, sondern eine **klare, konsistente und fachlich verständliche Benennung**.

---

## 4. Deutsch in der Fachdomäne

Im fachlichen Kern des Systems werden deutsche Fachbegriffe bevorzugt.

Dies betrifft insbesondere:

- Entitäten,
- Value Objects,
- Domänenservices,
- fachliche Use Cases,
- fachliche Methoden,
- zentrale UI-Begriffe,
- Gherkin-Szenarien und Akzeptanzkriterien.

### Beispiele für bevorzugte Domänenbegriffe

- `Spiel`
- `Runde`
- `Spieler`
- `Regelwerk`
- `Wertungseintrag`
- `Punktestand`
- `Reizwert`
- `Spielmacher`
- `Meldepunkte`
- `Stichpunkte`
- `Mitpunkte`
- `Spielstatus`

### Beispiele für fachliche Methoden

- `berechne_punktestand`
- `fuege_runde_hinzu`
- `pruefe_stichzwang`
- `werte_runde_aus`
- `ist_abgeschlossen`
- `ermittle_spielmacher`

Wenn ein Fachbegriff im Regelwerk, in der Fachsprache und im Gespräch auf Deutsch verwendet wird, soll er **nicht nur aus Stilgründen ins Englische übersetzt** werden.

---

## 5. Englisch in technischer Infrastruktur

In technischer Infrastruktur und frameworknahen Bereichen dürfen englische oder framework-übliche Begriffe verwendet werden.

Dies betrifft insbesondere:

- Framework-Artefakte,
- Bibliotheksintegration,
- technische Adapter,
- Plattform-Konfiguration,
- Build- und Deployment-Artefakte,
- Testwerkzeuge,
- technische Architekturbausteine.

### Beispiele für zulässige technische Begriffe

- `Repository`
- `Controller`
- `Service`
- `Serializer`
- `Mapper`
- `Settings`
- `Migration`
- `Factory`
- `ViewSet`
- `TestClient`

### Empfohlene Mischformen

Wenn fachlicher Kern und technischer Typ zusammenkommen, ist eine Mischform zulässig, solange sie konsistent ist.

Beispiele:

- `SpielRepository`
- `RundenSerializer`
- `SpielController`
- `RegelwerkMapper`
- `DjangoSpielRepository`

Die technische Form darf englisch sein, der fachliche Kern bleibt deutsch.

---

## 6. Regeln für Dokumentation und Gherkin

### Dokumentation

Fachdokumentation wird auf Deutsch verfasst.

Dazu gehören insbesondere:

- `README.md` (soweit fachlich orientiert),
- `docs/project-foundation.md`,
- `docs/ubiquitous-language.md`,
- Regelwerksdokumente,
- fachlich geprägte Architektur- und Entscheidungsdokumente.

### Gherkin / BDD

BDD- und Gherkin-Spezifikationen werden auf Deutsch verfasst.

Dies betrifft:

- Feature-Beschreibungen,
- Szenarien,
- Fachbegriffe in Given/When/Then,
- Akzeptanzkriterien.

Beispiel:

- `Funktionalität: Runde auswerten`
- `Szenario: Meldepunkte verfallen ohne Stich`

---

## 7. Regeln nach Schichten

### 7.1 Domänenschicht

Die Domänenschicht verwendet bevorzugt deutsche Fachbegriffe.

### 7.2 Anwendungsschicht

Die Anwendungsschicht verwendet überwiegend deutsche Fachbegriffe, wenn sie fachnahe Abläufe orchestriert.

Beispiele:

- `SpielAnlegenUseCase`
- `RundeAuswertenService`
- `SpielAbschliessenHandler`

### 7.3 Infrastruktur- und Adapterschicht

Die Infrastruktur darf stärker englisch bzw. frameworküblich benannt werden, solange der fachliche Bezug erhalten bleibt.

### 7.4 Benutzeroberfläche

Die UI verwendet bevorzugt deutsche Fachbegriffe, sofern keine bewusste Produktentscheidung für englische Benutzeroberflächen getroffen wurde.

### 7.5 Persistenz

Tabellen-, Spalten- und Persistenzbegriffe sollen konsistent in **einer Sprache** benannt werden.

Für dieses Projekt ist Deutsch in der fachnahen Persistenz bevorzugt, sofern keine technischen Gründe dagegensprechen.

### 7.6 API

Die API-Sprache ist eine bewusste Architekturentscheidung.

Für das MVP gilt zunächst:

- interne fachliche Modelle bleiben deutsch,
- eine spätere externe API darf englisch gestaltet werden,
- notwendige Mappings müssen dokumentiert werden.

---

## 8. Vermeidung problematischer Mischformen

Die folgenden Benennungsmuster sollen vermieden werden:

### 8.1 Unklare Sprachmischungen innerhalb eines Begriffs

Nicht empfohlen:

- `GameMitPointsService`
- `SpielScoreEntry`
- `RoundBewertung`

Besser:

- `SpielWertungService`
- `Wertungseintrag`
- `Rundenbewertung`

oder, wenn technisch sinnvoll:

- `RundenbewertungService`

### 8.2 Mehrere Begriffe für dasselbe Fachkonzept

Nicht parallel verwenden:

- `Spiel` und `Game`
- `Punktestand` und `Standing`
- `Reizwert` und `Bid`
- `Spielmacher` und `GameMaker`

Für jedes zentrale Fachkonzept soll es **einen bevorzugten Begriff** geben.

### 8.3 Vage technische Ersatzwörter für Fachbegriffe

Nicht empfohlen:

- `bonus` statt `mitpunkte`
- `score` statt `punktestand`, `meldepunkte` oder `stichpunkte`
- `session` statt `spiel`

---

## 9. Mapping-Regel zwischen Fachsprache und Code

Die gemeinsame Fachsprache ist in `docs/ubiquitous-language.md` definiert.

Wenn im Code, in der API oder in technischen Artefakten ausnahmsweise ein anderer Begriff verwendet wird, muss dieses Mapping dokumentiert und begründet werden.

Beispiele:

- `Spiel` → `Game` **nur**, wenn ein externer API-Kontext dies erfordert
- `Reizwert` → `bid` in einer externen Schnittstelle
- `Punktestand` → `score` **nur** bei klar dokumentiertem technischen Zwang

Die Standardannahme bleibt jedoch:

**Fachbegriff in der Doku = Fachbegriff im Domänenmodell**

---

## 10. Entscheidungsregel bei Zweifeln

Wenn unklar ist, wie ein Begriff benannt werden soll, gilt folgende Reihenfolge:

1. Welcher Begriff wird von Fachseite und im Regelwerk tatsächlich verwendet?
2. Ist der Begriff bereits in `docs/ubiquitous-language.md` definiert?
3. Gehört der Begriff zur Fachdomäne oder zur technischen Infrastruktur?
4. Führt eine Übersetzung zu Klarheit oder zu zusätzlicher mentaler Übersetzung?
5. Ist die gewählte Benennung im Projekt bereits konsistent etabliert?

Im Zweifel gilt:

- **fachlich deutsch**, wenn es um die Binokel-Domäne geht,
- **technisch pragmatisch**, wenn es um Framework- oder Infrastrukturbegriffe geht,
- **niemals unbegründet mischen**.

---

## 11. Verweise auf andere Dokumente

- `docs/project-foundation.md` beschreibt die grundlegenden Projektentscheidungen.
- `docs/ubiquitous-language.md` definiert die gemeinsame Fachsprache.
- Dieses Dokument beschreibt, **wie** diese Fachsprache in Dokumentation, Code und technischen Artefakten angewendet wird.
