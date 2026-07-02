# Entwicklungsansatz V1

## 1. Zweck dieses Dokuments

Dieses Dokument beschreibt den operativen Entwicklungsansatz für V1 des **Binokel Score Trackers** — vom Akzeptanztest bis zur laufenden Anwendung.

Es ergänzt die strategischen Prinzipien in `docs/project-foundation.md` um konkrete Aussagen darüber, in welcher Reihenfolge und nach welchem Muster entwickelt wird.

---

## 2. Leitendes Prinzip: Outside-In Development

Wir entwickeln von außen nach innen, getrieben durch Akzeptanztests:

```
Gherkin-Szenario (Akzeptanztest)   ← Außen: beschreibt beobachtbares Verhalten
         ↓
  API / Use Case                   ← Anwendungsschicht: orchestriert den Ablauf
         ↓
  Domänenlogik                     ← Fachkern: enthält die Wertungsregeln
         ↓
  Persistenz / Infrastruktur       ← Innen: speichert und liest Daten
```

Kein Code wird geschrieben, der nicht durch einen fehlschlagenden Test gefordert wird.

### Warum Outside-In und nicht Inside-Out?

**Inside-Out** (klassischer Ansatz) bedeutet: erst Datenbankschema, dann Klassen, dann Use Cases, dann API, dann UI. Das klingt strukturiert, hat aber einen fundamentalen Fehler: Man baut das Fundament, ohne zu wissen, welches Haus darauf steht. Typische Konsequenzen: Das Datenbankschema passt nicht zur Domänenlogik, die API passt nicht zur UI — und man refaktorisiert alles mehrfach.

**Outside-In** dreht das um: Die Domänenfälle (Gherkin) bestimmen, was die API braucht. Die API bestimmt, welche Use Cases nötig sind. Die Use Cases bestimmen, welche Domänenklassen es geben muss. Die Domänenklassen bestimmen, wie das Datenbankschema aussieht.

Man baut immer genau das, was der nächste Test braucht — nicht mehr.

---

## 3. RED-Green-Refactor im BDD-Kontext

Im Unterschied zum klassischen Unit-Test-TDD operiert BDD auf zwei ineinandergreifenden Schleifen:

### Äußere Schleife — Akzeptanztests (behave)

| Schritt | Aktion | Zustand |
|---|---|---|
| **RED** | Gherkin-Szenario existiert, Step-Definition als Stub angelegt | `behave` schlägt fehl |
| **GREEN** | Domänenlogik und API implementieren | `behave` besteht |
| **REFACTOR** | Code aufräumen, Struktur verbessern | `behave` bleibt grün |

### Innere Schleife — Unit-Tests (pytest)

Innerhalb der GREEN-Phase wird die Domänenlogik selbst per Unit-Tests entwickelt:

| Schritt | Aktion | Zustand |
|---|---|---|
| **RED** | Unit-Test für eine Fachrregel schreiben | schlägt fehl |
| **GREEN** | Minimale Implementierung | Test besteht |
| **REFACTOR** | Aufräumen | Test bleibt grün |

Die äußere Schleife gibt die Richtung vor. Die innere Schleife sichert die Korrektheit der Domänenlogik ab.

```
behave (äußere Schleife)
  └── pytest (innere Schleife pro Domänenregel)
```

### Warum zwei Schleifen?

Die **äußere Schleife** (Gherkin/behave) stellt sicher, dass wir **das Richtige bauen**: Das Szenario definiert das gewünschte Verhalten aus fachlicher Perspektive. Wenn die äußere Schleife grün ist, ist das Feature fachlich korrekt.

Die **innere Schleife** (pytest) stellt sicher, dass wir **es richtig bauen**: Sie prüft die Domänenlogik isoliert, ohne HTTP-Request, ohne Datenbank. Das macht Tests schnell und die Logik unabhängig vom Framework testbar — genau das, was §13 „Testbarkeit" in `docs/project-foundation.md` fordert.

Ohne diesen Zyklus entsteht typischerweise:
- Code wird geschrieben, ohne zu wissen ob er gebraucht wird.
- Tests werden nachträglich geschrieben und passen sich der Implementierung an statt sie zu treiben.
- Refaktorisierungen werden hinausgezögert, weil die Sicherheit fehlt, nichts kaputt zu machen.
- Das System wächst unkontrolliert.

---

## 4. Vertikale Slices statt horizontaler Schichten

Wir implementieren **Feature für Feature** als vollständigen vertikalen Schnitt durch alle Schichten — nicht erst alle Domänenklassen, dann alle Use Cases, dann alle Controller.

```
Feature-Datei  →  Step-Definitionen  →  Use Case  →  Domänenlogik  →  API
     ↑ eine Slice = ein testbarer, lieferbarer Mehrwert ↑
```

