# ADR-009 – Internet-Hardening-Baseline der VM

## Status

Angenommen (19.07.2026)

## Kontext

Für TASK-CI-006 wird eine neue **1&1 / IONOS-VM mit frisch installiertem Ubuntu LTS**
im offenen Internet betrieben. Der Auslieferungszustand einer solchen VM ist nicht
für den ungeschützten Internetbetrieb gehärtet (Root-SSH-Login, Passwort-Login,
keine Brute-Force-Abwehr, keine automatischen Sicherheitsupdates).

`ADR-008` regelt die Deployment-Strategie (systemd/Gunicorn/Nginx, kein Docker für V1)
und den Migrationspfad zu Docker + PostgreSQL — trifft aber **keine** Aussage zur
Härtung der VM als Betriebssystem-Basis. Diese Lücke schließt dieser ADR.

Zusätzlich stellte sich die Frage, **welche** Härtungsmaßnahmen im idempotenten
Setup-Skript (`deploy/setup-server.sh`) automatisiert und welche bewusst manuell
im Runbook (`deploy/runbook-task-ci-006.md`) gehalten werden.

## Entscheidung

Es wird eine **Internet-Hardening-Baseline** für die Produktions-VM festgelegt:

1. **Non-root Admin-User mit sudo**, Login ausschließlich per SSH-Key.
2. **SSH-Daemon-Hardening** via Drop-in (`/etc/ssh/sshd_config.d/99-binokel-hardening.conf`):
   `PermitRootLogin no`, `PasswordAuthentication no`, `PubkeyAuthentication yes`,
   `MaxAuthTries 3`, `LoginGraceTime 30`, optional nicht-Standard-Port.
