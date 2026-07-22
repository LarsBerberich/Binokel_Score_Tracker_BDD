# Copilot-Handover für V1

## Ziel
Dieses Repository modelliert fachlich einen Binokel Score Tracker auf Basis von BDD.

## Führende Dokumente
Die folgende Priorität gilt bei fachlichen Unklarheiten:

1. `docs/rule-set-v1.md`
2. `docs/ubiquitous-language.md`
3. `docs/language-conventions.md`
4. `docs/Anschreibetabelle_4_Spieler.md`

## Engineering-Dokumente
Für Entwicklungsprozess und technische Entscheidungen:

- `docs/project-foundation.md` – Produktvision, BDD-Strategie, Architektur- und Technologieprinzipien
- `docs/development-approach-v1.md` – Operativer Entwicklungsansatz: Outside-In, RED-Green-Refactor, Vertikale Slices, Phasenmodell
- `docs/agents/coding-agent.md` – Rollenbeschreibung Coding-Agent
- `docs/agents/rubber-duck-agent.md` – Rollen- und Prompt-Guide für den ergänzenden Rubber-Duck-Agenten
- `docs/agents/devops-agent.md` – Rollenbeschreibung Dev/Ops-Agent
- `docs/agents/orchestration.md` – Orchestrierungs-Workflow der Agenten
- `docs/adr/ADR-001-backend-vor-frontend.md` – Backend vor Frontend in Phase 1
- `docs/adr/ADR-002-vertikale-slices.md` – Vertikale Slices statt horizontaler Schichten
- `docs/adr/ADR-003-behave-als-bdd-toolchain.md` – behave als BDD-Toolchain für Django
- `docs/adr/ADR-004-repository-pattern.md` – Repository Pattern zur Trennung von Domäne und Persistenz
- `docs/adr/ADR-005-jsonresponse-statt-drf.md` – JsonResponse statt Django REST Framework für V1
- `docs/adr/ADR-006-behave-http-blackbox-tests.md` – Behave-Akzeptanztests via HTTP (Blackbox)
- `docs/adr/ADR-007-github-actions-ci-cd.md` – GitHub Actions als CI/CD-Toolchain
- `docs/adr/ADR-008-vm-deployment-strategie.md` – VM-Deployment via systemd/Gunicorn/Nginx
- `docs/adr/ADR-009-internet-hardening-baseline.md` – Internet-Hardening-Baseline der VM

## V1-Scope
V1 unterstützt ausschließlich:

- 4 Spieler
- Einzelwertung
- Geber setzt aus
- feste Spielerreihenfolge gegen den Uhrzeigersinn
- feste Rundenzahl als Vielfaches von 4
- Default: 12 Runden

Nicht Teil von V1 sind insbesondere:

- Zielspiel-Endbedingungen wie 1000 oder 1500
- Teamwertung
- andere Spielerzahlen

## Wichtige Rundenausgänge
- gewonnenes Spiel
- einfaches Abgehen
- doppeltes Abgehen
- Tausender gewonnen
- Tausender verloren

## Fachliche Kernaussagen
- Der Geber spielt in der Runde nicht mit.
- In der Geber-Spalte wird in der Rundenzeile ein Strich dargestellt.
- Der Spielmacher nimmt den Dapp auf und drückt anschließend 4 Karten.
- Dapp und gedrückte Karten sind fachlich nicht dasselbe.
- Eingegebene Stichwerte enthalten den letzten Stichbonus bereits.
- Die Gesamtsumme aus Stichwerten einschließlich gedrückter Karten und letztem Stich beträgt 250.
- Wenn zwei Stichwerte bekannt sind, kann der dritte automatisch ermittelt werden.
- Reizwerte und Mitpunkte sind volle 10er.
- Nur Stichwerte können 1er-genau sein.
- Im Regelfall werden Stichwerte auf volle 10 gerundet gespeichert.
- In der letzten Runde werden bei möglichem Gleichstand zusätzlich exakte 1er-Werte berücksichtigt.

