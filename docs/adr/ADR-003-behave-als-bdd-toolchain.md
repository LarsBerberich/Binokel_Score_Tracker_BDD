# ADR-003: behave als BDD-Toolchain für Django

| Feld | Wert |
|---|---|
| **Status** | Accepted |
| **Datum** | 28.06.2026 |
| **Kontext** | Wahl der BDD-Testinfrastruktur für das Python/Django-Backend |

---

## Kontext

Das Projekt verwendet Python/Django als Backend und setzt BDD mit Gherkin als zentrales Entwicklungsprinzip ein. Die Gherkin-Feature-Dateien unter `features/` sind vollständig vorhanden. Es wird eine Toolchain benötigt, die:

- Gherkin-Syntax (`.feature`-Dateien) direkt ausführt,
- Django-Integration unterstützt,
- aktiv gepflegt und in der Python-Community etabliert ist.

Relevante Alternativen:

| Tool | Beschreibung |
|---|---|
| **behave** | Etabliertes BDD-Framework für Python, natives Gherkin, behave-django für Django-Integration |
| **pytest-bdd** | BDD-Plugin für pytest, Gherkin-Syntax, eng in pytest-Ökosystem integriert |
| **lettuce** | Älteres BDD-Framework für Python, heute weitgehend inaktiv |

## Entscheidung

**behave** in Verbindung mit **behave-django** als BDD-Toolchain.

Unit-Tests der Domänenlogik werden weiterhin mit **pytest** geschrieben (innere Schleife). behave und pytest ergänzen sich: behave für die äußere Akzeptanztest-Schleife, pytest für die innere Unit-Test-Schleife.

## Begründung

- **Natives Gherkin:** behave liest `.feature`-Dateien direkt. Die bestehenden Feature-Dateien unter `features/` können ohne Anpassung verwendet werden.
- **Explizite Trennung:** behave macht die Zweischleifigkeit (Akzeptanztest vs. Unit-Test) sichtbar und erzwungen — die äußere Schleife ist klar von pytest getrennt.
- **Django-Integration:** `behave-django` bietet Test-Client-Integration, Transaktionsisolation zwischen Szenarien und Zugriff auf den Django-ORM.
- **Reife und Stabilität:** behave ist seit Jahren aktiv gepflegt und in professionellen Python-Projekten weit verbreitet.

pytest-bdd wurde nicht gewählt, weil die engere pytest-Integration zwar Vorteile bei der Werkzeugkette bietet, aber die konzeptionelle Trennung zwischen äußerer (Akzeptanz) und innerer (Unit) Schleife weniger sichtbar macht.

## Konsequenzen

### Positiv
- Feature-Dateien sind unmittelbar ausführbar ohne Konvertierung.
- Klare Trennung: `behave` für Akzeptanztests, `pytest` für Unit-Tests.
- Django-Testinfrastruktur (Fixtures, Transaktionen) über behave-django verfügbar.

### Negativ / Risiken
- Zwei separate Test-Runner (`behave` und `pytest`) müssen in CI-Pipeline integriert werden.
- behave-django erfordert eine eigene Konfiguration (`environment.py`, Django-Settings für Tests).

### Abhängigkeiten
- `behave` (Kernpaket)
- `behave-django` (Django-Integration)
- `pytest` + `pytest-django` (Unit-Tests, innere Schleife)