Horizontale Querschnittsthemen (z. B. Datenbankzugriff, Fehlerbehandlung, Auth) werden einmalig aufgesetzt, dann von allen Slices genutzt.

### Warum nicht horizontale Schichten?

**Horizontale Entwicklung** würde bedeuten: erst alle Domänenklassen für alle 6 Features fertigstellen, dann alle Use Cases, dann alle API-Endpunkte. Das hat drei massive Nachteile:

- **Kein Feedback über lange Zeit:** Man kann erst nach Wochen prüfen, ob das System als Ganzes funktioniert.
- **Designfehler werden spät aufgedeckt:** Wenn die API ein anderes Objekt braucht als die Domäne liefert, ist die Korrektur teuer — viele bereits fertiggestellte Schichten sind betroffen.
- **Motivationsproblem:** Nichts ist lauffähig bis ganz am Ende.

Vertikale Slices liefern dagegen nach jeder Slice ein lauffähiges, getestetes Teilsystem. Nach der ersten Slice (`spiel_anlegen`) läuft bereits ein vollständiger Akzeptanztest. Das gibt sofort Sicherheit und zeigt frühzeitig, ob die Gesamtarchitektur trägt.

---

## 5. Technische Entwicklungsreihenfolge für V1

Da die Domänenlogik komplex und vollständig spezifiziert ist und Django und Vue als getrennte Schichten eingesetzt werden, empfiehlt sich folgendes Phasenmodell:

### Warum Backend vor Frontend?

**a) Die Domänenlogik ist das Herzstück.** Die Rundenauswertung (Reizwert-Prüfung, Stich-Zwang, Verlustwertberechnung) ist komplex und fachlich präzise in `docs/rule-set-v1.md` spezifiziert. Fehler in der Domänenlogik sind gefährlicher als Fehler in der UI — sie produzieren stille, falsche Ergebnisse.

**b) Die Akzeptanztests laufen gegen das Backend.** Die Gherkin-Features beschreiben fachliches Verhalten, keine UI-Interaktion. Sie sind die natürliche Antriebskraft für Phase 1 und laufen vollständig ohne Frontend.

**c) Die API definiert den Kontrakt für das Frontend.** Wenn das Backend stabil und durch Tests abgesichert ist, kann das Frontend auf einem stabilen Fundament aufgebaut werden — ohne dass sich API-Änderungen laufend durch die UI-Schicht durchziehen.

**d) Austauschbarkeit.** Wenn die Domänenlogik vollständig getestet ist, kann das Frontend bei Bedarf ausgetauscht werden (z.B. native App), ohne die Kernlogik anzufassen.

### Phase 1 — Backend-Kern (Outside-In, Feature für Feature)

Ziel: Alle Gherkin-Szenarien laufen grün gegen das Backend.

1. Python-Projektstruktur und `behave` einrichten.
2. Django-Grundgerüst anlegen (Settings, URL-Routing, App-Struktur).
3. Step-Stub-Dateien aus `docs/gherkin-step-phrase-reference-v1.md` generieren → `behave` ausführen → **alles RED**.
4. Feature für Feature implementieren (Domänenlogik + Django-Use-Case + REST-API):

| Reihenfolge | Feature-Datei | Begründung |
|---|---|---|
| 1 | `spiel_anlegen.feature` | Grundlage: ohne Spiel keine Runde |
| 2 | `runde_normales_spiel.feature` | Häufigster Ablauf, zentrale Wertungslogik |
| 3 | `runde_einfaches_abgehen_auswerten.feature` | Einfachster Verlustfall |
| 4 | `runde_deoppeltes_abgehen.feature` | Komplexerer Verlustfall, baut auf Slice 2 auf |
| 5 | `runde_tausender.feature` | Sonderfall ohne numerische Wertung |
| 6 | `spielende_und_siegerermittlung.feature` | Setzt alle vorigen Slices voraus |

### Phase 2 — Frontend (Vue, Slice für Slice)

Ziel: Alle Kern-Workflows sind über eine Vue-Oberfläche bedienbar.

1. Vue-Anwendung aufsetzen, API-Client konfigurieren.
2. Reihenfolge orientiert sich an häufigsten Nutzerworkflows:
   - Spiel anlegen
   - Runde eingeben und auswerten
   - Spielstand anzeigen
   - Spiel abschließen

Die Gherkin-Akzeptanztests aus Phase 1 bleiben in Phase 2 grün — das Backend ändert sich nicht.

---

## 6. Was nicht gebaut wird

Dem **YAGNI-Prinzip** folgend gilt:

- Kein Code ohne fehlschlagenden Test.
- Keine Schicht, die kein Feature fordert.
- Keine Abstraktion, die nur ein einziges Feature bedient.
- Kein UI-Polishing, bevor das Backend stabil ist.

### Warum YAGNI?