## Stich-Zwang
- Im Normalfall gilt der Stich-Zwang für alle aktiven Spieler.
- Meldepunkte zählen nur mit mindestens einem eigenen Stich.
- Beim einfachen Abgehen behalten die Gegenspieler ihre Meldepunkte auch ohne eigenen Stich.
- Beim doppelten Abgehen gilt für Gegenspieler weiterhin der normale Stich-Zwang.

## Verlustwertung
- Einfaches Abgehen: negativer einfacher Reizwert
- Doppeltes Abgehen: negativer doppelter Reizwert
- Verlustwerte werden in der Darstellung mit Minuszeichen und in Klammern geschrieben.

## Tausender
- Keine Meldepunkte
- Keine Stichwerte
- Keine Mitpunkte
- Kein Einfluss auf den numerischen Punktestand
- Sterne nur als Zusatzinformation
- Ausgang wird explizit als gewonnen oder verloren erfasst

## Stand 22.07.2026 (TASK-CI-006 — realer Prod-Deploy Phase 0/1 + IONOS-Security-Review, Dev/Ops)

**Realer Produktions-Deploy gestartet** (Agent ohne SSH-Zugang → User führt VM-Kommandos,
paste-sichere Blöcke). Zieldomain **`api.bebe-soft.de`** → `212.132.119.150`, Ubuntu 24.04.

- **Phase 0 (DNS + Admin-Key) ✅** — A-Record verifiziert (beide Resolver, kein AAAA);
  Admin-Key `~/.ssh/binokel_admin` erzeugt.
