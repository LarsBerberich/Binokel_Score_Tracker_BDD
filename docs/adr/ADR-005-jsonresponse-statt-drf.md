# ADR-005: JsonResponse statt Django REST Framework für V1-API

**Status:** Akzeptiert  
**Datum:** 18.07.2026  
**Kontext:** TASK-004 — REST-Endpunkte (views.py + urls.py)

---

## Kontext

Für die HTTP-Schicht standen zwei Optionen zur Wahl:

**Option A — Django REST Framework (DRF)**
- Serializer, ViewSets, Browsable API, Pagination, Authentication-Klassen
- Etablierter Standard für Django REST APIs
- Zusätzliche Abhängigkeit (`djangorestframework`)

**Option B — Django `JsonResponse` + funktionsbasierte Views**
- Kein zusätzliches Framework, nur Django Core
- Manuelle JSON-Serialisierung und Fehlerbehandlung
- Volle Kontrolle ohne Framework-Magie

---

## Entscheidung

Wir verwenden **Option B: JsonResponse** mit funktionsbasierten Views für V1.

---

## Begründung

**YAGNI** (`docs/project-foundation.md`): DRF bringt Features mit, die V1 nicht braucht:
- Keine Auth in V1
- Keine Pagination (wenige Endpunkte, kleine Datenmenge)
- Keine Browsable API nötig (kein Kundenbetrieb)
- Keine generischen ViewSets (Domänenlogik ist nicht CRUD)

**Die Validierungslogik liegt bereits in `use_cases.py`.** DRF-Serializer würden
Validierungsregeln duplizieren, die im Domänenkern bereits korrekt und getestet sind.

**Geringe Endpunktanzahl** in V1:
```
POST   /api/spiele/
GET    /api/spiele/{id}/
POST   /api/spiele/{id}/runden/
GET    /api/spiele/{id}/punktestaende/
GET    /api/spiele/{id}/sieger/
```
Fünf Endpunkte rechtfertigen keinen Framework-Overhead.

---

## Konsequenzen

**Positiv:**
- Keine zusätzliche Abhängigkeit in `pyproject.toml`.
- Views sind leicht lesbar — kein Framework-Wissen nötig.
- Validierungsfehler aus Use Cases werden direkt als 400-Response weitergeleitet.
- Austausch auf DRF jederzeit möglich (Views sind thin wrapper über Use Cases + Repos).

**Negativ / Kompromisse:**
- Manuelle JSON-Deserialisierung und Fehlerbehandlung.
- Kein automatisches Schema / OpenAPI-Dokument.
- Wenn Auth, Throttling oder Pagination nötig werden, ist DRF die natürliche Migration.

---

## Sicherheitshinweis

Die Views verwenden `@csrf_exempt` für schreibende Endpunkte.
Dies ist für eine REST-API ohne Browser-Session-Auth die korrekte Lösung
(CSRF schützt formularbasierte Browser-Requests, nicht JSON-APIs).
Wenn in V2 Session-Authentifizierung hinzukommt, muss `@csrf_exempt` durch
DRFs `SessionAuthentication` oder ein Token-basiertes Schema ersetzt werden.

---

## Verwandte Entscheidungen

- ADR-001: Backend vor Frontend — API ist Phase-1-Ziel
- ADR-004: Repository Pattern — Views rufen Use Cases + Repositories auf
- FUTURE-001 (BACKLOG.md): DRF als Upgrade-Kandidat für V2
