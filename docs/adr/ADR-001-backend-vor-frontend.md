# ADR-001: Backend vor Frontend in Phase 1

| Feld | Wert |
|---|---|
| **Status** | Accepted |
| **Datum** | 28.06.2026 |
| **Kontext** | Technische Entwicklungsreihenfolge für V1 |

---

## Kontext

Das Projekt verwendet Django als Backend und Vue als Frontend. Beide Schichten sind technisch klar getrennt. Die Gherkin-Spezifikation ist vollständig vorhanden und beschreibt fachliches Verhalten auf Domänenebene, nicht UI-Interaktionen. Die Domänenlogik (Rundenauswertung, Stich-Zwang, Verlustwertberechnung) ist komplex und fachlich präzise in `docs/rule-set-v1.md` spezifiziert.

Es stand die Entscheidung an, in welcher Reihenfolge die beiden Schichten entwickelt werden:

- **Option A:** Backend vollständig entwickeln, dann Frontend
- **Option B:** Frontend-Prototyp zuerst, Backend nachziehen
- **Option C:** Backend und Frontend parallel, Feature für Feature

## Entscheidung

**Option A: Backend vollständig in Phase 1, Frontend in Phase 2.**

Die gesamte Domänenlogik, Use-Case-Schicht und REST-API wird in Phase 1 implementiert und durch Akzeptanztests (`behave`) abgesichert. Das Vue-Frontend folgt in Phase 2 als Präsentationsschicht über die fertige API.

## Begründung

- Die Gherkin-Akzeptanztests laufen gegen das Backend — sie sind der natürliche Treiber für Phase 1 und benötigen kein Frontend.
- Fehler in der Domänenlogik sind gefährlicher als Fehler in der UI: Sie produzieren stille, falsche Ergebnisse. Daher muss der Kern zuerst korrekt und testgetrieben gebaut werden.
- Die API definiert den Kontrakt für das Frontend. Ein stabiler, getesteter API-Kontrakt vor dem Frontend-Start verhindert kostspielige Nachkorrekturen in der UI-Schicht.
- Die Domänenlogik ist vollständig vorab spezifiziert — der typische Vorteil eines Frontend-First-Ansatzes (frühes UX-Feedback zur Klärung offener Anforderungen) greift hier weniger.

## Konsequenzen

### Positiv
- Akzeptanztests treiben die gesamte Backend-Entwicklung.
- API-Kontrakt ist stabil, wenn das Frontend startet.
- Domänenlogik ist vollständig getestet, bevor sie in der UI sichtbar wird.
- Frontend kann bei Bedarf ausgetauscht werden, ohne die Kernlogik anzufassen.

### Negativ / Risiken
- Kein visuelles Feedback auf die UX bis Phase 2.
- API-Designfehler, die sich erst bei der UI-Entwicklung zeigen, erfordern Nachkorrekturen im Backend.

### Mitigation
Das Risiko von API-Designfehlern wird durch die Outside-In-Entwicklung (ADR-002 / `development-approach-v1.md`) minimiert: Die API wird nicht spekulativ designed, sondern ergibt sich aus den Use Cases, die die Akzeptanztests fordern.
