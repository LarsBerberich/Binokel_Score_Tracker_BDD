# Projektgrundlagen

## 1. Zweck dieses Dokuments

Dieses Dokument hält die grundlegenden Entscheidungen für das Projekt **Binokel Score Tracker** fest. Es schafft eine gemeinsame Ausgangsbasis für Produktrichtung, Domänenverständnis, Architektur, Entwicklungspraktiken und Qualitätsansprüche.

Sein Zweck ist es, sicherzustellen, dass zukünftige Implementierungsentscheidungen mit einer klaren Produktvision und einem wartbaren technischen Ansatz im Einklang bleiben.

---

## 2. Produktvision

Der **Binokel Score Tracker** ist eine Online-Anwendung zum Erfassen, Verwalten und Nachvollziehen von Spielständen für das traditionelle deutsche Kartenspiel **Binokel**.

Das Produkt soll das manuelle Anschreiben ersetzen oder verbessern, indem es bietet:

- eine zuverlässige und transparente Punkterfassung,
- einen intuitiven Ablauf während des laufenden Spiels,
- die Persistierung abgeschlossener Spiele,
- ein geringeres Risiko für Rechen- oder Übertragungsfehler,
- eine Grundlage für spätere Erweiterungen wie Spielerhistorie, Statistiken und Spielvarianten.

### Vision Statement

> Baue einen zuverlässigen, verständlichen und wartbaren Online-Score-Tracker für Binokel, der fachliche Klarheit mit modernen Software-Engineering-Praktiken wie BDD, sauberer Architektur, Automatisierung und testbarer Geschäftslogik verbindet.

---

## 3. Projektziele

### Primäre Ziele

- Digitale Punkterfassung für Binokel-Spiele ermöglichen.
- Die wesentlichen Wertungs- und Fachkonzepte des Spiels klar und korrekt modellieren.
- **BDD mit Gherkin** nutzen, um fachliches Verhalten in einer gemeinsamen Sprache zu beschreiben.
- Eine saubere, wartbare und testbare Codebasis aufbauen.
- Qualitätsprüfungen und Entwicklungsabläufe so früh wie möglich automatisieren.

### Sekundäre Ziele

- Praktische, KI-gestützte Entwicklungsabläufe kennenlernen und bewerten.
- Ein vorzeigbares Beispiel für diszipliniertes Software Engineering schaffen.
- Das Projekt auf zukünftiges Wachstum vorbereiten, ohne vorschnell zu überengineeren.

---

## 4. Nicht-Ziele

Die folgenden Punkte gehören **nicht zur initialen Projektbasis**, sofern sie nicht später ausdrücklich ergänzt werden:

- Echtzeit-Mehrspieler-Gameplay,
- die vollständige Umsetzung aller denkbaren regionalen Binokel-Regelvarianten,
- Social-Platform-Funktionen,
- ausgefeilte Ranglisten-Systeme,
- native Mobile-Apps,
- Offline-First-Synchronisation,
- umfassende Gamification-Funktionen.

Diese Themen können später Teil einer Roadmap werden, liegen aber außerhalb des Umfangs der ersten Grundlage und des MVP.

---

## 5. Zielgruppen

### Primäre Nutzer

- Kleine Spielergruppen, die Binokel-Punkte während oder nach einem Spiel digital erfassen möchten.
- Spieler, die eine klarere und weniger fehleranfällige Alternative zum papierbasierten Anschreiben suchen.

### Sekundäre Nutzer

- Wiederkehrende Spieler, die vergangene Spiele nachverfolgen möchten.
- Der Projekteigentümer bzw. Entwickler als Lernender und Wartender.

---

## 6. MVP-Umfang

Das MVP soll sich auf die kleinste zusammenhängende Funktionsmenge konzentrieren, die echten Nutzen liefert.

### Im MVP enthalten

- Ein neues Spiel anlegen.
- Teilnehmende Spieler oder Teams erfassen.
- Wertungsrelevante Ergebnisse rundenweise eingeben.
- Kumulative Spielstände berechnen und speichern.
- Den aktuellen Spielstand klar anzeigen.
- Ein Spiel beenden und das Endergebnis persistieren.
- Abgeschlossene Spiele nachträglich ansehen.

### Explizit außerhalb des MVP

- Benutzerkonten mit komplexen Berechtigungen,
- Live-Zusammenarbeit über mehrere Geräte,
- fortgeschrittene Analyse-Dashboards,
- Turnierverwaltung,
- gleichzeitige Unterstützung vieler Regelvarianten,
- Benachrichtigungssysteme,
- Chat- oder Community-Funktionen.

---

## 7. Domänenverständnis

Das Projekt soll die Fachdomäne ausdrücklich modellieren, anstatt Spielregeln, UI-Verhalten und Persistenzlogik miteinander zu vermischen.

