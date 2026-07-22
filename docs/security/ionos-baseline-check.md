# IONOS-Security-Baseline — Compliance-Abgleich

> **Zweck:** Abgleich der IONOS-Sicherheitsempfehlungen für Linux-Server mit dem
> Ist-Zustand des Binokel-Score-Tracker-Deployments (V1, Ubuntu 24.04 LTS).
> **Quelle:** IONOS-Hilfe-Center-Artikel „Wichtige Sicherheitsinformationen für
> Ihren Linux-Server" (Teil 1 + 2), „SSH-Root-Login deaktivieren", „SSH-Port ändern".
> Die Empfehlungen sind hier **in eigenen Worten zusammengefasst** (kein Verbatim-Zitat;
> die Original-PDFs bleiben lokal und werden nicht ins Repository aufgenommen).
> **Normative Quellen bei uns:** `docs/adr/ADR-009-internet-hardening-baseline.md`,
> `deploy/setup-server.sh`, `deploy/runbook-task-ci-006.md`,
> `docs/engineering-notes/ENG-004-deployment-hardening-fallstricke.md`.

**Legende Status:** ✅ erfüllt · 🟡 teilweise / Verbesserung möglich · 🔴 offen (Handlung nötig) · ⚪ bewusst nicht im V1-Scope

---

## Abgleich

