# Backlog – Binokel Score Tracker V1

> **Workflow:** Session startet → diese Datei lesen → sofort im Bild.  
> Session endet → `BACKLOG.md` + `docs/copilot-handover-v1.md` + `/memories/repo/handover-status.md` synchron aktualisieren.

---

## ▶ Aktueller Fokus

**Phase 2 (Frontend, Vue) läuft.** **TASK-007a** (Same-Origin-Infrastruktur, ADR-010/011)
und **TASK-007** (Vue-Fundament) sind **abgeschlossen**: `frontend/` steht mit Vite + Vue 3
+ TS, Router + Pinia, Tailwind v4, handgeschriebenem OpenAPI 3.1, dünnem fetch-API-Client
(Same-Origin), Vitest (Smoke grün), genau **1** Playwright-E2E-Smoke, Vite-Dev-Proxy
(`/api`+`/health` → Django) und CI-Jobs `frontend` + `frontend-e2e`. **Teststrategie
verbindlich festgelegt: ADR-013** (Fachlichkeit auf API-Ebene, E2E-Budget ≤ 3–5 bis MVP).
**TASK-008** (Spiel anlegen – UI, Slice 1) **abgeschlossen**: `StartView` mit
Formular-Komponente `SpielAnlegenForm` (4 Spieler + Rundenanzahl, Client-Validierung),
`spiel`-Pinia-Store, `spielAnlegen()`-Aufruf → Navigation zu `/spiel/:spielId`; 11 Vitest
grün (Formular-Unit + StartView-Integration). **TASK-009** (Runde eingeben und auswerten –
UI, Slices 2–5) **abgeschlossen** (009.1–009.6): Geber-Rotation-Domänenmodul
(`domain/rotation.ts`), Regelkonstante `domain/regeln.ts` (`STICHWERT_KONTROLLSUMME = 250`),
`RundeForm`-Komponente für alle fünf Rundentypen (normal, einfaches/doppeltes Abgehen,
Tausender gewonnen/verloren), `SpielView` mit Rundenfortschritt, Geber-Anzeige,
letztem Ergebnis und Link zur Auswertung bei Spielende; 26 Vitest grün, alle fünf
Rundentypen zusätzlich per curl gegen das echte Backend verifiziert (201). **TASK-010**
(Spielstand anzeigen – UI, Slice 6, Punktestände) **abgeschlossen**: `SpielView` lädt nach
jeder Runde und beim Öffnen die Punktestände (`punktestaendeLaden`) und zeigt sie absteigend
sortiert (Führender hervorgehoben); 27 Vitest grün, per curl verifiziert (200). **TASK-011**
(Spiel abschließen / Sieger anzeigen – UI, Slice 6) **abgeschlossen**: `SpielendeView` ruft
`siegerErmitteln()` auf, zeigt Sieger (auch mehrere bei Gleichstand) + absteigenden Endstand
+ „Neues Spiel"; 30 Vitest grün, per curl verifiziert (200). **Damit ist der Phase-2-MVP-Loop
komplett** (Spiel anlegen → Runden aller Typen → Punktestand → Sieger). **Erstes Durchspielen
mit USER-Feedback erfolgt** → daraus **Phase 2b** geplant (TASK-012/013/014): Rundenerfassung
regelkonform verfeinern. **Häppchen A von TASK-012 (012.1/012.2/012.4/012.6) umgesetzt +
validiert** (Reizwert-Minimum 150 als Hausregel in `rule-set-v1.md` §7 + `ubiquitous-language.md`
verankert). **Häppchen B von TASK-012 (012.3/012.5/012.7) umgesetzt + validiert** — Stichwerte
jetzt **1er-genau** (`step=1`, Korrektur: knappe Spiele erfordern exaktes Zählen, §9.1/§17.2
aktualisiert), dritter Stichwert automatisch read-only, `hat_eigenen_stich` aus Stichwert
abgeleitet, doppeltes-Abgehen-Hinweis; 33 Vitest grün, Build grün, curl 201/200. **TASK-012
komplett.** **Nächster Schritt: Rubber-Duck-Review von Häppchen B, danach TASK-013 (Sterne,
Prio vor 014).**

**Plausibilitätsregel Meldepunkte (15.08.2026, aus Live-Test):** Die Meldepunkte eines einzelnen
Spielers sind auf **0–1800** begrenzt (theoretisches Maximum: doppelte Familie 1500 + doppelter
Binokel 300; `rule-set-v1.md` §7.1). Durchgesetzt in Domäne/Use Case/View (HTTP 400) und im
`RundeForm`-UI (Absenden gesperrt + Hinweis); OpenAPI-Vertrag + `ubiquitous-language.md` §4.9
nachgezogen. 22 Django + 28 Behave + 35 Vitest grün, Build grün, live-curl 1801→400/1800→201.