### Zentrale Fachkonzepte

Die folgenden Konzepte werden voraussichtlich zentral sein:

- **Spiel** – eine vollständige Binokel-Partie.
- **Runde** – ein Wertungszyklus innerhalb eines Spiels.
- **Spieler** – ein einzelner Teilnehmender.
- **Team** – falls der gewählte Binokel-Modus mit Teams gespielt wird.
- **Wertungseintrag** – die wertungsrelevante Eingabe für eine Runde.
- **Gesamtstand** – der aufaddierte Punktestand über mehrere Runden.
- **Regelwerk** – die gewählte Wertungslogik oder Spielvariante.
- **Spielstatus** – zum Beispiel geplant, aktiv, abgeschlossen oder abgebrochen.

### Prinzip der Domänenmodellierung

Fachbegriffe müssen konsistent benannt und unabhängig von technischen Belangen wie Framework-Code, HTTP-Transport oder Datenbanklayout umgesetzt werden.

---

## 8. Gemeinsame Fachsprache

Eine gemeinsame Fachsprache sollte früh definiert und stabil gehalten werden.

### Erste Kandidaten für die gemeinsame Fachsprache

- **Spiel**: eine vollständige Partie
- **Runde**: ein ausgewerteter Spiel- bzw. Wertungszyklus
- **Punktestand**: ein numerisches Ergebnis in einem klaren Kontext
- **Wertungseintrag**: ein Eingabedatensatz, der zur Wertung beiträgt
- **Spieler**: eine am Spiel teilnehmende Person
- **Team**: eine Gruppe von Spielern, falls regelbedingt nötig
- **Regelwerk**: die gewählte Menge an Wertungsregeln
- **Stand**: der aktuelle kumulative Spielstand innerhalb einer Partie
- **Endergebnis**: das persistierte Ergebnis eines abgeschlossenen Spiels

### Regel

Wenn ein Fachbegriff mehrdeutig ist, muss er in der Dokumentation geklärt werden, bevor er sich in Code, Tests und UI-Texten verbreitet.

---

## 9. Funktionale Anforderungen

Auf hoher Ebene soll das System die folgenden Fähigkeiten unterstützen:

1. Eine neue Score-Tracking-Sitzung starten.
2. Teilnehmende definieren.
3. Wertungsinformationen pro Runde erfassen.
4. Aktuelle Gesamtstände konsistent berechnen.
5. Den aktuellen Stand anzeigen.
6. Ein Spiel abschließen und archivieren.
7. Frühere abgeschlossene Spiele abrufen.

### Beispielhafte User Stories

- Als Spieler möchte ich ein neues Spiel anlegen, damit ich mit der Punkteerfassung beginnen kann.
- Als Spieler möchte ich Ergebnisse rundenweise eingeben, damit der aktuelle Stand jederzeit sichtbar ist.
- Als Spieler möchte ich, dass die Anwendung Gesamtstände automatisch berechnet, damit ich manuelle Rechenfehler vermeide.
- Als Spieler möchte ich abgeschlossene Spiele später ansehen, damit ich frühere Ergebnisse nachvollziehen kann.

---

## 10. BDD-Strategie

BDD ist ein zentrales Projektprinzip und nicht nur eine Ergänzung für Tests.

### Ziele von BDD in diesem Projekt

- Ein gemeinsames Verständnis des Verhaltens schaffen, bevor implementiert wird.
- Fachliche Anforderungen in lesbarer Form ausdrücken.
- Geschäftsszenarien mit ausführbaren automatisierten Prüfungen verbinden.
- Den Fokus auf beobachtbares Verhalten statt auf interne Implementierungsdetails richten.

### Gherkin-Richtlinien

- Features beschreiben fachlich relevantes bzw. für Nutzer sichtbares Verhalten.
- Szenarien sollen konkret, klein und verständlich sein.
- Jedes Szenario soll genau ein fachliches Verhalten prüfen.
- Die Formulierung der Szenarien soll die gemeinsame Fachsprache des Projekts verwenden.
- Technische Implementierungsdetails gehören nicht in fachlich ausgerichtetes Gherkin.

### Empfohlene Struktur für Features

- Eine Feature-Datei pro zusammenhängender fachlicher Fähigkeit.
- Eine klare Feature-Beschreibung mit fachlicher Absicht.
- Szenarien mit Fokus auf Akzeptanzkriterien.
- `Background` nur dann, wenn er die Lesbarkeit verbessert.

### Trennungsprinzip

- **Gherkin** beschreibt die fachliche Absicht.
- **Integrations- bzw. Akzeptanztests** prüfen Verhalten über Systemgrenzen hinweg.
- **Unit-Tests** prüfen interne Regeln und Randfälle.

---

