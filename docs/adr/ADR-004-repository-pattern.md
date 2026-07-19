# ADR-004: Repository Pattern zur Trennung von Domäne und Persistenz

**Status:** Akzeptiert  
**Datum:** 18.07.2026  
**Kontext:** TASK-003 — Persistenzschicht für Django ORM

---

## Kontext

Mit der Implementierung der Django ORM-Modelle (`models.py`, TASK-001) entstand die
Frage: Wo gehört der Code, der Domänenobjekte in Datenbankzeilen umwandelt und
umgekehrt?

Drei Alternativen wurden betrachtet:

**Option A — Direkt in `use_cases.py`**
```python
def spiel_anlegen(spieler, rundenanzahl=None) -> SpielModel:
    spiel = Spiel(...)
    return SpielModel.objects.create(...)  # ORM direkt im Use Case
```
Nachteil: Use Cases werden an Django gebunden. Behave-Tests brauchen eine echte
Datenbank. Domäne und Infrastruktur sind nicht mehr trennbar.

**Option B — Direkt in `views.py`**
ORM-Aufrufe landen im HTTP-Handler.
Nachteil: `views.py` hat zwei Verantwortlichkeiten (HTTP + Persistenz).
Persistenzlogik kann nicht ohne HTTP-Kontext wiederverwendet oder getestet werden.

**Option C — Separates Repository-Modul**
Ein eigenes `repositories.py` kapselt alle Datenbankoperationen.
Use Cases bleiben unverändert. Views orchestrieren: Use Case → Repository.

---

## Entscheidung

Wir verwenden **Option C: das Repository Pattern** (Martin Fowler,
*Patterns of Enterprise Application Architecture*, 2002; Eric Evans,
*Domain-Driven Design*, 2003).

`backend/scoring/repositories.py` ist die **einzige Stelle** im System,
die Domänenobjekte (`Spiel`, `Rundenausgang`) in ORM-Modelle umwandelt und
umgekehrt.

### Schichtenstruktur

```
views.py         HTTP-Schicht     empfängt Request, gibt Response zurück
    │
    ├── use_cases.py    Anwendungsschicht   reine Domänenfunktionen, kein Framework
    │
    ├── repositories.py Infrastruktur       ORM-Operationen, DB-Transaktionen
    │
    └── models.py       Datenbankschema     Django ORM-Modelle
```

**Abhängigkeitsregel:** Jede Schicht darf nur nach innen schauen, nie nach außen.
`use_cases.py` importiert kein Django. `domain.py` importiert gar nichts aus dem Projekt.

### Implementierte Repository-Funktionen

| Funktion | Slice | Richtung |
|---|---|---|
| `spiel_persistieren(spiel)` | 1 | Domain → DB |
| `spiel_laden(spiel_id)` | 1 | DB → Domain |
| `runde_persistieren(*, spiel_id, …)` | 2–5 | Domain-Ergebnis → DB |
| `punktestaende_laden(spiel_id)` | 6 | DB → aggregiertes Dict |

---

## Konsequenzen

**Positiv:**
- `use_cases.py` bleibt vollständig framework-frei und testbar ohne Datenbank.
- Alle 28 Behave-Szenarien laufen weiterhin ohne DB-Setup (0,011 s).
- Austauschbarkeit: Die Persistenzschicht kann gegen eine andere DB oder einen
  In-Memory-Store ausgetauscht werden, ohne `use_cases.py` oder `views.py` zu ändern.
- Klare Verantwortlichkeiten: Jede Datei hat genau einen Änderungsgrund.

**Negativ / Kompromisse:**
- Eine zusätzliche Datei (`repositories.py`) und damit mehr Dateien im Projekt.
- Bei sehr einfachen CRUD-Operationen wirkt die Trennung gelegentlich wie Overhead.
  Für dieses Projekt mit nicht-trivialer Domänenlogik (Rundenauswertung, Stich-Zwang,
  Verlustwertberechnung) überwiegen die Vorteile klar.

---

## Verwandte Entscheidungen

- ADR-002: Vertikale Slices — Repository-Funktionen werden Slice für Slice hinzugefügt
- ADR-001: Backend vor Frontend — Repository ist Teil des Backend-Kerns in Phase 1