**TASK-006 abgeschlossen. TASK-CI-006 (erster Produktions-Deploy) erfolgreich: App läuft prod auf `api.bebe-soft.de` (CD #30/#31 GREEN, Post-Deploy-Smoke-Test automatisiert). Verbleibende Go-Live-Governance-/Ops-Nacharbeiten sind hinter Phase 2 eingeordnet → `TASK-CI-007`…`TASK-CI-010`.**

**TASK-CI-001–005 — CI/CD-Pipeline + Betriebsfundament fertig.**

**TASK-CI-006 — Trockenlauf gegen Wegwerf-VM erfolgreich durchgeführt (21.07.2026).**
Der komplette Deploy-Pfad wurde real gegen eine Wegwerf-VM (`staging.bebe-soft.de`,
Certbot `--staging`) durchgespielt und lieferte am Ende `health-https: 200`. Dabei traten
**sechs** weitere reale Blocker auf (gunicorn-Dep, Deploy-env, `/etc/binokel`-Traversal,
uv-Interpreter im Deploy-Home/`203/EXEC`, Gunicorn-Control-Server-`HOME`, Nginx-Host-Header)
— alle behoben. Anschließend fand ein **Rubber-Duck-Security-Review** zwei prod-blockierende
Punkte (K1 sudo-`status`-Root-Escape, K2 fail-open SECRET_KEY) + fünf Verschärfungen (E1–E5)
— ebenfalls alle behoben. Details: `docs/engineering-notes/ENG-004-...` + ADR-009-Nachträge.
Betriebssystem-Basis: **Ubuntu 24.04 LTS**. **Nächster Schritt: Teardown der Wegwerf-VM,
dann realer Produktions-Deploy** (reale Domain, ohne `CERTBOT_STAGING`).

---

## Offen / Priorisiert

### Phase 1 – Backend (Outside-In, Slice für Slice)

- [x] **TASK-001** `models.py` — Django ORM-Modelle angelegt (18.07.2026)
  - `SpielModel`, `SpielerModel`, `RundeModel`, `GegenspielerRundeModel`
  - UniqueConstraints für Position, Rundennummer und Gegenspieler pro Runde
  - `_RUNDENAUSGANG_CHOICES` von `domain.Rundenausgang` abgeleitet (Single Source of Truth)

- [x] **TASK-002** Datenbankmigrationen erzeugt und angewendet (18.07.2026)
  - `scoring/migrations/0001_initial.py`
  - `python3 manage.py migrate` — alle Migrationen OK
  - 28/28 Behave-Szenarien weiterhin GREEN

- [x] **TASK-003** Use Cases an ORM ankoppeln (18.07.2026)
  - `backend/scoring/repositories.py` neu angelegt
  - `spiel_persistieren`, `spiel_laden`, `runde_persistieren`, `punktestaende_laden`
  - Use cases bleiben pure Funktionen (keine Änderung an `use_cases.py`)
  - 28/28 Behave-Szenarien weiterhin GREEN

- [x] **TASK-004** REST-Endpunkte implementiert (18.07.2026)
  - `backend/scoring/views.py` — 5 Views (JsonResponse, keine DRF-Abhängigkeit)
  - `backend/binokel_tracker/urls.py` — 6 URL-Muster registriert
  - `docs/adr/ADR-005-jsonresponse-statt-drf.md` — Entscheidung dokumentiert
  - Toten Code in `use_cases.py` entfernt
  - Bug in `repositories.py` behoben (Gegenspieler-Punkte korrekt aggregiert)
  - 28/28 Behave-Szenarien weiterhin GREEN

- [x] **TASK-005** API-Integrationstests in `scoring/tests.py` (TestCase + TestClient) — 19.07.2026
  - 18 Tests, alle GREEN
  - `SpielAnlegenApiTest`, `RundeAuswertenApiTest`, `PunktestaendeUndSiegerApiTest`
  - Normative Quelle: ADR-006

- [x] **TASK-006** Behave-Steps Slice 1 auf HTTP umgestellt, Infrastruktur für alle weiteren Slices bereitgestellt — 19.07.2026
  - `features/environment.py`: Test-Datenbank-Setup + `context.client` pro Szenario + Cleanup
  - `features/steps/spiel_anlegen_steps.py`: vollständige HTTP-Migration (ADR-006)
  - Slices 2–5: Domänen-Steps bleiben (testen interne Berechnungsregeln, nicht HTTP-sichtbar)
  - Slice 6: Domänen-Steps bleiben (Punktestände werden direkt gesetzt, keine passenden HTTP-Endpunkte)
  - Normative Quelle: ADR-006

### Phase 1 – DevOps / CI/CD

- [x] **TASK-CI-001** GitHub Actions CI-Workflow (19.07.2026)
  - `.github/workflows/ci.yml` — Django-Check + 28 BDD-Szenarien auf jedem Push/PR
  - Verwendet `uv` und Python 3.14 (entspricht `.python-version`)

- [x] **TASK-CI-002** GitHub Actions CD-Workflow (19.07.2026)
  - `.github/workflows/cd.yml` — SSH-Deploy auf 1&1 VM nach CI-Erfolg auf `main`
  - rsync + Migrationen + collectstatic + systemd-Restart + Healthcheck + Rollback

- [x] **TASK-CI-003** Django-Settings produktionsreif (19.07.2026)
  - `settings.py` liest Konfiguration aus Env-Vars (SECRET_KEY, DEBUG, ALLOWED_HOSTS, …)
  - Production-Sicherheitseinstellungen (HSTS, Secure Cookies) bei `DEBUG=False`
  - `/health/`-Endpunkt in `urls.py` für Deployment-Healthchecks

- [x] **TASK-CI-004** Server-Setup und Betriebsdokumentation (19.07.2026)
  - `deploy/setup-server.sh` — Einmal-Setup für VM (Debian/Ubuntu)
  - `deploy/binokel-tracker.service` — systemd-Unit (Gunicorn)
  - `deploy/nginx.conf.template` — Nginx mit TLS
  - `deploy/README.md` — vollständiges Betriebsrunbook

- [x] **TASK-CI-005** Agenten-Orchestrierung dokumentiert (19.07.2026)
  - `docs/agents/coding-agent.md` — Rollenbeschreibung Coding-Agent
  - `docs/agents/rubber-duck-agent.md` — Rollenbeschreibung Rubber-Duck-Agent
  - `docs/agents/devops-agent.md` — Rollenbeschreibung Dev/Ops-Agent
  - `docs/agents/orchestration.md` — Workflow für alle 3 Agenten (Coding, Rubber-Duck, Dev/Ops)
  - ADR-007 (GitHub Actions CI/CD), ADR-008 (VM-Deployment-Strategie)

- [x] **TASK-CI-006** VM einrichten + erster Produktions-Deploy — **erfolgreich (22.07.2026)**: App live auf `https://api.bebe-soft.de` (echtes Let's-Encrypt-Cert), CD-Läufe #30/#31 GREEN, Post-Deploy-Smoke-Test automatisiert (letzter Commit `e8cd217`)
  - **Ausführungsanleitung:** `deploy/runbook-task-ci-006.md` (Phasen 0–6 mit Verifikation + Rollback)
  - Ziel-Infrastruktur: neue 1&1/IONOS-VM mit frischem Ubuntu LTS (z. B. 24.04)
  - Phase 1: Internet-Hardening (Admin-User, SSH-Key-only, sshd-Härtung) — manuell (ADR-009)
  - Phase 2: VM mit `deploy/setup-server.sh` initialisieren (inkl. fail2ban, unattended-upgrades, chrony)
  - Phase 3: `/etc/binokel/env` mit Produktionskonfiguration befüllen (600 root:root + gezielte ACL für binokel-deploy)
  - Phase 4: Deploy-SSH-Key + GitHub-Secrets `VM_SSH_KEY`, `VM_HOST`, `VM_USER`, `VM_SSH_KNOWN_HOSTS`
  - Phase 5: Branch Protection für `main` aktivieren (ADR-007)
  - Phase 6: Ersten Deploy manuell auslösen (CD → workflow_dispatch, confirm=yes) und verifizieren
  - Rubber-Duck-Review erfolgt (21.07.2026): 5 Blocker behoben — `settings.py` (Redirect-Loop), `setup-server.sh` (Certbot-Reihenfolge + uv-Pfad + POSIX-ACL-Schreibrechte + Backup-Cron), `nginx.conf.template` (Healthcheck); `known_hosts` jetzt Pflicht, sudoers `/usr/bin/systemctl`. Fallstricke: `docs/engineering-notes/ENG-004-deployment-hardening-fallstricke.md`
  - Betriebssystem-Basis: **Ubuntu 24.04 LTS** (ADR-008)
  - **Trockenlauf (21.07.2026) erfolgreich:** kompletter Pfad gegen Wegwerf-VM durchgespielt (Certbot `--staging`), `health-https: 200`. 6 weitere Blocker gefunden+behoben (gunicorn-Dep, Deploy-env, `/etc/binokel`-x-ACL, uv-Interpreter/`UV_PYTHON_INSTALL_DIR`, Gunicorn-`HOME`, Nginx-Host-Header). Danach Security-Review: K1/K2 (blockierend) + E1–E5 behoben. Commits: 5d6c5e3, 991c493, f486ade, c37dc30, bbd07e3, ded2e13 (+Security-Commit).
  - **IONOS-Security-Review (22.07.2026):** Best-Practice-PDFs → Compliance-Matrix `docs/security/ionos-baseline-check.md`; Rubber-Duck-Audit. Umgesetztes **Go-Live-Gate**: (a) konsistentes SQLite-Backup `sqlite3 .backup` + `integrity_check` + atomarer `mv` + journald-Logging (`/usr/local/bin/binokel-backup.sh`, `setup-server.sh`) statt `cp`; (b) `/admin/`-Route in V1 deaktiviert (RD-6); (c) HSTS `preload`/`includeSubDomains` vorerst zurückgenommen (RD-8); (d) Restore-Probe als Runbook-Schritt 6.2. Offener Blocker: **IONOS-Cloud-Panel-Ports 8000/8443/8447 schließen** (Betreiber-Aktion, #9).
  - **Erledigt:** Teardown Wegwerf-VM + Test-DNS entfernt; realer Prod-Deploy gegen reale Domain ohne `CERTBOT_STAGING` durchgeführt und via Smoke-Test verifiziert.
  - **Restaufgaben (Go-Live-Governance/Ops)** bewusst hinter Phase 2 gezogen → `TASK-CI-007`…`TASK-CI-010`.
  - V1 nutzt SQLite; Docker + PostgreSQL als späterer Meilenstein (ADR-008)

### Phase 2 – Frontend (Vue) — in Arbeit (Start 23.07.2026)

> **Stack (ADR-011):** Vue 3.5 + Vite + TypeScript + Vue Router + Pinia + Tailwind CSS,
> PWA (`vite-plugin-pwa`) + Capacitor-ready, mobil-first. **Deployment (ADR-010):**
> Same-Origin auf einer Domain (`binokel.bebe-soft.de`), Nginx serviert SPA + proxied
> `/api/`; alte API-Domain 301 → Primärdomain. **BDD/E2E:** Playwright + playwright-bdd.
> **API-Vertrag:** handgeschriebenes OpenAPI 3.1 (Auto-Schema = FUTURE-002).
>
> **Teststrategie-Leitplanke (ADR-011):** fachliche Abdeckung bleibt schwerpunktmäßig
> auf der API-Ebene (18 Django + 28 Behave). E2E (Playwright) bewusst schlank halten
> (kritische Journeys/Smoke). **Vor** dem breiten Ausbau der playwright-bdd-Szenarien
> mit dem Repo-Eigentümer final abstimmen (offener Gesprächspunkt).

- [x] **TASK-007a** Phase-0-Infrastruktur (Same-Origin) — 23.07.2026
  - `deploy/nginx.conf.template`: SPA-Root `/opt/binokel/frontend`, `try_files`-Fallback,
    `/api/`-Proxy, `/assets/`-Immutable-Cache, `index.html` `no-cache`; zweiter
    Server-Block 301 (API-Domain → Primärdomain), gemeinsames SAN-Zertifikat.
  - `deploy/setup-server.sh`: `/opt/binokel/frontend` + `www-data`-rX-ACL (+Default),
    optionale `API_DOMAIN` (SAN-Cert + Zwei-Domain-Substitution, Sentinel-Block-Stripping
    im Ein-Domain-Modus). `bash -n` OK, beide Render-Modi verifiziert.
  - Doku: ADR-010, ADR-011, ENG-005, `project-foundation.md` §20 aktualisiert.
  - **Offen (Live-Cut-Over, USER/Betreiber):** DNS `binokel.bebe-soft.de`; einmalige
    Cert-Migration auf gemeinsame SAN-Lineage; `cd.yml`-Smoke-Test auf Primärdomain
    umstellen; `DJANGO_ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` beide Domains.
- [x] **TASK-007** Vue-Anwendung aufsetzen (Vite-Scaffold `frontend/`), API-Client + handgeschriebenes OpenAPI 3.1, Tailwind + Router + Pinia, Vitest + Playwright-Grundgerüst
  - [x] **007.0 Toolchain:** Node-Bereitstellung via **fnm** (verifizierte Binary, kein sudo) — fnm `v1.39.0`, Node `v22.23.1`, npm `10.9.8`; `fnm env --use-on-cd` in `~/.bashrc`. Entscheidung: **ADR-012**. Version pinnen mit `frontend/.node-version` (+ `engines` in `package.json`) im Scaffold-Schritt.
  - [x] **007.1 Scaffold:** `npm create vite@latest frontend -- --template vue-ts` (Vue 3.5, Vite 8, TS); `.gitignore` deckt `node_modules`/`dist` ab; `frontend/.node-version` = `22` + `engines.node` `>=22 <23` in `package.json`; `npm install` (0 Vulnerabilities), `npm run build` grün (Smoke)
  - [x] **007.2 Router + Pinia:** `vue-router@4` (History-Mode, `src/router/index.ts`) + `pinia` in `main.ts` registriert; leere Route-Struktur `start` (Slice 1) / `spiel/:spielId` (Slices 2–5) / `spielende` (Slice 6) + 404-Fallback; Platzhalter-Views lazy-geladen; `App.vue` → `<RouterView>`; Build grün (Code-Splitting bestätigt)
  - [x] **007.3 Tailwind:** Tailwind CSS **v4** via `@tailwindcss/vite`-Plugin (keine PostCSS-Config); `@import 'tailwindcss'` + mobile-first Basis (`min-h-dvh`, `max-w-screen-sm`) in `style.css`; Scaffold-Demo-CSS entfernt; Smoke-Style in `StartView`; Build grün, Utilities im Output verifiziert
  - [x] **007.4 API-Vertrag:** `frontend/openapi/binokel-api.v1.yaml` — handgeschriebenes **OpenAPI 3.1** aus `urls.py` + `views.py`; 5 API-Endpunkte + `/health/`, 15 Schemata; `runden`-Body mit `oneOf`+Discriminator (5 Rundentypen); YAML- und `$ref`-Integrität geprüft (17 Refs, 0 dangling). PFLICHT: bei View-Änderungen nachziehen
  - [x] **007.5 API-Client:** dünner `fetch`-Client (`src/api/`) — relative Basis `/api` (Same-Origin); Funktionen für alle 5 Endpunkte + Healthcheck; `ApiError` (Status + Backend-Meldung); TS-Typen aus OpenAPI abgeleitet (`types.ts`, diskriminierte `RundeRequest`-Union); Typecheck grün
  - [x] **007.6 Vitest:** Vitest + `@vue/test-utils` + `jsdom`; Config in `vite.config.ts` (`environment: jsdom`, `globals`, `include src/**`); Scripts `test`/`test:watch`; 1 Smoke-Test (`StartView.spec.ts`) grün; Build unberührt
  - [x] **007.7 Playwright + playwright-bdd:** Grundgerüst + **genau 1** Smoke-Szenario (`e2e/features/smoke.feature`, deutsch, „Startseite lädt") gegen Vite-Dev-Server (Chromium) — grün. Teststrategie verbindlich in **ADR-013** (Fachlichkeit auf API-Ebene, E2E-Budget ≤ 3–5 bis MVP, kein Ausbau ohne Einzelentscheidung)
  - [x] **007.8 Dev-Proxy:** Vite-Dev-Server proxied `/api` **und** `/health` → `http://127.0.0.1:8000` (`vite.config.ts` `server.proxy`); Dev = Prod-Same-Origin (ADR-010). End-to-end verifiziert: `/health/` 200, `POST /api/spiele/` 201 über Port 5173
  - [x] **007.9 CI:** `.github/workflows/ci.yml` um Job **`frontend`** (npm ci → build inkl. vue-tsc → Vitest) und separaten Job **`frontend-e2e`** (Chromium + Playwright-Smoke) erweitert; `actions/setup-node` SHA-gepinnt (`49933ea…` # v4), Node aus `.node-version`, npm-Cache. YAML validiert; CD gated auf gesamte CI → Frontend-Jobs gaten jetzt auch den Deploy
  - [x] **007.10 Doku-Sync:** `development-approach-v1.md` §Phase 2 um Frontend-Fundament/-Zyklus ergänzt; `glossar.md` um gaten/Testpyramide/playwright-bdd/Dev-Proxy erweitert; `datenmodell-v1.puml` unberührt; BACKLOG + Handover + Memory nachgezogen
- [x] **TASK-008** Spiel anlegen (UI) — Slice 1
  - [x] **Pinia-Store** `src/stores/spiel.ts` — hält das aktuelle Spiel (`aktuellesSpiel`, `setzeSpiel`)
  - [x] **Formular-Komponente** `src/components/SpielAnlegenForm.vue` — präsentationsnah: 4 Spielernamen + Rundenanzahl, Client-Validierung (alle Namen gefüllt, eindeutig, Rundenanzahl positives Vielfaches von 4), Absenden-Button gesperrt bis gültig, meldet gültige Eingabe per `absenden`-Event; kennt keine API
  - [x] **StartView** orchestriert: `spielAnlegen()` → Store setzen → `router.push({ name: 'spiel' })`; `ApiError`-Meldung inline, Lade-/Fehlerzustand an Formular durchgereicht
  - [x] **Vitest:** `SpielAnlegenForm.spec.ts` (Validierung, Trimmen, Emit) + `StartView.spec.ts` (Integration mit gemocktem API-Client, Pinia, Memory-Router: Erfolg → Store+Navigation, Fehler → Meldung, keine Navigation). 11 Tests grün, Build (vue-tsc) grün. Kein neues E2E-Szenario (ADR-013)
- [x] **TASK-009** Runde eingeben und auswerten (UI) — Slices 2–5
  - [x] **009.1 Rotation + Store + View-Fundament:** `src/domain/rotation.ts` (reine Funktionen `geberFuerRunde`, `aktiveSpieler`, `gegenspielerNamen`), `spiel`-Store um `aktuelleRundennummer` + `naechsteRunde()` erweitert, `SpielView` zeigt Rundenfortschritt + Geber (setzt aus) + aktive Spieler
  - [x] **009.2 RundeForm-Gerüst + Tausender + Integration:** präsentationsnahe `RundeForm` (Rundentyp-Auswahl, Spielmacher, abgeleitete Gegenspieler), Tausender gewonnen/verloren vollständig; `SpielView` reicht `rundeAuswerten()` durch → `letztesErgebnis` + `naechsteRunde()`
  - [x] **009.3 Normales Spiel:** `src/domain/regeln.ts` (`STICHWERT_KONTROLLSUMME = 250`), Detailfelder je aktivem Spieler (Meldepunkte/Stichwerte/eigener Stich) als `reactive`-Map, Live-Kontrollsumme (muss genau 250 ergeben), Sterne; baut vollständigen `RundeNormal`-Payload
  - [x] **009.4 Einfaches + doppeltes Abgehen:** einfaches Abgehen nur Gegenspieler-Meldepunkte (kein Stich-Zwang, keine 250er-Summe), doppeltes Abgehen volle Gegenspieler-Daten inkl. Stich-Zwang; passende Payloads (`RundeEinfachesAbgehen` / `RundeDoppeltesAbgehen`)
  - [x] **009.5 Tausender (Review):** bereits in 009.2 vollständig verdrahtet und getestet — Gegenprüfung ohne Änderung
  - [x] **009.6 Spielende-Navigation + Doku:** Beendet-Bereich zeigt letztes Ergebnis + `RouterLink` zur Auswertung (`/spiel/:spielId/ende`)
  - [x] **Vitest:** `rotation.spec.ts` (4), `RundeForm.spec.ts` (Gegenspieler-Ableitung, normal gesperrt/gültig, einfaches/doppeltes Abgehen, Tausender, Fehler), `SpielView.spec.ts` (Store/API-Laden, Fehler, Spielende-Link mit `RouterLinkStub`). 26 Tests grün, Build (vue-tsc) grün. Alle fünf Rundentypen zusätzlich per curl gegen Backend geprüft (201). Kein neues E2E-Szenario (ADR-013)
- [x] **TASK-010** Spielstand anzeigen (UI) — Slice 6 (Punktestände)
  - [x] **Client/Store:** `punktestaendeLaden()` bereits vorhanden; `SpielView` hält `punktestaende` (`PunktestandMap | null`) + `punktestaendeAktualisieren()` (weicher Fallback bei Ladefehler, blockiert die Runde nicht)
  - [x] **View:** Punktestand-Sektion (`data-testid="punktestaende"`) zwischen Header und Rundenerfassung, absteigend sortiert (`sortierteStaende`, höchster zuerst), Führender hervorgehoben; wird nach jeder gewerteten Runde und beim Öffnen aktualisiert
  - [x] **Vitest:** `SpielView.spec.ts` um `punktestaendeLaden`-Mock + Sortier-/Anzeige-Test erweitert. 27 Tests grün, Build (vue-tsc) grün. Per curl verifiziert (200). Kein neues E2E-Szenario (ADR-013)
- [x] **TASK-011** Spiel abschließen / Sieger anzeigen (UI) — Slice 6 (Sieger)
  - [x] **View:** `SpielendeView.vue` (vorher Platzhalter) lädt `siegerErmitteln(spielId)` in `onMounted`; zeigt Sieger-Banner (einzeln oder „Gleichstand – mehrere Sieger") + absteigenden Endstand (Sieger hervorgehoben) + `RouterLink` „Neues Spiel" → `start`. Lade-/Fehlerzustand analog `SpielView`
  - [x] **Vitest:** `SpielendeView.spec.ts` — alleiniger Sieger + Sortierung, Gleichstand (mehrere Sieger), Fehlerfall (`vi.mock('../api')` siegerErmitteln, `RouterLinkStub`). 30 Tests grün, Build (vue-tsc) grün. Per curl verifiziert (200). Kein neues E2E-Szenario (ADR-013)
  - [ ] **Nachzügler (optional):** UI-Eingabe für exakte 1er-Stichwerte (Tiebreak bei Gleichstand, §9.3/§17.2) — Backend unterstützt `?exakte_stichwerte=` bereits. **Erledigt durch TASK-012.3/012.5:** Die normalen Stichwert-Felder erfassen jetzt durchgängig 1er-genau (`step=1`), womit die punktgenaue Eingabe in der letzten Runde nativ möglich ist. Ein Sonder-Eingabefeld ist nicht mehr nötig

### Phase 2b – Rundenerfassung: fachliche Verfeinerung aus Live-Feedback (24.07.2026)

> **Kontext:** Erstes Durchspielen der Rundenerfassung (nach TASK-009–011). USER-Feedback +
> Eigenreview gegen `rule-set-v1.md` und `Anschreibetabelle_4_Spieler.md`. Mehrere Punkte sind
> **Regelkonformität** (nicht nur UX): §16.1/§16.2 (automatische vs. explizite Rundenausgänge),
> §8.2 (dritter Stichwert automatisch), §10.3 (Stich-Zwang), §15.3–15.5 (Sterne), §7/§9.1
> (10er-Werte). Reihenfolge nach Wert/Risiko: erst reines Frontend (TASK-012), dann
> Backend+Frontend (TASK-013, TASK-014).

- [x] **TASK-012** Rundenerfassung: Regelkonformität & UX (Frontend-only, Slices 2–5)
  - [x] **012.1 Rundentyp-Auswahl regelkonform reduzieren** — nur explizit zu erfassende Ausgänge anbieten (§16.2): „Normales Spiel", „Einfaches Abgehen", „Tausender gewonnen", „Tausender verloren". **„Doppeltes Abgehen" entfällt aus der Auswahl** — es wird bei normalem Spiel automatisch abgeleitet, wenn M+S < Reizwert (§16.1). `RundeDoppeltesAbgehen`-Zweig in `RundeForm.absenden()` + zugehöriger Vitest entfällt; API-Typ bleibt (Vertrag unberührt). **RD-Hinweis:** Nach dem Merge in „normal" unterliegt doppeltes Abgehen der 250-Kontrollsummen-Validierung (`stichwerteGueltig`) — fachlich korrekter (voll ausgespielt), bewusst dokumentieren + Vitest ergänzen
  - [x] **012.2 Zahlenfelder auf 10er-Werte + Grenzen** — Reizwert: `step=10`, Default 150. Meldepunkte: `step=10`, `min=0` (§7 „nur Stichwerte 1er-genau"). **Stichwerte: `step=1`, `min=0`** — bewusst 1er-genau (Korrektur 24.07.2026, USER: „bei knappen Spielen ist ein genaues Zählen auf Einer-Werte notwendig"; §9.1 aktualisiert, Rundung auf 10 nur optionale Bequemlichkeit, nie erzwungen). **RD-erledigt:** Reizwert-Minimum 150 als Hausregel in `rule-set-v1.md` §7 + `ubiquitous-language.md` §4.14 verankert; alle Fixtures ≥150 geprüft (kein Bruch)
  - [x] **012.3 „hat eigenen Stich" aus Stichwert ableiten** — Checkbox entfernt; `hat_eigenen_stich = stichwerte > 0` je aktivem Spieler (Spielmacher + Gegenspieler) im Payload (§10.3). Ohne manuelle Übersteuerung: kleinstmöglicher Stichwert ist 6 (3× Unter) → Edge-Case „kleiner Stich → 0" praktisch irrelevant (USER-Entscheid 24.07.2026). Vitest: Ableitung `false` bei automatischem 0-Stichwert abgedeckt
  - [x] **012.4 Sterne-Checkboxen entfernen** — Sterne ergeben sich ausschließlich aus dem Tausender-Ausgang (§15.3/§15.5); Backend setzt sie bereits automatisch. Manuelle `spielmacher_stern`/`gegenspieler_stern`-Eingaben im normalen Spiel entfallen
  - [x] **012.5 Dritten Stichwert automatisch berechnen** — sobald zwei der drei aktiven Stichwerte (Spielmacher + 2 Gegenspieler) erfasst sind, wird der fehlende dritte = `250 − w1 − w2` automatisch gesetzt; flexibel unabhängig davon, welche zwei zuerst erfasst wurden (§8.2/§16.1). Umsetzung: `stichwertReihenfolge`-Tracking (zwei zuletzt bearbeitete gewinnen), Auto-Feld **read-only** + Hinweis „— automatisch"; berechneter Wert < 0 → `stichwerte-fehler`-Hinweis + Absenden gesperrt. Vitest: Auto-Berechnung + read-only + Negativ abgedeckt
  - [x] **012.6 BUG-FIX + Reset nach Wertung** — nach erfolgreicher `rundeAuswerten()` das Formular vollständig zurücksetzen: alle Detailwerte (Meldepunkte/Stichwerte) auf 0, Reizwert auf Default, **Rundentyp auf „Normales Spiel"** (häufigster Fall), Spielmacher auf ersten aktiven Spieler der neuen Runde. Behebt: „Meldepunkte werden nach Wertung nicht genullt". **RD-Entscheid:** Reset-Trigger MUSS aus dem Parent kommen (`RundeForm` kennt POST-Erfolg nicht) — sauber via `watch(() => props.rundennummer)` bzw. `:key="rundennummer"` (erhöht sich nur nach erfolgreicher Wertung); Reset im Kind nach `emit` wäre bei Serverfehler falsch (Eingaben verloren)
  - [x] **012.7 (optional) Transparenz-Hinweis** — bei normalem Spiel live angezeigt, wenn M+S < Reizwert → „wird als doppeltes Abgehen gewertet" (`doppeltes-abgehen-hinweis`, §16.1 nachvollziehbar). Vitest abgedeckt
  - [x] **Vitest anpassen/ergänzen**; Build grün; per curl gegen Backend gegengeprüft (Runde 201, Punktestände 200); kein neues E2E (ADR-013). Doku-Sync erfolgt. **Rubber-Duck-Review (GO-mit-SOLLTE):** Negativ-Stichwert-Test ergänzt (S3, 34 Vitest grün). **S1 ENTSCHIEDEN (USER, Option a):** Ableitung `hat_eigenen_stich = stichwerte > 0` bleibt — im württembergischen Blatt ohne Siebener gibt es keinen 0-Augen-Stich (kleinster Stich = 6), daher kein Regelverstoß; fachlich verankert in `rule-set-v1.md` §5.2 (neu: Blatt) + §10.3 + `ubiquitous-language.md` §4.21. **S2 offen (optional, UX):** Auto-Stichwert-Slot innerhalb der Runde nicht umschaltbar → ggf. „Stichwerte zurücksetzen"-Button; zurückgestellt

- [ ] **TASK-013** Sterne im Wertungsbereich anzeigen (Backend + Frontend, Slice 6)
  - [ ] **Backend:** Sterne-Summe je Spieler aggregieren (aus `RundeModel.spielmacher_stern`/`gegenspieler_stern`) und über API ausliefern — bevorzugt `punktestaende`-Endpoint um `sterne: {name: int}` erweitern (additiv, rückwärtskompatibel; OpenAPI-Vertrag + Typen nachziehen). **RD-Hinweis:** Bei Tausender werden KEINE `GegenspielerRundeModel`-Zeilen angelegt → aktive Gegenspieler für die Stern-Aggregation aus `alle Spieler − Geber − Spielmacher` herleiten (Geber ausschließen, §15.3). Behave-/Django-Test mit **Tausender verloren** gezielt absichern. Vorab prüfen, welcher Endpoint den **Endstand** (`SpielendeView`) speist (`sieger` vs. `punktestaende`) → `sterne` dort konsistent ergänzen
  - [ ] **Frontend:** Sterne symbolisch (`★`) im Punktestand (`SpielView`) und Endstand (`SpielendeView`) anzeigen (§15.4)
  - [ ] Doku-Sync (OpenAPI, Typen, Datenmodell falls nötig). **Rubber-Duck-Prüfpunkt:** Vertragsänderung vor Umsetzung reviewen

- [ ] **TASK-014** Rundenhistorie, tabellarische Anschreibetabelle & Korrektur (Backend + Frontend, Slice 6 / neu)
  - [ ] **Konzept + Rubber-Duck-Review ZUERST** — größter Umfang/Risiko. Klären: (a) Nachvollziehbarkeit (Rundenhistorie im Anschreibetabellen-Stil, §5/§18) — die geforderte **zweizeilige Tabelle** (Rundenzeile `M | S | Mit` + STAND-Zeile, `Anschreibetabelle_4_Spieler.md` §5) braucht die **getrennte M|S-Aufschlüsselung** des Spielmachers; aktuell speichert `RundeModel` nur `spielmacher_punkte` = M+S (**nicht** getrennt). **RD-Weg:** additive, nullable/default-0-Felder (`spielmacher_meldepunkte`, `spielmacher_stichwerte`) ergänzen, `spielmacher_punkte` als Summe belassen → Altdaten 0/NULL, Migration risikoarm (kaum Prod-Daten). (b) Korrektur: **RD-Empfehlung nur „letzte Runde löschen" oder in-place editieren (gleiche `rundennummer`)** — beliebiges Löschen aus der Mitte erzeugt Rundennummer-Lücke (bricht Sequenz/Geberrotation-Anzeige). `punktestaende_laden` rechnet ohnehin bei jedem Aufruf neu → Nachberechnung automatisch. TASK-013 ist unabhängig → Reihenfolge 013 vor 014 korrekt
  - [ ] **012/013-Bezug:** Die tabellarische Anschreibetabelle (§5) war ursprünglich gefordert, wurde in Slices 2–6 aber nur als kumulierter Punktestand umgesetzt → hier als Detailpunkt nachgezogen (USER-Hinweis 24.07.2026)
  - [ ] **Backend:** Endpoint(s) zum Auflisten der Runden (inkl. getrennter M|S|Mit + Geber/Reizwert/Ausgang/Sterne je Runde für die Tabelle) + Löschen/Korrigieren; Modell-Erweiterung (Migration). Django-/Behave-Tests
  - [ ] **Frontend:** zweizeilige Anschreibetabelle (Rundenzeile + STAND-Zeile, Verlustwert `(-x)` im ersten Feld, `★` bei Tausender, „setzt aus" für Geber) + „letzte Runde korrigieren"; Punktestand dadurch nachvollziehbar
  - [ ] Doku-Sync (ADR falls Architekturentscheidung, OpenAPI, Datenmodell, Glossar)

### Nach Phase 2 – Go-Live-Nacharbeiten (Restaufgaben aus TASK-CI-006)

> Der Prod-Deploy selbst ist abgeschlossen (TASK-CI-006 ✅). Diese betrieblichen Nacharbeiten
> sind bewusst hinter Phase 2 (Frontend) eingeordnet und größtenteils USER-/Betreiber-Aktionen
> in der GitHub- bzw. IONOS-Oberfläche.

- [ ] **TASK-CI-007** Reviewer-Gate für Environment `production` erzwingen (USER, GitHub-UI)
  - Settings → Environments → `production` → Required reviewers (sich selbst eintragen)
  - Aktuell NICHT aktiv — Deploy lief ohne Approval-Dialog durch (Deploy-Start ~6 s nach CI-Ende). Offene MITTEL-Auflage aus Rubber-Duck-CD-Review.

- [ ] **TASK-CI-008** Branch Protection für `main` aktivieren (frühere Phase 5, USER, GitHub-UI)
  - Beide Checks als Required setzen: „BDD Akzeptanztests" + „Deploy-Skripte prüfen (shellcheck + bash -n)" (nach 1. erfolgreichem Lauf im BP-UI wählbar)
  - Fork-PR-Approval-Setting mitprüfen. Normative Quellen: ADR-007, `deploy/secrets-setup.md` §6

- [ ] **TASK-CI-009** IONOS-Cloud-Panel-Ports schließen (Blocker #9, USER-/Betreiber-Aktion)
  - 8000/8443/8447 dicht, nur 22/80/443 offen

- [ ] **TASK-CI-010** Backup-/Restore-Probe automatisieren (Runbook 6.2 → vgl. FUTURE-004)
  - SSH-Step in `cd.yml` mit `sqlite3 integrity_check` auf einer zerstörungsfreien Kopie
  - Normative Quelle: `deploy/runbook-task-ci-006.md` Phase 6.2

---

## Abgeschlossen

- [x] **TASK-000** Gherkin-Feature-Dateien (6 Features, alle Szenarien) — 26.06.2026
- [x] **TASK-000b** Gherkin-Nacharbeiten (3 fehlende Szenarien) — 28.06.2026
- [x] **TASK-000c** Engineering-Dokumentation (development-approach-v1.md, ADRs) — 28.06.2026
- [x] **TASK-000d** Domänenlogik (`domain.py` + `use_cases.py`, 28/28 Szenarien GREEN) — 02.07.2026
- [x] **TASK-000e** `docs/datenmodell-v1.puml` — PlantUML-Klassendiagramm angelegt und bereinigt — 18.07.2026

---

## Zukünftig / V2+ (noch nicht priorisiert)

- [ ] **FUTURE-001** i18n / Mehrsprachigkeit
  - `verbose_name`-Werte in `gettext_lazy(_())` einpacken
  - `LANGUAGE_CODE` + `LOCALE_PATHS` in `settings.py` konfigurieren
  - `.po`-Dateien für gewünschte Sprachen anlegen
  - Entscheidung: Bleibt die API-Sprache Deutsch oder wird sie ebenfalls übersetzt? → ADR anlegen
  - Fachbegriffe im Code (Ubiquitous Language) bleiben bewusst Deutsch — nur UI-Strings werden übersetzt

- [ ] **FUTURE-002** DRF (Django REST Framework) als Upgrade
  - Kandidat wenn: Auth, Throttling, Pagination oder OpenAPI-Schema benötigt werden
  - Normative Quelle: ADR-005 (JsonResponse für V1)

- [ ] **FUTURE-003** Backup-DR / Offsite (Fast-Follow aus IONOS-Security-Review 22.07.2026)
  - Pull-basiertes Offsite-Backup: externer/vertrauenswürdiger Host zieht `db.sqlite3.bak.*` per `scp` (kein Cloud-SDK auf der VM)
  - Sofort-Maßnahme (Null-Code): IONOS-VM-Snapshot aktivieren (Volume-DR)
  - Periodische Restore-Übung als wiederkehrender Ops-Schritt dokumentieren
  - Optional: `.last-backup-ok`-Staleness in `/health/` einhängen (Coding-Agent) für „Backup veraltet"-Alarm
  - Begründung: DR gegen Total-VM-Verlust ist ein in ADR-008/009 bewusst akzeptiertes V1-Restrisiko

- [ ] **FUTURE-004** Deploy-Artefakt-Tests vertiefen (Grundsatz „automate everything, test everything", 22.07.2026)
  - ERLEDIGT als Basis: `shellcheck` + `bash -n` für alle `*.sh` als CI-Job (`ci.yml`, Job `skript-lint`)
  - ERLEDIGT: **Post-Deploy-Smoke-Test** in `cd.yml` (End-to-End über öffentliches HTTPS): `/health/`=200, `/admin/`=404 (RD-6), HTTP→HTTPS-Redirect, HSTS-Header. Schlägt einer fehl → Deploy rot.
  - Offen: Smoke-Test um **Backup-/Restore-Probe** erweitern (Runbook 6.2 automatisieren — braucht SSH-Step + `sqlite3 integrity_check` auf einer Kopie; noch manuell)
  - Offen: `nginx -t` gegen das gerenderte `nginx.conf.template` (mit Platzhalter-Substitution) in CI
  - Offen: `systemd-analyze verify` für `binokel-tracker.service`
  - Optional/abwägen: `bats`-Tests für `binokel-backup.sh` (root-/sqlite3-/cron-Abhängigkeiten → ggf. unverhältnismäßig, Trockenlauf bevorzugt)
  - Normative Quelle: `docs/project-foundation.md` §16/§17

- [ ] **FUTURE-005** Deploy-Zugang auf kurzlebige SSH-Zertifikate umstellen (Rubber-Duck-Review CD, 20.10.2026)
  - Statt statischem Long-lived-Deploy-Key eine **SSH-CA / kurzlebige Certs** (z. B. HashiCorp Vault SSH, Teleport) einsetzen
  - Ziel: kein dauerhaft gültiges `VM_SSH_KEY`-Secret mehr; Zugang wird pro Deploy kurzlebig ausgestellt
  - Begründung: Der passwortlose Long-lived-Key ist für V1 pragmatisch vertretbar (kein natives OIDC für selbstverwaltete VMs), aber ein statisches Secret bleibt Restrisiko (OWASP CICD-SEC-6 Credential Hygiene)
  - Post-V1, niedrige Priorität; setzt eine erreichbare CA-Infrastruktur voraus

---

## Architektur-Entscheidungen (ADRs)

| ADR | Entscheidung |
|-----|-------------|
| ADR-001 | Backend vor Frontend |
| ADR-002 | Vertikale Slices |
| ADR-003 | behave als BDD-Toolchain |
| ADR-004 | Repository Pattern (Trennung Domäne/Persistenz) |
| ADR-005 | JsonResponse statt DRF für V1-API |
| ADR-006 | Behave-Tests via HTTP (Blackbox) statt direkter Use-Case-Aufrufe |
| ADR-007 | GitHub Actions als CI/CD-Toolchain |
| ADR-008 | VM-Deployment: systemd/Gunicorn/Nginx, kein Docker |
| ADR-009 | Internet-Hardening-Baseline der VM |

---

## Normative Quellen (Kurzreferenz)

| Thema | Dokument |
|-------|----------|
| Spielregeln | `docs/rule-set-v1.md` |
| Fachbegriffe | `docs/ubiquitous-language.md` |
| Sprachkonventionen | `docs/language-conventions.md` |
| Datenmodell | `docs/datenmodell-v1.puml` |
| Entwicklungsstrategie | `docs/development-approach-v1.md` |
| Gherkin-Phrasen | `docs/gherkin-step-phrase-reference-v1.md` |
| Vollständiger Handover | `docs/copilot-handover-v1.md` |
