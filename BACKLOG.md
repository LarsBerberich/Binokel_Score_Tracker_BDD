# Backlog – Binokel Score Tracker V1

> **Workflow:** Session startet → diese Datei lesen → sofort im Bild.  
> Session endet → `BACKLOG.md` + `docs/copilot-handover-v1.md` + `/memories/repo/handover-status.md` synchron aktualisieren.

---

## ▶ Aktueller Fokus

**TASK-006 ist abgeschlossen. TASK-CI-006 (erster Produktions-Deploy) ist erfolgreich: App läuft prod auf `api.bebe-soft.de` (CD #30/#31 GREEN, Post-Deploy-Smoke-Test automatisiert). Verbleibende Go-Live-Governance-/Ops-Nacharbeiten sind hinter Phase 2 eingeordnet → `TASK-CI-007`…`TASK-CI-010`.**

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

### Phase 2 – Frontend (Vue) — noch nicht gestartet

- [ ] **TASK-007** Vue-Anwendung aufsetzen, API-Client konfigurieren
- [ ] **TASK-008** Spiel anlegen (UI)
- [ ] **TASK-009** Runde eingeben und auswerten (UI)
- [ ] **TASK-010** Spielstand anzeigen (UI)
- [ ] **TASK-011** Spiel abschließen / Sieger anzeigen (UI)

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