## 11. Architekturprinzipien

Das Projekt soll eine **einfache, explizite und modulare Architektur** bevorzugen.

### Empfohlene architektonische Richtung

Empfohlen wird eine pragmatische Schichten- oder Clean-Architecture mit klarer Trennung zwischen:

- **Domänenlogik**
- **Anwendungs- bzw. Use-Case-Orchestrierung**
- **Infrastruktur bzw. Adaptern**
- **Benutzeroberfläche bzw. API**

### Architekturregeln

- Fachlogik darf nicht direkt von UI- oder Datenbankdetails abhängen.
- Framework-spezifischer Code soll isoliert werden.
- Seiteneffekte sollen in die äußeren Schichten verschoben werden.
- Abhängigkeiten sollen nach innen in Richtung Domäne zeigen.
- Module sollen isoliert verständlich und testbar sein.

### Regel der anfänglichen Einfachheit

Die erste Version soll nicht überengineert werden. Architektur soll Klarheit schaffen, nicht unnötige Komplexität.

---

## 12. Technologierichtung

Auf Basis der aktuellen Repository-Beschreibung ergibt sich folgende vorläufige Technologierichtung:

- **Backend:** Python mit Django
- **Frontend:** Vue
- **Tests/BDD:** Gherkin-kompatible Werkzeuge plus automatisierte Testebenen

### Regel für Technologieentscheidungen

Technische Entscheidungen sollen unterstützen:

- Klarheit,
- Wartbarkeit,
- Testbarkeit,
- einfache Auslieferung,
- Automatisierung.

Wenn eine Technologie die Komplexität erhöht, ohne klaren Projektwert zu liefern, soll sie verschoben oder vermieden werden.

---

## 13. Nicht-funktionale Anforderungen

### Wartbarkeit

- Code soll lesbar, modular und bewusst strukturiert sein.
- Benennungen sollen fachlich orientiert und eindeutig sein.
- Komplexität soll minimiert werden.

### Testbarkeit

- Domänenlogik muss ohne schwergewichtiges Framework-Setup testbar sein.
- Akzeptanzkriterien sollen automatisierbar sein.
- Tests sollen schnell genug sein, um häufig ausgeführt zu werden.

### Zuverlässigkeit

- Punktberechnungen müssen deterministisch und überprüfbar sein.
- Persistierte Ergebnisse müssen konsistent sein.

### Benutzbarkeit

- Zentrale Eingabeworkflows für das Anschreiben müssen einfach und schnell sein.
- Die UI soll Mehrdeutigkeiten während des laufenden Spiels minimieren.

### Sicherheit

- Auch in frühen Phasen sollen sichere Grundeinstellungen verwendet werden.
- Geheimnisse dürfen nicht eingecheckt werden.
- Konfiguration soll umgebungsbasiert sein.

### Deploybarkeit

- Die Anwendung soll reproduzierbar gebaut und ausgerollt werden können.
- Umgebungsspezifischer Setup-Aufwand soll minimiert werden.

### Beobachtbarkeit

- Logging soll Debugging und Betriebsverständnis unterstützen.
- Fehler sollen sichtbar und nachvollziehbar sein.

---

## 14. 12-Factor-App-Prinzipien

Das Projekt soll sich, wo sinnvoll, an relevanten 12-Factor-Prinzipien orientieren.

### Erste Festlegungen

- Konfiguration über Umgebungsvariablen.
- Klare Abhängigkeitsverwaltung.
- Trennung von Konfiguration und Code.
- Reproduzierbare Build- und Run-Schritte.
- Zustandsarme Anwendungsprozesse, wo möglich.
- Logs als Ereignisströme behandeln.

---

## 15. Qualitätsstandards

### Definition of Done

Ein Arbeitsergebnis gilt erst dann als fertig, wenn:

- das Verhalten klar definiert ist,
- Akzeptanzkriterien vorhanden sind,
- die Implementierung abgeschlossen ist,
- automatisierte Tests ergänzt oder angepasst wurden,
- der Code die Qualitätsprüfungen besteht,
- die Dokumentation bei Bedarf aktualisiert wurde,
- die Änderung reviewbar und verständlich ist.

### Coding-Prinzipien

- Klarheit vor Cleverness.
- Funktionen und Klassen mit klarem Fokus.
- Versteckte Kopplung vermeiden.
- Explizite Benennung verwenden.
- Kontinuierlich refaktorisieren, wenn es die Klarheit verbessert.

### Review-Prinzipien

In Reviews soll geprüft werden:

- Korrektheit,
- Lesbarkeit,
- Übereinstimmung mit der Architektur,
- Testabdeckung des beabsichtigten Verhaltens,
- Konsistenz der Benennung,
- unnötige Komplexität.

---

## 16. Teststrategie