3. **UFW-Firewall**: `deny incoming` als Default, nur SSH/HTTP/HTTPS erlaubt.
4. **fail2ban**: Brute-Force-Schutz für SSH.
5. **unattended-upgrades**: automatische Sicherheitsupdates.
6. **chrony**: Zeit-Synchronisation (relevant für TLS-Gültigkeit und Log-Korrelation).
7. **TLS**: erzwungenes HTTPS (Certbot/Let's Encrypt, HTTP→HTTPS-Redirect, HSTS).

**Aufgabenteilung Skript ↔ Runbook:**

| Maßnahme | Ort | Begründung |
|---|---|---|
| UFW, fail2ban, unattended-upgrades, chrony | `setup-server.sh` (automatisiert) | idempotent, ohne Lockout-Risiko |
| Admin-User + sshd-Hardening | Runbook Phase 1 (manuell) | SSH-Lockout-Risiko, menschliche Verifikation nötig |
| TLS/Nginx | `setup-server.sh` (automatisiert) | Certbot benötigt nur korrektes DNS |

## Begründung

- **Least Privilege / Angriffsflächenreduktion:** Root-SSH und Passwort-Login sind
  die häufigsten Einfallstore. Key-only + kein Root-Login eliminiert Passwort-
  Brute-Force und direkte Root-Kompromittierung.
- **Warum sshd-Hardening manuell bleibt:** Ein Skript kann sich nicht selbst gegen
  einen SSH-Lockout absichern. Sicheres Hardening verlangt eine **zweite, parallel
  offene Sitzung** zur Verifikation, bevor die erste geschlossen wird — eine
  menschliche Kontrollhandlung. Ein Auto-Reload eines fehlerhaften sshd-Configs
  könnte den einzigen Zugang unwiederbringlich sperren.
- **Warum fail2ban/unattended-upgrades/chrony automatisiert werden:** Diese Maßnahmen
  sind idempotent und tragen **kein** Lockout-Risiko. Automatisierung verhindert
  Konfigurationsdrift und vergessene Schritte.
- **Defense in Depth:** fail2ban ergänzt key-only SSH (Rate-Limiting/Logging),
  unattended-upgrades schließt bekannte CVEs zeitnah, UFW begrenzt exponierte Ports.

## Konsequenzen

### Positiv
- Deutlich reduzierte Angriffsfläche im offenen Internet.
- Automatische Sicherheitsupdates ohne manuelle Pflege.
- Reproduzierbare, dokumentierte Baseline (Runbook + Skript).

### Negativ / Risiken
- **SSH-Lockout-Risiko** beim manuellen Hardening → im Runbook durch offene
  Zweitsitzung und Provider-Konsole als Fallback abgesichert (Phase 1).
- **unattended-upgrades kann Neustarts auslösen** → Reboot-Fenster konfigurierbar;
  ungeplante Downtime bewusst in Kauf genommen (V1, kein HA).
- Optionaler nicht-Standard-SSH-Port erhöht Konfigurationsaufwand (UFW, known_hosts,
  keyscan) → für V1 wird Standardport 22 empfohlen.

### Meilenstein für Überprüfung
- Umstellung auf Docker + PostgreSQL (ADR-008): Härtung muss um Container-/DB-
  spezifische Aspekte (Netzwerksegmentierung, DB-Zugriffsrechte, Secrets) erweitert
  werden.
- Bei Bedarf an höherer Verfügbarkeit: Reboot-/Update-Strategie überdenken.

## Abgrenzung

- **SQLite-für-V1 und der Migrationspfad zu Docker + PostgreSQL** sind **nicht** Teil
  dieses ADR — sie sind bereits durch **ADR-008** abgedeckt. Dieser ADR ergänzt ADR-008
  ausschließlich um die Betriebssystem-Härtungs-Baseline.

## Implementierung

- `deploy/runbook-task-ci-006.md` — Phase 1 (manuelles sshd-Hardening) + Phase 2
  (automatisierte Maßnahmen), Verifikation und Rollback je Phase.
- `deploy/setup-server.sh` — fail2ban, unattended-upgrades, chrony (idempotent).
- `deploy/nginx.conf.template` — TLS-Erzwingung + Security-Header (bestehend).
- `deploy/binokel-tracker.service` — systemd-Prozesshärtung (bestehend).

## Nachtrag (21.07.2026) — Rubber-Duck-Review

Der Rubber-Duck-Review vor der ersten realen Ausführung bestätigte die Baseline als
**solide** (keine Änderung an der Hardening-Entscheidung selbst nötig), deckte aber
Blocker im *ausführbaren* Pfad auf. Daraus resultieren folgende Präzisierungen mit
Sicherheitsbezug:

1. **`known_hosts` ist Pflicht (MITM-Schutz).** Der bisherige Laufzeit-`ssh-keyscan`-
   Fallback im CD-Workflow war blindes Trust-on-first-use bei *jedem* Deploy. Das
   Secret `VM_SSH_KNOWN_HOSTS` ist nun verpflichtend; fehlt es, bricht der Workflow
   bewusst ab (`.github/workflows/cd.yml`).
2. **Gemeinsamer Schreibzugriff per POSIX-ACL statt root.** Der Dienst (`binokel-app`)
   und der Deploy-User (`binokel-deploy`) teilen sich `data`/`static` über Default-ACLs.
   Das erhält Least Privilege (keine root-Ausführung von migrate/collectstatic) und
   löst zugleich die SQLite-Schreibrechte. Neue Abhängigkeit: Paket `acl`.
3. **sudoers-Pfad `/usr/bin/systemctl`** (Ubuntu-24.04-usrmerge, kanonischer Pfad),
   damit die eng begrenzte NOPASSWD-Regel zuverlässig greift.
4. **App-seitige HTTPS-Erzwingung hinter Proxy:** `SECURE_PROXY_SSL_HEADER` +
   `SECURE_REDIRECT_EXEMPT` für `/health/` verhindern Redirect-Loop und halten den
   lokalen HTTP-Healthcheck funktionsfähig (`backend/binokel_tracker/settings.py`).

Vollständige Ursachen-/Lösungsanalyse: `docs/engineering-notes/ENG-004-deployment-hardening-fallstricke.md`.

## Nachtrag (21.07.2026) — Trockenlauf-Vorbereitung

Bei der Vorbereitung des Trockenlaufs wurde ein weiterer Blocker im Deploy-Pfad
gefunden und behoben:

5. **Deploy lädt die Produktionskonfiguration.** `migrate`/`collectstatic` liefen als
   `binokel-deploy` ohne `/etc/binokel/env` und verwendeten daher die Repo-Default-
   Pfade statt `DJANGO_DB_PATH`/`DJANGO_STATIC_ROOT` — der Dienst wäre gegen eine
   leere DB gestartet. Die Deploy-Schritte (`cd.yml`, manueller Not-Deploy) laden nun
   die Env (`set -a; . /etc/binokel/env; set +a`). Dazu erhält `binokel-deploy` per
   gezielter ACL (`setfacl -m u:binokel-deploy:r /etc/binokel/env`) **Lesezugriff**.
   Zusätzlich braucht das Verzeichnis `/etc/binokel` (root:root, 750) ein
   Such-Recht per ACL (`setfacl -m u:binokel-app:x -m u:binokel-deploy:x /etc/binokel`),
   sonst greift die Datei-ACL wegen fehlender Verzeichnis-Traversierung nicht.
   Dies schwächt Least Privilege nicht: `binokel-deploy` rsynct ohnehin den App-Code
   und startet den Dienst, könnte den `SECRET_KEY` also ohnehin erlangen — der
   Lesezugriff macht die bestehende Vertrauensgrenze nur explizit.

## Nachtrag (21.07.2026) — Trockenlauf-Ausführung: Dienst-User-Ausführungsrechte

Der reale Trockenlauf gegen eine Wegwerf-VM deckte eine Kette von Rechte-Blockern
auf, die den Dienststart verhinderten (`systemd status=203/EXEC`, Healthcheck `502`).
Sie sind in ENG-004 im Detail dokumentiert; die Baseline-relevante Konsequenz:

6. **Der Dienst-User muss den venv-Interpreter erreichen und ausführen können.**
   Der Dienst läuft als `binokel-app`, der venv wird aber von `binokel-deploy` erzeugt.
   Zwei Ebenen waren betroffen: (a) der App-Baum (`.venv/bin/gunicorn`) — behoben per
   `setfacl -R (-d) -m u:binokel-app:rX /opt/binokel/app`; und (b) der **eigentliche
   Übeltäter** — der von `uv` verwaltete Python-Interpreter, auf den der venv nur per
   Symlink zeigt, lag unter `~binokel-deploy/.local/share/uv/python` (Home = `0750`,
   für `binokel-app` nicht traversierbar). Fix: `uv` installiert den Interpreter jetzt
   in ein geteiltes Verzeichnis (`UV_PYTHON_INSTALL_DIR=/opt/binokel/python`), das
   `setup-server.sh` mit `setfacl -R (-d) -m u:binokel-app:rX` absichert. Least Privilege
   bleibt gewahrt: `binokel-app` erhält nur Lese-/Ausführungsrecht (`rX`), kein
   Schreibrecht — es schreibt zur Laufzeit ausschließlich in `data`/`static`.

## Nachtrag (21.07.2026) — Privilegienmodell: warum root nur fürs Provisioning

Wiederkehrende Frage: „Wir machen im Deployment vieles als root — ist das nicht gegen Best
Practice?" Antwort: Best Practice ist **nicht** „niemals root", sondern **„root nur zum
Einrichten, niemals für den laufenden, internet-exponierten Dienst"**. Genau so ist es hier
gebaut. Es gibt drei klar getrennte Phasen mit je minimalem Rechteumfang:

| Phase | Wer | Rechte | Warum |
|-------|-----|--------|-------|
| **Provisioning** (einmalig) — `setup-server.sh` | `root` | voll | Nutzer/Verzeichnisse anlegen, systemd-Unit installieren, Nginx/TLS/UFW/apt — inhärent Root-Operationen. Wird **einmal** ausgeführt, danach nicht mehr. |
| **Laufzeit** (dauerhaft) — Gunicorn/Django | `binokel-app` | System-User, **kein** Login, **kein** Home, **kein** sudo, nur `rX` auf Code | Das ist der dem Internet ausgesetzte Prozess — er ist bewusst **entprivilegiert** und kann nicht einmal seinen eigenen Code überschreiben. |
| **Deployment** (wiederkehrend) — CI/CD | `binokel-deploy` | **kein** root; `sudo` NUR für `systemctl restart/stop` des einen Dienstes | Deployt Code und startet den Dienst neu, mehr nicht. |

**Kernpunkt:** Root wird ausschließlich für die einmalige Systemadministration benutzt — um
die Nicht-root-Trennung überhaupt korrekt **einzurichten**. Der laufende Dienst und die
CI/CD-Pipeline sind entprivilegiert. Auch die manuellen Debug-Kommandos im Trockenlauf
(`setfacl` auf root-eigene Pfade, `systemctl`, Schreiben nach `/etc`) waren Systemadministration
und damit legitime Root-Operationen — nicht der Betrieb des Dienstes als root.

**Merksatz:** *root provisioniert, `binokel-app` bedient das Internet, `binokel-deploy` deployt* —
jeweils mit dem kleinstmöglichen Rechteumfang.

## Nachtrag (21.07.2026) — Security-Review-Nachschärfungen (K1, K2, E1–E5)

Ein Rubber-Duck-Security-Review der im Trockenlauf geänderten Zugriffsrechte fand zwei
prod-blockierende Punkte und fünf Verschärfungen. Alle behoben (Details in ENG-004):

- **K1 (Root-Escape):** Die sudoers-Regel `systemctl status` wurde entfernt. `status` läuft
  per Default durch einen Pager (`less`), aus dem sich via `!sh` eine Root-Shell öffnen ließe —
  ein kompromittierter Deploy-Key hätte zu vollem Root eskaliert. Statusdiagnose erfolgt jetzt
  unprivilegiert (`systemctl status --no-pager`, world-lesbares `/var/log/binokel`).
- **K2 (fail-open Secret):** `settings.py` bricht bei `DEBUG=False` hart ab
  (`ImproperlyConfigured`), wenn `DJANGO_SECRET_KEY` fehlt bzw. dem Insecure-Default entspricht.
- **E1 (Least Privilege Static):** `binokel-app` erhält auf `STATIC_DIR` nur noch `rX` (Eigentümer
  ist `binokel-deploy`); der exponierte Dienst kann keine Dateien mehr ins ausgelieferte
  Static-Verzeichnis schreiben. `DATA_DIR` bleibt `rwX` (SQLite zur Laufzeit).
- **E2 (Header-Ownership):** Security-Header werden nicht mehr doppelt/widersprüchlich gesetzt.
  Django liefert sie für proxied Antworten, Nginx exklusiv im `/static/`-Block; die Werte
  (u. a. Referrer-Policy) sind angeglichen.
- **E3 (systemd-Härtung):** `ProtectSystem=strict` + `ReadWritePaths`, `ProtectHome`,
  `PrivateDevices`, `SystemCallFilter=@system-service`, `RestrictAddressFamilies` u. a.
- **E4:** `server_tokens off;` (Versions-Disclosure).
- **E5:** Der CD-Deploy liest den echten `DJANGO_SECRET_KEY` nicht mehr — migrate/collectstatic
  laufen mit einem Wegwerf-Schlüssel (schlüssel-unabhängig); nur die nicht-geheimen Pfad-Variablen
  werden aus der env gelesen.
