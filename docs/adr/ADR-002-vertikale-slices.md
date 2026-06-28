# ADR-002: Vertikale Slices statt horizontaler Schichten

| Feld | Wert |
|---|---|
| **Status** | Accepted |
| **Datum** | 28.06.2026 |
| **Kontext** | Interne Implementierungsreihenfolge innerhalb von Phase 1 |

---

## Kontext

Innerhalb von Phase 1 (Backend-Kern) müssen 6 Feature-Dateien implementiert werden. Es gibt zwei grundlegende Ansätze für die Implementierungsreihenfolge:

- **Option A — Horizontale Schichten:** Erst alle Domänenklassen für alle Features, dann alle Use Cases, dann alle API-Endpunkte.
- **Option B — Vertikale Slices:** Feature für Feature als vollständigen Schnitt durch alle Schichten (Domänenlogik → Use Case → API).

## Entscheidung

**Option B: Vertikale Slices.**

Jede Feature-Datei treibt einen vollständigen vertikalen Schnitt durch alle Schichten. Die Reihenfolge der Features ist in `docs/development-approach-v1.md` §5 festgelegt.

## Begründung

- **Kontinuierliches Feedback:** Nach jeder abgeschlossenen Slice laufen die zugehörigen Akzeptanztests grün. Man weiß sofort, ob die gewählte Architektur trägt.
- **Frühzeitige Fehlererkennung:** Inkonsistenzen zwischen Domänenmodell, Use-Case-Schicht und API-Design zeigen sich nach der ersten Slice — nicht erst nach Wochen horizontaler Arbeit.
- **Lauffähiges System zu jedem Zeitpunkt:** Nach Slice 1 (`spiel_anlegen`) existiert bereits ein vollständig testbares Teilsystem.
- **Alignment mit BDD:** Jede Feature-Datei entspricht genau einer Slice. Der Übergang von Gherkin zu Implementierung ist direkt und nachvollziehbar.

Horizontale Schichten hätten einen langen Zeitraum ohne lauffähige Software und ohne Integrationsfeedback bedeutet.

## Konsequenzen

### Positiv
- Immer lauffähiges, testbares Teilsystem nach jeder Slice.
- Frühzeitiger Nachweis der Architektur durch echte Integration.
- Direkte Traceability von Feature-Datei zu Implementierungs-Slice.

### Negativ / Risiken
- Horizontale Querschnittsthemen (Datenbankzugriff, Fehlerbehandlung, Basisklassen) müssen vor der ersten Slice einmalig aufgesetzt werden.
- Ohne Disziplin können Domänenklassen früh zu allgemein oder zu spezifisch gestaltet werden.

### Mitigation
YAGNI und RED-Green-Refactor verhindern übermäßige Verallgemeinerung: Domänenklassen entstehen nur durch die konkreten Anforderungen der aktuellen Slice. Verallgemeinerungen erfolgen ausschließlich im REFACTOR-Schritt, wenn der Bedarf durch mindestens zwei Slices belegt ist.