Die Teststrategie soll ein Gleichgewicht zwischen Vertrauen, Geschwindigkeit und Wartbarkeit schaffen.

### Testebenen

- **BDD- bzw. Akzeptanztests** für fachliches Ende-zu-Ende-Verhalten
- **Integrationstests** für das Zusammenspiel von Komponenten
- **Unit-Tests** für isolierte Fachregeln und Berechnungen

### Prinzipien der Teststrategie

- Wichtige Geschäftsregeln sollen zuerst abgedeckt werden.
- Die Domänenlogik für die Wertung soll stark auf Unit-Ebene abgesichert werden.
- Akzeptanzszenarien sollen sinnvolle Nutzerabläufe widerspiegeln.
- Testdaten sollen leicht verständlich sein.
- Fragile oder zu stark an Implementierungsdetails gekoppelte Tests sollen vermieden werden.

---

## 17. Automatisierung und CI/CD-Basis

Automatisierung soll früh eingeführt werden.

### Mindestanforderungen an CI

Jede sinnvolle Änderung soll perspektivisch automatisierte Prüfungen auslösen, zum Beispiel:

- Installation der Abhängigkeiten,
- Linting- bzw. Formatprüfungen,
- Unit-Tests,
- Integrations- und/oder Akzeptanztests, wo sinnvoll,
- Build-Verifikation.

### Erwartungen an Pull Requests

Vor dem Mergen soll eine Änderung:

- automatisierte Prüfungen bestehen,
- im Umfang verständlich sein,
- dem Änderungsumfang angemessene Tests enthalten,
- Architektur und Codequalität nicht verschlechtern.

---

## 18. Dokumentationsstrategie

Dokumentation soll leichtgewichtig, aber bewusst gepflegt werden.

### Empfohlenes Dokumentationsset

- `README.md` – Einstiegspunkt und Projektüberblick
- `docs/project-foundation.md` – grundlegende Entscheidungen
- `docs/ubiquitous-language.md` – gemeinsame Fachsprache
- `docs/architecture.md` – Architekturstruktur und Begründung
- `docs/adr/` – Architecture Decision Records für wichtige Entscheidungen

### Dokumentationsregel

Dokumentiert werden soll nur das, was Entscheidungen, Onboarding, Wartung oder gemeinsames Verständnis wirklich unterstützt.

---

## 19. Annahmen

Derzeit werden die folgenden Annahmen getroffen, die später validiert werden sollten:

1. Die erste Implementierung verwendet **Python/Django** für das Backend.
2. Die erste Implementierung verwendet **Vue** für das Frontend.
3. Das erste Ziel ist ein nutzbares MVP für das Anschreiben und nicht eine vollständige Spielplattform.
4. Zunächst wird genau **eine primäre Binokel-Regelauslegung** unterstützt, bevor mehrere Varianten betrachtet werden.
5. Der Repository-Eigentümer legt neben der Produktfunktionalität großen Wert auf Lernen und technische Qualität.

---

## 20. Offene Fragen

Die folgenden Fragen sollten früh geklärt werden:

1. Welche exakten Binokel-Regeln und welche Wertungslogik definieren Version 1?
2. Ist die Anwendung zunächst für lokale/private Nutzung gedacht oder für breiteren öffentlichen Mehrbenutzerzugang?
3. Werden Spieler zunächst nur innerhalb eines Spiels erfasst oder sollen früh persistente Spielerprofile existieren?
4. Nutzt das MVP Teams, Einzelwertung oder beides?
5. Soll Authentifizierung Teil des MVP sein oder ausdrücklich zurückgestellt werden?
6. Welches Deployment-Ziel ist zuerst vorgesehen?
7. Welche BDD-Toolchain soll für die Integration von Django und Vue gewählt werden?
8. Wie stark soll die UI von Anfang an für mobile Nutzung während des Live-Spiels optimiert werden?

---

## 21. Empfohlene nächste Schritte

1. Das README überarbeiten, damit es die Produktvision und die Engineering-Prinzipien klarer widerspiegelt.
2. `docs/ubiquitous-language.md` erstellen und die erste stabile Fachsprache definieren.
3. Die exakten Binokel-Regeln für Version 1 klären.
4. Eine erste Menge an MVP-User-Stories ableiten.
5. Die ersten Gherkin-Feature-Dateien für die wertvollsten Abläufe erstellen.
6. Die ersten Architektur- bzw. Modulgrenzen definieren und dokumentieren.
7. Die erste automatisierte Qualitätspipeline aufsetzen.

---

## 22. Leitprinzip

Im Zweifel bevorzugen wir:

- einfacheres Design,
- explizite Fachsprache,
- testbare Geschäftslogik,
- automatisierte Qualitätssicherung,
- inkrementelle Lieferung statt spekulativer Komplexität.
