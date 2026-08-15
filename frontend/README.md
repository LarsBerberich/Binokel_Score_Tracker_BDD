# Frontend – Binokel Score Tracker

Vue 3.5 + Vite + TypeScript (Composition API, `<script setup>`), Vue Router + Pinia,
Tailwind CSS v4, Vitest + Playwright. Fachlicher Kontext und Architektur: siehe `docs/`.

---

## Lokale Dev-Umgebung starten

Für die lokale Entwicklung laufen **zwei** Server parallel:

1. **Django-Backend** auf `127.0.0.1:8000` – liefert die API (`/api/…`, `/health/`).
2. **Vite-Dev-Server** auf `:5173` – liefert die SPA und **proxied** `/api` + `/health`
   an das Backend. Dev entspricht damit dem Prod-Same-Origin-Setup (ADR-010).

### 1. Backend starten

```bash
# aus dem Repo-Root
backend/.venv/bin/python backend/manage.py runserver 127.0.0.1:8000
```

### 2. Frontend starten (zweites Terminal)

```bash
# Node-Umgebung in JEDER neuen Shell laden (fnm, siehe ADR-012):
export PATH="$HOME/.local/bin:$PATH" && eval "$(fnm env)"

cd frontend
npm install        # nur beim ersten Mal bzw. nach Dependency-Änderungen
npm run dev
```

Anschließend im Browser öffnen: **http://localhost:5173/**

### Kurzcheck, dass alles läuft

```bash
curl -s -o /dev/null -w "index: %{http_code}\n" http://localhost:5173/
curl -s -w "\nhealth: %{http_code}\n"          http://localhost:5173/health/
# erwartet: index: 200  und  {"status": "ok"} / health: 200
```

---

## ⚠️ Fallstricke

- **Beide Server nötig.** Ohne laufendes Backend liefert der Vite-Proxy für `/api`-
  und `/health`-Aufrufe Fehler (z. B. 500/ECONNREFUSED). Immer **zuerst das Backend**,
  dann `npm run dev` starten.
- **fnm-Umgebung pro Shell laden.** `node`/`npm` sind erst nach
  `export PATH="$HOME/.local/bin:$PATH" && eval "$(fnm env)"` verfügbar. In einer neuen
  Shell ohne diesen Schritt schlägt `npm run dev` fehl bzw. nutzt eine falsche Node-Version.
  (Node-Version ist über `frontend/.node-version` = `22` gepinnt.)
- **Aus dem richtigen Verzeichnis starten.** `npm run dev` muss im `frontend/`-Ordner
  laufen (dort liegt die `package.json`). Ein Start eine Ebene höher bricht mit
  `ENOENT … package.json` ab.
- **Proxy-Ziel ist fix `127.0.0.1:8000`.** Läuft das Backend auf einem anderen Port,
  greift der Proxy nicht (siehe `vite.config.ts` → `server.proxy`).

---

## Nützliche Skripte

| Befehl              | Zweck                                             |
|---------------------|---------------------------------------------------|
| `npm run dev`       | Dev-Server mit HMR (`:5173`)                       |
| `npm run build`     | Production-Build inkl. Typecheck (`vue-tsc`)       |
| `npm run preview`   | Production-Build lokal ansehen                     |
| `npm test`          | Vitest (Unit/Komponenten) einmalig                 |
| `npm run test:watch`| Vitest im Watch-Modus                              |
| `npm run test:e2e`  | Playwright-E2E (`bddgen` + `playwright test`)      |

Teststrategie (Testpyramide, E2E-Budget): siehe `docs/adr/ADR-013-teststrategie-testpyramide.md`.