- **Phase 1 (Erst-Login + sshd-Hardening) ✅ + lockout-sicher verifiziert** — `binokel-admin`
  angelegt (sudo-Gruppe), Key-Login OK, Passwort- + Root-Login abgewiesen.
  **Fallstrick (neu, ENG-004):** cloud-init legt `/etc/ssh/sshd_config.d/50-cloud-init.conf`
  mit `PasswordAuthentication yes` an → überstimmt eine `99-`-Drop-in (sshd „first match wins").
  **Fix:** Hardening als **`00-binokel-hardening.conf`** + Effektivwert-Prüfung via `sshd -T`.
  Runbook Phase 1.3/1.4 korrigiert (realer Login/sudo-Check statt `sudo -n`).

**IONOS-Security-Review (Best-Practice-PDFs → Compliance-Matrix → Rubber-Duck-Audit).**
Matrix: `docs/security/ionos-baseline-check.md` (paraphrasiert; PDFs bleiben lokal/uncommitted).
Ablauf als wiederverwendbares Muster: `pdftotext` → paraphrasierte Matrix (committbar) →
Rubber-Duck-Audit → Dev/Ops-Remediationsplan. Audit-Votum initial **NO-GO** bis Blocker behoben.

**Umgesetztes Go-Live-Gate (Rubber-Duck: GO, nur NIEDRIG-Restpunkte):**
- **#4/#20** SQLite-Backup: `cp` → **`sqlite3 .backup`** + `PRAGMA integrity_check` + atomarer
  `mv` + journald-Logging in neuem `/usr/local/bin/binokel-backup.sh`; cron.d ruft nur noch das
  Skript + separate Retention. Stale-`.tmp`-Cleanup ergänzt. (`deploy/setup-server.sh`)
- **RD-6** `/admin/`-Route in V1 **deaktiviert** (kein Superuser nötig; Reaktivierung nur mit
  Nginx-IP-Allowlist). (`backend/binokel_tracker/urls.py`)
- **RD-8** HSTS `preload` + `includeSubDomains` = **`False`** (host-scoped, reversibel; erst
  nach stabilem TLS scharf schalten). (`backend/binokel_tracker/settings.py`)
- **Restore-Probe** als Runbook-Schritt **6.2** (zerstörungsfrei, Go-Live-Gate).
- Tests GREEN (28 Behave + 19 Django); `bash -n setup-server.sh` OK.

**RD-7** (`@csrf_exempt` auf POST-Views) bewusst akzeptiert/dokumentiert (token-lose JSON-API,
V1 ohne Auth). **Fast-Follow → FUTURE-003:** Offsite-DR (scp-Pull) + IONOS-VM-Snapshot +
periodische Restore-Übung (Backups liegen auf gleicher Platte — in ADR-008/009 akzeptiert).

**Offener Go-Live-Blocker (Betreiber-Aktion):** IONOS-Cloud-Panel-Ports **8000/8443/8447
schließen** (nur 22/80/443).

**Nächste Schritte:** Doc-Änderungen committen (Push-Timing wg. CD beachten — „lokal patchen":
VM erhält gepatchtes `setup-server.sh` per scp, nicht via `curl` aus main) → **Phase 2**
(`setup-server.sh api.bebe-soft.de <repo>`, ohne `CERTBOT_STAGING`) → Phasen 3–6.

---

## Stand 22.07.2026 (TASK-CI-006 — Trockenlauf erfolgreich + Security-Hardening, Dev/Ops)

**Trockenlauf abgeschlossen (GRÜN).** Der komplette Deploy-Pfad wurde real gegen eine
Wegwerf-VM (`staging.bebe-soft.de`, Certbot `--staging`) durchgespielt: `HTTP→HTTPS 301`,
`health-https 200`, sauberes `error.log`, korrekte migrate-/collectstatic-Pfade. Dabei traten
**sechs** weitere reale Blocker auf (gunicorn-Dependency fehlte, Deploy ohne Prod-env → falsche
DB-/Static-Pfade, `/etc/binokel`-Verzeichnis-Traversal, uv-Interpreter im Deploy-Home →
`203/EXEC`, Gunicorn-Control-Server ohne `HOME`, Nginx-Host-Header im 443-`/health/`-Block) —
alle behoben. Commits: `5d6c5e3`, `991c493`, `f486ade`, `c37dc30`, `bbd07e3`, `ded2e13`.

**Security-Review des Rechte-/Zugriffsmodells (Rubber-Duck).** Zwei prod-blockierende Punkte
(K1, K2) + fünf Nachschärfungen (E1–E5), alle umgesetzt; Tests GREEN (28 Behave + 19 Django).

- **K1** – sudoers-Regel `systemctl status` **entfernt** (Pager-Root-Escape via `!sh` aus
  `less`). NOPASSWD nur noch `restart`/`stop`; Statusdiagnose läuft unprivilegiert.
  (`deploy/setup-server.sh`, `.github/workflows/cd.yml`)
- **K2** – fail-open `SECRET_KEY` behoben: bei `DEBUG=False` **harter Abbruch**
  (`ImproperlyConfigured`), wenn der Insecure-Default-Key aktiv ist. `DEBUG`-Default bleibt
  `True` (Test-/Behave-Läufe ohne env). (`backend/binokel_tracker/settings.py`)
- **E1** – `STATIC_DIR` gehört `binokel-deploy`; der exponierte Dienst `binokel-app` hat nur
  noch `rX` (kann ausgeliefertes Static nicht überschreiben). (`deploy/setup-server.sh`)
- **E2** – Security-Header-Ownership entwirrt: Django für proxied Antworten, Nginx exklusiv im
  `/static/`-Block; `Referrer-Policy` vereinheitlicht. (`settings.py`, `nginx.conf.template`)
- **E3** – systemd-Härtung ausgebaut (`ProtectSystem=strict` + `ReadWritePaths`, `ProtectHome`,
  `PrivateDevices`, `SystemCallFilter=@system-service`, `RestrictAddressFamilies` …).
  (`deploy/binokel-tracker.service`)
- **E4** – `server_tokens off;`. (`nginx.conf.template`)
- **E5** – CD liest den echten `SECRET_KEY` nicht mehr: migrate/collectstatic laufen mit einem
  Wegwerf-Schlüssel; nur nicht-geheime Pfad-Variablen werden aus der env gelesen.
  (`.github/workflows/cd.yml`)

**Doku:** ADR-009 (zwei Nachträge: Privilegienmodell „warum root nur fürs Provisioning" +
K1–E5-Zusammenfassung); `ENG-004` (K1/K2-Fallstricke + E1–E5-Abschnitt); `BACKLOG.md`;
`deploy/runbook-task-ci-006.md` (Phase-4-Verifikation an K1 angepasst; env-Perms `640 root:binokel-app`
→ `600 root:root + ACL`).

**Nächste Schritte:** Teardown Wegwerf-VM + Test-DNS entfernen; **realer Produktions-Deploy**
nach Runbook (reale Domain, **ohne** `CERTBOT_STAGING`, IONOS-Ports 8000/8443/8447 schließen).
Danach Phase 2 Frontend (Vue).

---

## Stand 21.07.2026 (TASK-CI-006 — Rubber-Duck-Review + Blocker-Fixes, Dev/Ops)

Der Rubber-Duck-Review der Hardening-/Deploy-Planung ist erfolgt. Ergebnis-Votum war
zunächst **NO-GO**: Die Hardening-Baseline (ADR-009) ist solide, aber der ausführbare
Pfad enthielt 5 Blocker. Diese wurden behoben (Code + Doku), Tests bleiben GREEN
(28 Behave + 19 Django).

**Behobene Blocker:**
- `backend/binokel_tracker/settings.py` — `SECURE_PROXY_SSL_HEADER` + `SECURE_REDIRECT_EXEMPT`
  für `/health/`; `localhost`/`127.0.0.1` immer in `ALLOWED_HOSTS` (Redirect-Loop + Healthcheck).
- `deploy/setup-server.sh` — Nginx/Certbot Henne-Ei gelöst (HTTP-only-Bootstrap → Certbot →
  volles Template); `uv`-Pfad-Fallback (`~/.local/bin`); POSIX-ACLs für gemeinsamen
  Schreibzugriff (`binokel-app` + `binokel-deploy`) auf `data`/`static`; sudoers auf
  `/usr/bin/systemctl`; tägliches SQLite-Backup via `cron.d`; `acl`-Paket ergänzt.
- `deploy/nginx.conf.template` — `location = /health/` im Port-80-Block (HTTP-Healthcheck
  ohne Redirect).
- `.github/workflows/cd.yml` — `VM_SSH_KNOWN_HOSTS` jetzt **Pflicht** (kein
  Laufzeit-`ssh-keyscan`-Fallback mehr; MITM-Schutz).

**Entscheidung:** Betriebssystem-Basis bleibt **Ubuntu 24.04 LTS** (ADR-008 erweitert).

**Neu/aktualisiert:** `docs/engineering-notes/ENG-004-deployment-hardening-fallstricke.md`;
ADR-008 (OS-Basis), ADR-009 (Nachtrag Review); Runbook + `deploy/README.md` angeglichen;
`BACKLOG.md`.

**Nächste Schritte:** Trockenlauf gegen Wegwerf-VM mit Certbot `--staging`, danach realer
Deploy nach Runbook.

---

## Stand 19.07.2026 (TASK-CI-006 geplant — Dev/Ops)

### Erledigt (reine Planung/Dokumentation, KEINE Ausführung auf realer VM)

Für den ersten Produktions-Deploy wurde ein vollständiges Runbook erstellt. Es wurden
**keine** SSH-Verbindungen aufgebaut, **keine** echten Secrets erzeugt und **kein**
Deploy ausgelöst.

- `deploy/runbook-task-ci-006.md` — **neu**: Schritt-für-Schritt-Runbook (Phasen 0–6)
  mit Verifikation + Rollback je Phase, Betriebsrisiken-Tabelle, V2-Migrationsausblick
  (Docker + PostgreSQL) und Rubber-Duck-Review-Punkten.
- `docs/adr/ADR-009-internet-hardening-baseline.md` — **neu**: Internet-Hardening-
  Baseline der VM (SSH-Key-only, sshd-Hardening, UFW, fail2ban, unattended-upgrades,
  chrony, TLS). Ergänzt ADR-008 (deckt SQLite-für-V1 + Docker/PostgreSQL-Pfad ab).
- `deploy/setup-server.sh` — **geändert**: idempotent um `fail2ban`,
  `unattended-upgrades` und `chrony` ergänzt (Schritt 10/10). sshd-Hardening bleibt
  bewusst manuell (Lockout-Risiko, ADR-009).
- `deploy/README.md` — **geändert**: Hardening-Abschnitt + Verweis auf das Runbook.
- `BACKLOG.md` — TASK-CI-006 präzisiert (Status: geplant), ADR-009 ergänzt.

**Nebenbefund:** In diesem Dokument standen unaufgelöste Merge-Konflikt-Marker
(`<<<<<<<`/`>>>>>>>`) im Abschnitt „Engineering-Dokumente" — beim Update bereinigt
(deconflictete `docs/agents/*`-Variante übernommen).

### Nächste Schritte (Dev/Ops)

1. **Rubber-Duck-Review** der Härtungsentscheidungen (Punkte am Ende des Runbooks).
2. **TASK-CI-006 ausführen** auf realer 1&1/IONOS-VM (benötigt Zugangsdaten, Domain,
   DNS). Ablauf strikt nach `deploy/runbook-task-ci-006.md`.

---

## Stand 26.06.2026

### Abgeschlossen
Die Gherkin-Arbeit an den Feature-Dateien ist abgeschlossen.

Alle sechs Feature-Dateien unter `features/` enthalten konkrete Szenarien:
- `spiel_anlegen.feature`
- `runde_normales_spiel.feature`
- `runde_einfaches_abgehen_auswerten.feature`
- `runde_deoppeltes_abgehen.feature`
- `runde_tausender.feature`
- `spielende_und_siegerermittlung.feature`

Zusätzlich wurde `docs/gherkin-step-phrase-reference-v1.md` angelegt.
Sie enthält alle kanonischen Step-Phrasen als Referenz für die spätere Testautomation.

### Wichtige Sprachregeln für Gherkin
- Rundenausgang wird ausschließlich über Zielerreichung des Spielmachers bestimmt.
- Stich-Zwang ist eine Zählregel für Meldepunkte, keine Gewinnbedingung.
- Gegenspieler können fachlich nicht verlieren; sie sammeln nur Punkte.
- Terminologie: "geht ab", nicht "gibt ab".
- Doppeltes Abgehen: Runde wird regulär vollständig ausgespielt.
- Kein Szenario "Spielmacher mit 0 Stichen" in normaler Runde (würde in der Praxis zum einfachen Abgehen führen).

### Offene Todos (Stand 26.06.2026 — inzwischen abgeschlossen, siehe Stand 28.06.2026)

1. ~~Fehlende Szenarien prüfen~~ → erledigt
2. ~~Projektstruktur aufsetzen~~ → noch offen
3. ~~Step-Definitionen schreiben~~ → noch offen
4. ~~Domänenlogik implementieren~~ → noch offen

---

## Stand 19.07.2026 (CI/CD)

### Abgeschlossen

**CI/CD-Pipeline + Dev/Ops-Fundament:**
- `backend/binokel_tracker/settings.py` — produktionsreife Konfiguration via Env-Vars (12-Factor)
  - `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_DB_PATH`,
    `DJANGO_STATIC_ROOT`, `DJANGO_CSRF_TRUSTED_ORIGINS`
  - Automatische HSTS/Secure-Cookie-Aktivierung bei `DEBUG=False`
- `backend/binokel_tracker/urls.py` — `/health/`-Endpunkt für Deployment-Healthchecks
- `.github/workflows/ci.yml` — CI: Django-Check + BDD-Szenarien bei jedem Push/PR
- `.github/workflows/cd.yml` — CD: rsync auf 1&1-VM, Migrationen, Neustart, Healthcheck, Rollback
- `deploy/binokel-tracker.service` — systemd-Unit (Gunicorn)
- `deploy/nginx.conf.template` — Nginx Reverse Proxy mit TLS
- `deploy/setup-server.sh` — einmaliges Server-Initialsetup
- `deploy/README.md` — vollständiges Betriebsrunbook
- `docs/agents/coding-agent.md` — Rollenbeschreibung Coding-Agent
- `docs/agents/rubber-duck-agent.md` — Rollenbeschreibung Rubber-Duck-Agent
- `docs/agents/devops-agent.md` — Rollenbeschreibung Dev/Ops-Agent
- `docs/agents/orchestration.md` — Orchestrierungs-Workflow der 3 Agenten
- `docs/adr/ADR-007-github-actions-ci-cd.md`
- `docs/adr/ADR-008-vm-deployment-strategie.md`
- 28/28 Behave-Szenarien weiterhin GREEN

### Nächste Schritte (Priorität)

1. **TASK-CI-006** VM einrichten und ersten Produktions-Deploy durchführen
   - Benötigt: Zugangsdaten zur 1&1-VM, Domain, GitHub-Secrets
   - Schritte: `deploy/README.md`
2. Weitere Priorisierung siehe `BACKLOG.md` im Repo-Root

---

## Stand 19.07.2026

### Abgeschlossen

**TASK-006: Behave HTTP-Blackbox-Infrastruktur + Slice-1-Migration (19.07.2026):**
- `features/environment.py` — vollständig neu: `setup_databases()` + Migrationen in `before_all`, `context.client` (Django TestClient) in `before_scenario`, `SpielModel.objects.all().delete()` in `after_scenario` (Cascade)
- `features/steps/spiel_anlegen_steps.py` — Slice 1 vollständig auf HTTP migriert: POST /api/spiele/ statt `spiel_anlegen()`, HTTP-400-Checks statt Exception-Fang, `Spiel`-Domänenobjekt aus API-Antwort rekonstruiert (für `geber_in_runde`)
- Slices 2–5: Domain-Steps bleiben bewusst erhalten (testen interne Berechnungsregeln, Stich-Zwang, 250er-Kontrollsumme — nicht über HTTP-Response sichtbar)
- Slice 6: Domain-Steps bleiben (Punktestände werden direkt als Dict gesetzt; kein passender API-Endpunkt)
- 28/28 Behave GREEN, 18/18 Django GREEN

### Nächste Schritte (Priorität)

Alle definierten TASKs abgeschlossen. Keine offenen priorisierten Aufgaben.

→ Vollständiger Backlog: `BACKLOG.md` im Repo-Root

---

## Stand 19.07.2026 (TASK-005)
- `backend/scoring/tests.py` — 18 API-Integrationstests (Django TestCase + TestClient)
  - `SpielAnlegenApiTest` (6 Tests): POST /api/spiele/, GET /api/spiele/{id}/, Fehlerbehandlung
  - `RundeAuswertenApiTest` (8 Tests): alle 5 Rundentypen, Pflichtfeld- und Typ-Validierung
  - `PunktestaendeUndSiegerApiTest` (4 Tests): Punktestände, Sieger, Tiebreaking, 404
- 18/18 Django-Tests GREEN, 28/28 Behave-Szenarien weiterhin GREEN
- Normative Quelle: ADR-006

### Nächste Schritte (Priorität)

1. **TASK-006** Behave-Steps schrittweise auf HTTP umstellen (ADR-006, Slice für Slice)
   - Slice 1: `spiel_anlegen.feature` + `spiel_anlegen_steps.py`
   - Dann Slices 2–6 analog

→ Vollständiger Backlog: `BACKLOG.md` im Repo-Root

---

## Stand 18.07.2026

### Abgeschlossen

**Domänenlogik vollständig — 28/28 Szenarien GREEN (02.07.2026):**
- `backend/scoring/domain.py` — `Spiel` (dataclass), `Rundenausgang` (Enum), Fehlerklassen
- `backend/scoring/use_cases.py` — alle Use Cases für Slices 1–6 implementiert
- `features/steps/` — alle 7 Step-Dateien vollständig implementiert
- `features/environment.py` — Django-Integration (setup_test_environment in before_all)
- `docs/engineering-notes/ENG-001`, `ENG-002` — Implementierungs-Fallstricke dokumentiert

**Persistenzschicht + Workflow-Dokumentation (18.07.2026):**
- `docs/datenmodell-v1.puml` — PlantUML-Klassendiagramm repariert und bereinigt
- `BACKLOG.md` — neues zentrales Steuerungsdokument für Session-Kontinuität angelegt
- `docs/project-foundation.md` §18 — BACKLOG.md und 3-Quellen-Workflow dokumentiert
- `docs/development-approach-v1.md` §8 — neuer Abschnitt „Session-Kontinuität und Backlog-Workflow“
- `backend/scoring/models.py` — 4 Django ORM-Modelle implementiert
  (SpielModel, SpielerModel, RundeModel, GegenspielerRundeModel)
- `backend/scoring/migrations/0001_initial.py` — erzeugt und angewendet
- 28/28 Behave-Szenarien weiterhin GREEN

### Nächste Schritte (Priorität)

1. **TASK-005** API-Integrationstests in `scoring/tests.py` (TestCase + TestClient)
2. **TASK-006** Behave-Steps schrittweise auf HTTP umstellen (ADR-006, Slice für Slice)

→ Vollständiger Backlog: `BACKLOG.md` im Repo-Root

---

## Stand 28.06.2026

### Abgeschlossen

**Gherkin-Nacharbeiten:**
Drei fehlende Szenarien in `features/` ergänzt:
- `spiel_anlegen.feature`: Geberrotation streng reihum
- `runde_normales_spiel.feature`: Validierungsfehler wenn Stichwert-Summe > 250
- `runde_einfaches_abgehen_auswerten.feature` + `runde_deoppeltes_abgehen.feature`: Verlustwert-Darstellung `(-250)` / `(-400)`

Neue Step-Phrasen in `docs/gherkin-step-phrase-reference-v1.md` (Geberrotation, Stichwert-Validierung, Verlustwert-Darstellung).

**Engineering-Dokumentation:**
- `docs/development-approach-v1.md` erstellt: Outside-In, RED-Green-Refactor, Vertikale Slices, Phasenmodell mit ausführlichen Begründungen
- `docs/adr/` angelegt: ADR-001, ADR-002, ADR-003
- `docs/project-foundation.md` §10 (BDD-Entwicklungszyklus) und §18 (Dokumentationsset) aktualisiert

### Offene Todos (nächster Schritt)

1. **Projektstruktur aufsetzen** (technisch)
   - Python-Projektstruktur und `behave` + `behave-django` einrichten
   - Django-Grundgerüst anlegen
   - Step-Stub-Dateien aus `docs/gherkin-step-phrase-reference-v1.md` generieren → `behave` ausführen → alles RED
   - Feature-Reihenfolge: laut `docs/development-approach-v1.md` §5

2. **Step-Definitionen schreiben**
   - Auf Basis von `docs/gherkin-step-phrase-reference-v1.md`
   - Zunächst ohne Domänenlogik (pending)

3. **Domänenlogik implementieren**
   - Feature für Feature als vertikale Slice
   - Normative Quelle: `docs/rule-set-v1.md`
