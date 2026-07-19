# ADR-006: Behave-Akzeptanztests via HTTP (Blackbox) statt direkter Use-Case-Aufrufe

**Status:** Akzeptiert  
**Datum:** 19.07.2026  
**Kontext:** TASK-005/006 — Teststrategie für Akzeptanztests

---

## Kontext

Die bestehenden 28 Behave-Szenarien rufen Use Cases direkt aus Python auf:

```python
# Aktueller Stand — kein echter Blackbox-Test
from scoring.use_cases import spiel_anlegen
context.spiel = spiel_anlegen(["Anna", "Bernd", "Carla", "Dirk"])
```

Das funktioniert und testet die Domänenlogik korrekt. Es ist jedoch kein
vollständiger Akzeptanztest im Sinne von BDD — es testet eine interne Python-
Funktion, nicht das nach außen sichtbare Verhalten des Systems.

---

## Problem

Ein Step, der `use_cases.spiel_anlegen()` direkt aufruft, würde folgende Bugs
**nicht** entdecken:

- Ein Routing-Fehler in `urls.py` (falsche URL, falsche HTTP-Methode)
- Ein Parsing-Fehler in `views.py` (falsche Feldnamen, falscher Status-Code)
- Ein Fehler in `repositories.py` beim Speichern oder Laden
- Eine fehlende Datenbank-Transaktion
- Ein Integrationsfehler zwischen View, Use Case und Repository

Der Test sieht grün aus, obwohl das System als Ganzes kaputt wäre.

---

## BDD-Prinzip: Akzeptanztests testen beobachtbares Verhalten

Ein Gherkin-Szenario beschreibt das System aus Sicht eines Akteurs — es beschreibt
**was das System tut**, nicht **wie es intern aufgebaut ist**. Der Akteur interagiert
mit dem System über seine öffentliche Schnittstelle: die HTTP-API.

```
Gherkin-Szenario (Was der Akteur sieht)
    → HTTP POST /api/spiele/          (öffentliche Schnittstelle)
        → View                        (interne Implementierung — für den Test egal)
            → Use Case
                → Repository
                    → Datenbank
```

Solange ein Step `use_cases.spiel_anlegen()` direkt aufruft, testet er eine interne
Implementierungsebene. Das ist ein Unit-Test in Gherkin-Verkleidung.

Das Ziel von BDD ist der **saubere Blackbox-Test von außen**: Das Szenario kennt
nur Input und erwarteten Output — nicht den Weg dazwischen. Ändert sich die interne
Implementierung (z.B. Repository-Strategie), bleibt das Szenario unverändert.

---

## Entscheidung

Die Behave-Akzeptanztests werden **schrittweise** auf HTTP-basierte Tests umgestellt.
Jeder Step verwendet Djangos `TestClient`, der denselben vollständigen Stack
durchläuft wie ein echter HTTP-Request.

### Umsetzungsplan (Slice für Slice)

**TASK-005 (Vorstufe):** API-Integrationstests in `scoring/tests.py`
- Djangos `TestCase` + `TestClient`
- Testet denselben Stack wie HTTP-Behave-Tests
- Gibt sofort Sicherheit für die Views ohne Behave-Umbau
- Validiert, dass der HTTP-Stack grundsätzlich funktioniert

**TASK-006 (Hauptumbau):** Behave-Steps auf HTTP umstellen
- Beginn mit Slice 1 (`spiel_anlegen.feature`) — einfachste Steps
- Slice für Slice, in der Reihenfolge des Entwicklungsansatzes (§5)
- `features/environment.py`: Datenbanksetup/-teardown per Szenario
- `features/steps/`: Steps ersetzen Python-Aufrufe durch `context.client.post(...)`

### Datenbankisolation

Jedes Szenario erhält eine saubere Datenbank via Django's `TestCase`-Rollback-
Mechanismus (oder behave-django's eingebautem Support). Kein Szenario hinterlässt
Daten für das nächste.

---

## Konsequenzen

**Positiv:**
- Behave-Szenarien testen das System als vollständige Black Box.
- Interne Refaktorierungen (z.B. anderes ORM, anderes Repository) ändern keine
  einzige Feature-Datei — nur die Steps und die Implementierung.
- Ein grünes Szenario bedeutet: das Feature funktioniert von der HTTP-Schicht
  bis zur Datenbank.
- Konsistent mit dem BDD-Prinzip aus `docs/development-approach-v1.md` §2:
  "Outside-In Development — getrieben durch Akzeptanztests".

**Negativ / Kompromisse:**
- Tests werden etwas langsamer (Datenbank-Roundtrip pro Szenario statt reines
  Python).
- Step-Definitionen werden etwas ausführlicher (JSON bauen, Response parsen).
- Umbau ist Arbeit — deshalb Slice-für-Slice, nicht alles auf einmal.

**Übergangsregel:** Solange ein Step noch Use Cases direkt aufruft, bleibt er
gültig. Er wird in TASK-006 Slice für Slice ersetzt. Beide Varianten können
während des Übergangs koexistieren.

---

## Verwandte Entscheidungen

- ADR-003: behave als BDD-Toolchain — begründet den Einsatz von behave
- ADR-004: Repository Pattern — die Schicht, die HTTP-Tests erstmals vollständig abdecken
- ADR-005: JsonResponse — die HTTP-Schicht, die jetzt getestet wird
- `docs/development-approach-v1.md` §2 (Outside-In), §3 (RED-Green-Refactor)