| # | IONOS-Empfehlung (paraphrasiert) | Ist-Zustand bei uns | Status | Maßnahme / Notiz |
|---|---|---|---|---|
| 1 | Sicherheitspatches/Updates zeitnah & automatisch installieren | `unattended-upgrades` + `apt-listchanges` (setup-server.sh [10/10]) | ✅ | Reboot-Fenster optional via `Automatic-Reboot-Time` |
| 2 | Public-Key-Auth statt Passwort-Auth | `PasswordAuthentication no` (Phase 1, lockout-sicher verifiziert) | ✅ | Effektivwert per `sshd -T` geprüft |
| 3 | Starke Passwörter (≥12 Zeichen, gemischt) | Admin-sudo-Passwort (Nutzer); `DJANGO_SECRET_KEY` wird **manuell** erzeugt (env-Platzhalter), Guard prüft nur ≠ Insecure-Default (nicht Länge/Entropie) | 🟡 | Admin-Passwortstärke + Key-Erzeugung liegen beim Betreiber; Länge selbst sicherstellen |
| 4 | Backup-Strategie inkl. **getesteter Restores** | Tägliches Backup (cron.d, 03:00) + 30-Tage-Retention | 🔴 | **`cp` auf Live-SQLite → Konsistenzrisiko** (siehe #20); Fehler werden per `2>/dev/null||true` verschluckt; Backups auf gleicher Platte; Restore-Test fehlt |
| 5 | Lokale Dienste nur an `localhost` binden | Gunicorn über Unix-Socket (`/run/binokel`), SQLite lokale Datei; extern nur nginx 80/443 | ✅ | Kein DB-Port nach außen |
| 6 | VPN für Server-Zugriff | Öffentliche Web-App; Admin-Zugang per SSH-Key | ⚪ | Für V1 nicht anwendbar |
| 7 | Server-Zugriff auf nötige Benutzer beschränken | Least Privilege: `binokel-app` (kein Login), `binokel-deploy` (nur `systemctl restart/stop` via sudoers) | ✅ | K1-Review: `status` aus sudoers entfernt |
| 8 | Nur benötigte Anwendungen installieren | Minimale Paketliste (nginx, certbot, ufw, fail2ban, chrony, acl, git, curl) | ✅ | Aus offiziellen Quellen |
| 9 | Nur benötigte Ports öffnen | UFW: nur 22/80/443 | 🔴 | **IONOS-Cloud-Panel-Firewall: Ports 8000/8443/8447 noch offen → schließen** (bekanntes Go-Live-TODO) |
| 10 | Server überwachen (Monitoring) | Healthcheck `/health/` + `journalctl` + `/var/log/binokel/error.log` | 🟡 | Kein aktives Alerting (für V1 akzeptiert) |
| 11 | Regelmäßig auf Malware/Viren prüfen (ClamAV, rkhunter) | Nicht eingerichtet | ⚪ | Optional für V1; Angriffsfläche durch minimale Installation gering |
| 12 | SSH-Root-Login deaktivieren | `PermitRootLogin no` (Phase 1) | ✅ | Verifiziert: Root-Login abgewiesen |
| 13 | SSH-Port ändern (Brute-Force-Reduktion) | Bewusst Port **22**; fail2ban als Kompensation | ⚪ | Ubuntu 24.04: SSH ist **socket-aktiviert** → Portwechsel via `ssh.socket`/`ListenStream`, **nicht** `Port` in `sshd_config` (Runbook-Hinweis korrigiert) |
| 14 | E-Mail-Benachrichtigung bei SSH-Logins | Nicht eingerichtet | � | Nice-to-have (gleiche Klasse wie #16 IDS); leichtgewichtig via `pam_exec`/`.profile` oder bewusst auf V2 |
| 15 | fail2ban gegen SSH-Brute-Force | `fail2ban` sshd-Jail (maxretry 5 / findtime 10m / bantime 1h) | ✅ | setup-server.sh [10/10] |
| 16 | Intrusion Detection System (AIDE/Tripwire/Psad) | Nicht eingerichtet | ⚪ | Optional für V1 |
| 17 | Mit Nmap auf offene Ports prüfen | Verifikation via `ufw status`; extern per Nmap möglich | 🟡 | **Externen Nmap-Check als Verifikationsschritt** in Phase 6 aufnehmen (bestätigt zugleich #9) |
| 18 | Distributions-Hardening-Guides konsultieren | ADR-009-Baseline + systemd-Härtung (E3: `ProtectSystem=strict`, `SystemCallFilter` u. a.) | ✅ | An Ubuntu/systemd-Hardening orientiert |
| 19 | Verdächtige Prozesse prüfen (`ps aux`) | Operativ / Incident-Response | ⚪ | Teil des Betriebs, nicht des Setups |
| 20 | Datenbanken absichern; **konsistenter Export** statt reinem Datei-Backup | SQLite lokal (kein phpMyAdmin o. ä.); Backup per `cp` | 🟡 | **`sqlite3 .backup` / `.dump` statt `cp`** für Konsistenz (v. a. bei WAL); siehe #4 |

---

## Handlungsbedarf (verdichtet)

> **Umsetzungsstand (22.07.2026):** #4/#20, RD-6 und RD-8 sind **umgesetzt** (Go-Live-Gate,
> siehe unten). Offener Go-Live-Blocker: **#9** (IONOS-Panel-Ports, Betreiber-Aktion).
> Offsite-DR ist bewusst als Fast-Follow zurückgestellt (FUTURE-003).

**Vor Go-Live (blockierend/wichtig):**
- **#9** IONOS-Cloud-Panel-Firewall: Ports **8000/8443/8447 schließen** (nur 22/80/443). Bereits als Go-Live-TODO geführt. 🔴 **offen (Betreiber)**
- **#4 / #20** SQLite-Backup von `cp` auf **konsistenten `sqlite3 .backup`** umstellen. ✅ **umgesetzt** (`/usr/local/bin/binokel-backup.sh` + `integrity_check` + atomarer `mv`; Restore-Probe Runbook 6.2)

**Empfohlen (nicht blockierend):**
- **#17** Externen **Nmap-Portscan** als Verifikationsschritt in Runbook Phase 6 ergänzen (bestätigt #9 unabhängig).
- **#14** SSH-Login-**E-Mail-Benachrichtigung** — leichtgewichtig umsetzen oder bewusst zurückstellen (Monitoring-Ausbau V2).
- **#4** **Restore-Test** dokumentieren/periodisch durchführen.

---

## Rubber-Duck-Audit (22.07.2026) — Zusatzbefunde außerhalb der IONOS-Liste

Der Rubber-Duck-Agent hat die Matrix gegen die realen Configs auditiert. Votum:
**NO-GO bis #9 + #4/#20 behoben**, danach GO. Zusätzlich gefundene Risiken:

| Nr | Befund | Schwere | Quelle | Empfehlung |
|---|---|---|---|---|
| RD-6 | Django-`/admin/` internet-exponiert; fail2ban schützt nur sshd, nicht `/admin/` | MITTEL | `backend/binokel_tracker/urls.py` | ✅ **umgesetzt**: `/admin/`-Route in V1 entfernt (kein Superuser nötig); Reaktivierung nur mit Nginx-IP-Allowlist |
| RD-7 | POST-Endpunkte `spiele_view`/`runden_view` sind `@csrf_exempt` → CSRF-Schutz für diese Endpunkte wirkungslos | MITTEL | `backend/scoring/views.py` (Z. 80, 134) | Bestätigt. Für token-lose JSON-API vertretbar, aber bewusst begründen/dokumentieren (V1 hat keine Auth) |
| RD-8 | HSTS `preload` + `includeSubDomains` (1 Jahr) auf Subdomain committet alle Geschwister-Subdomains, praktisch irreversibel | MITTEL | `backend/binokel_tracker/settings.py` | ✅ **umgesetzt**: `preload`+`includeSubDomains` = `False` (host-scoped, reversibel); erst nach stabilem TLS scharf schalten |
| RD-9 | Backup-Fehler verschluckt (`2>/dev/null||true`) + kein Offsite (gleiche Platte) | MITTEL | `deploy/setup-server.sh` | 🟡 Exit-Code-Auswertung **umgesetzt** (`binokel-backup.sh`, `fail`+`exit 1`); Offsite → FUTURE-003 |
| RD-10 | `/run/binokel` `RuntimeDirectoryMode=0755` (Control-Socket + binokel.sock) | NIEDRIG | `deploy/binokel-tracker.service` | Sauberer `0750` + Gruppenzugriff für Nginx-User; dokumentieren |
| RD-11 | Deploy-User liest realen `SECRET_KEY` (`setfacl u:binokel-deploy:r /etc/binokel/env`) | NIEDRIG (akzeptiert) | ADR-009-Nachtrag | Residualrisiko festhalten: kompromittierter Deploy-Key ⇒ Signing-Forgery |
| RD-12 | `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS`-Platzhalter surfacen erst zur Laufzeit | NIEDRIG | ENG-004 | Pre-Go-Live-Verifikation über **echten** Domainnamen (nicht localhost) verpflichtend |

**Bewusst zurückgestellt (V1-Scope, ADR-009):**
- **#11** Malware-Scanner, **#16** IDS/AIDE, **#10** aktives Monitoring/Alerting, **#6** VPN, **#13** SSH-Port-Wechsel.

---

## Prüf-Workflow für die Agenten

1. **Rubber-Duck-Agent** auditiert diese Matrix gegen die realen Configs
   (`setup-server.sh`, `settings.py`, `nginx.conf.template`, `binokel-tracker.service`,
   sshd-Drop-in) und benennt Fehleinschätzungen/zusätzliche Risiken mit Schwere.
2. **Dev/Ops-Agent** plant die Remediation der bestätigten 🔴/🟡-Punkte
   (Skript-/Runbook-Änderungen, Rollback), Rubber-Duck gibt frei.
3. Umsetzung → erneuter Kurz-Check → Go-Live.