Das klassische Problem spekulativer Entwicklung: Man schreibt eine generische Abstraktion, „weil sie später sicher nützlich sein wird". Meistens wird sie es nicht — oder sie passt nicht zu dem, was später tatsächlich gebraucht wird, und wird zur Last.

Konkrete Beispiele für dieses Projekt:
- Keine generische `BaseRound`-Klasse einführen, bevor drei Rundentypen sie tatsächlich gemeinsam brauchen.
- Kein Caching-Layer, weil er „vielleicht nützlich" sein könnte.
- Keine Authentifizierung in Phase 1, solange kein Gherkin-Szenario sie fordert.

Der RED-Green-Refactor-Zyklus ist der mechanische Schutz: Wenn kein Test rot ist, wird kein Code geschrieben.

---

## 7. Gherkin-Sprachkonventionen für Deutsch (`# language: de`)

Die Feature-Dateien dieses Projekts verwenden `# language: de`. Damit verarbeitet behave die Datei mit dem deutschen Keyword-Set gemäß der offiziellen Gherkin-Spezifikation unter [cucumber.io/docs/gherkin/languages](https://cucumber.io/docs/gherkin/languages).

### Gültige deutsche Schlüsselwörter (offiziell, Stand 2026)

| Gherkin-Rolle | Gültige Schlüsselwörter |
|---|---|
| **Given** | `Angenommen` · `Gegeben sei` · `Gegeben seien` |
| **When** | `Wenn` |
| **Then** | `Dann` |
| **And** | `Und` |
| **But** | `Aber` |
| **Feature** | `Funktionalität` · `Funktion` |
| **Background** | `Grundlage` · `Hintergrund` · `Voraussetzungen` · `Vorbedingungen` |
| **Scenario** | `Szenario` · `Beispiel` |
| **Scenario Outline** | `Szenariogrundriss` · `Szenarien` |
| **Examples** | `Beispiele` |

### Verbindliche Konvention für dieses Projekt

**Given-Schritte werden ausschließlich mit `Angenommen` formuliert.**

Begründung:
- `Gegeben sei` / `Gegeben seien` sind grammatikalisch auf Sätze im Konjunktiv beschränkt und passen nicht zu allen Step-Formulierungen (z.B. *„Gegeben sei der Rundenausgang ist ..."* ist grammatikalisch falsch).
- `Angenommen` ist grammatikalisch neutral und passt zu allen Satzstrukturen.
- behave 1.3.3 erkennt `Gegeben` allein **nicht** als gültiges Given-Keyword — nur `Gegeben sei` und `Gegeben seien` sind registriert. `Gegeben` allein führt zu einem `ParserError`.

### Praktische Konsequenz

Alle Feature-Dateien unter `features/` sowie `docs/gherkin-step-phrase-reference-v1.md` verwenden `Angenommen` für alle Given-Schritte.

---

## 8. Verhältnis zu Architecture Decision Records (ADR)

Dieses Dokument ist bewusst kein ADR, sondern ein **Entwicklungshandbuch**. Ein ADR dokumentiert genau eine Entscheidung knapp und strukturiert (Kontext → Entscheidung → Konsequenzen → Status). Dieses Dokument erklärt mehrere zusammenhängende Prinzipien ausführlich und mit Begründung.

Dieses Dokument ist bewusst kein ADR, sondern ein **Entwicklungshandbuch**. Ein ADR dokumentiert genau eine Entscheidung knapp und strukturiert (Kontext → Entscheidung → Konsequenzen → Status). Dieses Dokument erklärt mehrere zusammenhängende Prinzipien ausführlich und mit Begründung.

Einzelne Entscheidungen aus diesem Dokument können bei Bedarf als formale ADRs unter `docs/adr/` nacherfasst werden — insbesondere wenn das Projekt wächst und Entscheidungen explizit versioniert oder für neue Teammitglieder nachvollziehbar gemacht werden sollen. Kandidaten wären:

- ADR-001: Backend vor Frontend in Phase 1
- ADR-002: Vertikale Slices statt horizontaler Schichten
- ADR-003: behave als BDD-Toolchain für Django

Diese drei ADRs sind unter `docs/adr/` erfasst.

---

## 9. Verbindung zu anderen Dokumenten

| Dokument | Rolle |
|---|---|
| `docs/project-foundation.md` §10 | Strategische BDD-Prinzipien, Kurzreferenz auf dieses Dokument |
| `docs/project-foundation.md` §11 | Architekturprinzipien (Schichtentrennung) |
| `docs/rule-set-v1.md` | Normative Quelle für alle Domänenlogik-Implementierungen |
| `features/` | Normative Grundlage für Step-Definitionen |
| `docs/gherkin-step-phrase-reference-v1.md` | Kanonische Step-Phrasen für Stub-Generierung |
