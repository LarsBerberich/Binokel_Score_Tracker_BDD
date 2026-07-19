# Agenten-Orchestrierung — Binokel Score Tracker

Dieses Dokument beschreibt, wie die drei Copilot-Agenten zusammenarbeiten.

---

## Die drei Agenten im Überblick

| Agent | Kernaufgabe | Entscheidungsmacht |
|---|---|---|
| **Coding-Agent** | Features implementieren, Bugs beheben, Code-Änderungen | Implementierungsentscheidungen innerhalb der Architekturleitlinien |
| **Rubber-Duck-Agent** | Pläne und Änderungen kritisch prüfen, Risiken benennen | Veto bei erkannten Architekturbrüchen oder hohen Risiken |
| **Dev/Ops-Agent** | CI/CD, Deployment, Server-Betrieb | Infrastruktur- und Release-Entscheidungen |

---

## Orchestrierungs-Workflow

```
Neue Aufgabe eingeht
        │
        ▼
┌─────────────────────────────────────────┐
│  Schritt 1: Aufgabe klassifizieren      │
│                                         │
│  Fachlich/Code?   →  Coding-Agent       │
│  Infra/Deploy?    →  Dev/Ops-Agent      │
│  Beides?          →  beide parallel     │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│  Schritt 2: Zuständiger Agent plant     │
│                                         │
│  - Coding-Agent: Entwurf mit Testplan  │
│  - Dev/Ops-Agent: Pipeline + Runbook   │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│  Schritt 3: Rubber-Duck-Agent prüft    │
│                                         │
│  Bei mittlerem/hohem Risiko:            │
│  - Architekturkonformität?              │
│  - Randfälle abgedeckt?                 │
│  - Rollback definiert?                  │
│  - Sicherheitsrisiken?                  │
│                                         │
│  Ergebnis: Freigabe ODER Nacharbeits-  │
│  liste zurück an Schritt 2             │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│  Schritt 4: Implementierung             │
│                                         │
│  Coding-Agent implementiert Code.       │
│  Dev/Ops-Agent baut/ändert Pipeline.   │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│  Schritt 5: Qualitätsgating            │
│                                         │
│  - CI läuft automatisch (28 Szenarien) │
│  - Rubber-Duck-Agent reviewed bei PR   │
│  - Dev/Ops-Agent gibt Release frei     │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│  Schritt 6: Release (bei Deploy)       │
│                                         │
│  - CD-Pipeline läuft                   │
│  - Dev/Ops-Agent überwacht Healthcheck │
│  - Rollback bei Fehler                 │
└─────────────────────────────────────────┘
```

---

## Übergabe-Protokoll zwischen Agenten

### Coding-Agent → Rubber-Duck-Agent

```
Übergabe-Artefakt:
  - Geänderte Dateien (Liste)
  - Teststatus (behave-Ergebnis)
  - Bekannte Risiken oder offene Fragen
  - Architekturentscheidungen (neue ADRs?)
```

### Rubber-Duck-Agent → Coding/Dev/Ops-Agent

```
Rückgabe-Artefakt:
  - Freigabe: JA / NEIN
  - Falls NEIN: Nacharbeits-Liste (nummeriert, priorisiert)
  - Risiken mit Schwere: HOCH / MITTEL / NIEDRIG
  - Offene Fragen, die entschieden werden müssen
```

### Dev/Ops-Agent → Rubber-Duck-Agent (bei riskanten Infra-Änderungen)

```
Übergabe-Artefakt:
  - Geplante Infrastruktur-Änderung
  - Betroffene Dienste / Ausfallzeit
  - Rollback-Plan
  - Erwartete Betriebsauswirkung
```

### Dev/Ops-Agent → Coding-Agent

```
Übergabe-Artefakt:
  - Neue Env-Variablen, die der Code lesen muss
  - Neue Service-Abhängigkeiten (z. B. Redis, Datenbank)
  - Deployment-Anforderungen (z. B. collectstatic, migrate)
```

---

## Aktivierungsregeln

### Wann wird der Coding-Agent aktiviert?

- Neue Feature-Implementierung
- Bug-Fixes in Fachlogik oder API
- Refactoring
- Gherkin-Szenarien erweitern
- Datenbankmodelle ändern

### Wann wird der Dev/Ops-Agent aktiviert?

- CI/CD-Workflow ändern oder erweitern
- Server-Konfiguration anpassen
- Secrets oder Env-Variablen verwalten
- Neuen Service deployen
- Rollback oder Incident-Response
- Monitoring oder Backup einrichten

### Wann wird der Rubber-Duck-Agent aktiviert?

- **Immer** vor einem PR-Merge in `main`
- **Immer** vor einer Infrastruktur-Änderung, die Downtime riskiert
- **Immer** wenn ein Agent bei einer Entscheidung unsicher ist
- Optional: vor der Planung einer neuen Domänenlogik

---

## Session-Start- und Session-Ende-Konvention

Für alle Agenten verbindlich (Normative Quelle: `docs/project-foundation.md` §18):

- **Session-Start**: Zuerst `BACKLOG.md` im Repo-Root lesen, um den aktuellen Arbeitsfokus zu erfassen.
- **Session-Ende**: `BACKLOG.md`, `docs/copilot-handover-v1.md` und die Repo-Memory (`/memories/repo/handover-status.md`) immer **synchron** aktualisieren, damit der Projektstand konsistent bleibt.

---

## Nicht-triviale Entscheidungen — Eskalationsregel

Wenn ein Agent auf eine Entscheidung stößt, die außerhalb seines Verantwortungsbereichs liegt oder auf die die vorhandene Dokumentation keine klare Antwort gibt:

1. Entscheidung **explizit benennen** (kein stilles Durchentscheiden)
2. Rubber-Duck-Agent um Einschätzung bitten
3. Wenn nötig: ADR anlegen (`docs/adr/ADR-NNN-*.md`)
4. Erst danach implementieren

---

## Bezug zur Projektdokumentation

| Dokument | Relevanz |
|---|---|
| `docs/project-foundation.md` §17 | Mindestanforderungen an CI |
| `docs/development-approach-v1.md` | Entwicklungszyklus, Phasenmodell |
| `BACKLOG.md` | Aktueller Arbeitsfokus |
| `docs/agents/coding-agent.md` | Detailbeschreibung Coding-Agent |
| `docs/agents/rubber-duck-agent.md` | Detailbeschreibung Rubber-Duck-Agent |
| `docs/agents/devops-agent.md` | Detailbeschreibung Dev/Ops-Agent |
| `deploy/README.md` | Deployment-Runbook |
