# Runbook TASK-CI-006 — VM einrichten, Secrets hinterlegen, erster Produktions-Deploy

> **Status:** Geplant / noch nicht auf realer VM ausgeführt.
> **Rubber-Duck-Review erfolgt (21.07.2026)** — die dort gefundenen 5 Blocker wurden in
> `settings.py`, `setup-server.sh`, `nginx.conf.template` und `cd.yml` behoben
> (Details: `docs/engineering-notes/ENG-004-deployment-hardening-fallstricke.md`).
> Dieses Runbook ist eine **Ausführungsanleitung** für den erstmaligen Aufbau der
> Produktionsumgebung auf einer neuen **1&1 / IONOS-VM mit frisch installiertem
> Ubuntu 24.04 LTS** (Referenzplattform, siehe ADR-008). Es wurde als reine Planungs-
> und Dokumentationsarbeit erstellt — es wurden **keine** SSH-Verbindungen aufgebaut,
> **keine** echten Secrets erzeugt und **kein** Deploy ausgelöst.
>
> **Normative Quellen:** `docs/adr/ADR-007-github-actions-ci-cd.md`,
> `docs/adr/ADR-008-vm-deployment-strategie.md`,
> `docs/adr/ADR-009-internet-hardening-baseline.md`,
> Betriebsrunbook `deploy/README.md`.

---

## Platzhalter-Konvention

Alle Beispiele verwenden konsistente Platzhalter (identisch zu `deploy/README.md`).
Vor der echten Ausführung durch die realen Werte ersetzen:

| Platzhalter | Bedeutung | Beispiel |
|---|---|---|
| `binokel.example.com` | Produktions-Domain (DNS zeigt auf VM-IP) | *reale Domain* |
| `203.0.113.10` | Öffentliche IPv4 der VM (RFC-5737-Doku-IP) | *reale IP* |
| `binokel-admin` | Non-root Admin-User mit sudo (SSH-Login für Menschen) | frei wählbar |
| `binokel-deploy` | Deploy-User für die CD-Pipeline (SSH, kein sudo außer systemctl) | fix |
| `binokel-app` | System-User, unter dem Gunicorn läuft (kein Login) | fix |
| `/opt/binokel/...` | App-, Daten- und Static-Verzeichnisse | fix |
| `/etc/binokel/env` | Produktionskonfiguration (Secrets, 12-Factor) | fix |
| `2222` | Optionaler SSH-Port (Standard bleibt 22, siehe Phase 1) | frei wählbar |

**Grundregeln (aus `docs/agents/devops-agent.md`):**
- Secrets **niemals** ins Repository — nur GitHub-Secrets oder `/etc/binokel/env`.
- 12-Factor: Laufzeitkonfiguration ausschließlich über Umgebungsvariablen.
- Least Privilege für User, Verzeichnisse und Credentials.
- Jede Phase hat **Verifikation** und **Rollback/Recovery**.

---

## Phasen-Überblick

| Phase | Inhalt | Ausführender | Automatisiert? |
|---|---|---|---|
| 0 | Voraussetzungen (VM, DNS, lokaler SSH-Key) | Betreiber lokal | — |
| 1 | Erst-Login + Internet-Hardening der VM | Betreiber (manuell) | teilweise |
| 2 | App-Setup via `setup-server.sh` | Betreiber (root/sudo) | ja |
| 3 | `/etc/binokel/env` befüllen | Betreiber (root) | manuell |
| 4 | Deploy-SSH-Key + GitHub-Secrets | Betreiber | manuell |
| 5 | Branch Protection für `main` | Betreiber (GitHub UI) | manuell |
| 6 | Erster Deploy auslösen + verifizieren | Betreiber (GitHub Actions) | ja |

> **Wichtige Aufgabenteilung Hardening ↔ Script:**
> Das SSH-Daemon-Hardening (Root-Login/Passwort-Login abschalten, ggf. Port) wird
> **bewusst manuell in Phase 1** ausgeführt — **nicht** in `setup-server.sh`.
> Begründung siehe [ADR-009](../docs/adr/ADR-009-internet-hardening-baseline.md) und
> Abschnitt „Warum SSH-Hardening manuell bleibt“ unten.
> `fail2ban`, automatische Sicherheitsupdates (`unattended-upgrades`) und Zeit-Sync
> (`chrony`) werden dagegen **idempotent von `setup-server.sh`** übernommen.

---

## Phase 0 — Voraussetzungen

**Ziel:** Alle externen Abhängigkeiten stehen, bevor die VM angefasst wird.

### Checkliste

- [ ] VM bei 1&1 / IONOS bestellt, Image: **Ubuntu 24.04 LTS (frisch installiert)**.
- [ ] Öffentliche IPv4 (und ggf. IPv6) der VM notiert: `203.0.113.10`.
- [ ] **DNS**: A-Record `binokel.example.com` → `203.0.113.10` gesetzt
      (bei IPv6 zusätzlich AAAA-Record).
- [ ] Root-Zugang zur VM vorhanden (Passwort oder Key vom Provider-Panel).
- [ ] **Lokaler SSH-Key** für den Admin-User vorhanden (Ed25519 empfohlen).

### Befehle (lokal, auf dem Betreiber-Rechner)

```bash
# Admin-SSH-Key erzeugen (falls noch nicht vorhanden)
ssh-keygen -t ed25519 -a 100 -C "binokel-admin@$(hostname)" -f ~/.ssh/binokel_admin

# DNS-Auflösung prüfen (muss die VM-IP liefern, BEVOR Certbot in Phase 2 läuft)
dig +short binokel.example.com
# Erwartet: 203.0.113.10
```

### Verifikation

- `dig +short binokel.example.com` liefert exakt die VM-IP.
- Kein alter A-Record / kein Proxy (z. B. Cloudflare „orange cloud") aktiv, der die
  ACME-HTTP-01-Challenge von Certbot stören würde.

### Rollback / Recovery

- Noch keine Änderungen an der VM → kein Rollback nötig.
- Falls DNS falsch: A-Record korrigieren und TTL-Propagation abwarten
  (`dig +short binokel.example.com @1.1.1.1` zum Gegenprüfen).

---

## Phase 1 — Erst-Login + Internet-Hardening

**Ziel:** Die VM wird vom Auslieferungszustand in einen für das offene Internet
gehärteten Zustand überführt, **bevor** die Anwendung installiert wird.

> Referenz-Baseline und Begründung: [ADR-009](../docs/adr/ADR-009-internet-hardening-baseline.md).

### Was deckt `setup-server.sh` bereits ab, was ist hier manuell?

| Maßnahme | Ort | Warum |
|---|---|---|
| UFW-Firewall (deny incoming, nur SSH/HTTP/HTTPS) | `setup-server.sh` (Phase 2) | idempotent, ungefährlich |
| `fail2ban` (Brute-Force-Schutz SSH) | `setup-server.sh` (Phase 2) | idempotent, ungefährlich |
| `unattended-upgrades` (autom. Sicherheitsupdates) | `setup-server.sh` (Phase 2) | idempotent, ungefährlich |
| Zeit-Sync (`chrony`) | `setup-server.sh` (Phase 2) | idempotent, ungefährlich |
| Non-root Admin-User + sudo | **Phase 1 manuell** | menschlicher Key erforderlich |
| SSH-Key-only, Root-Login aus, Passwort-Login aus, Port | **Phase 1 manuell** | Lockout-Risiko → menschliche Verifikation nötig |

**Warum SSH-Hardening manuell bleibt:** Ein Skript kann sich nicht selbst gegen
einen SSH-Lockout absichern. Das sichere Vorgehen verlangt eine **zweite, parallel
offene SSH-Sitzung** zur Verifikation, bevor die erste geschlossen wird — das ist
eine menschliche Kontrollhandlung. Deshalb wird das sshd-Hardening bewusst hier
im Runbook gehalten (siehe ADR-009), während gefahrlose, idempotente Maßnahmen
(`fail2ban`, `unattended-upgrades`, `chrony`) vom Skript übernommen werden.

### Schritt 1.1 — Erst-Login als root und System aktualisieren

```bash
# Lokal:
ssh root@203.0.113.10

# Auf der VM:
apt-get update && apt-get upgrade -y
```

### Schritt 1.2 — Non-root Admin-User mit sudo anlegen

```bash
# Auf der VM (als root):
adduser --gecos "" binokel-admin          # Passwort setzen (nur als Notfall-Fallback)
usermod -aG sudo binokel-admin

# SSH-Key des Admins hinterlegen
install -d -m 700 -o binokel-admin -g binokel-admin /home/binokel-admin/.ssh
# Öffentlichen Key einfügen (Inhalt von ~/.ssh/binokel_admin.pub vom lokalen Rechner):
nano /home/binokel-admin/.ssh/authorized_keys
chmod 600 /home/binokel-admin/.ssh/authorized_keys
chown binokel-admin:binokel-admin /home/binokel-admin/.ssh/authorized_keys
```

> Alternativ vom lokalen Rechner (solange Root-Login noch offen ist):
> `ssh-copy-id -i ~/.ssh/binokel_admin.pub binokel-admin@203.0.113.10`

### Schritt 1.3 — Key-Login des Admins verifizieren (VOR dem Hardening!)

```bash
# Lokal, in einem ZWEITEN Terminal — die root-Sitzung offen lassen!
# Key-Login muss funktionieren UND binokel-admin muss in der sudo-Gruppe sein.
# (Kein `sudo -n`-Check: ein Admin-User braucht bewusst ein Passwort für sudo —
#  passwortloses sudo ist hier NICHT gewollt.)
ssh -i ~/.ssh/binokel_admin binokel-admin@203.0.113.10 \
  'echo LOGIN_OK; id | grep -qw "(sudo)" && echo SUDO_GROUP_OK || echo SUDO_GROUP_MISSING'
```

**Erst weitermachen, wenn `LOGIN_OK` und `SUDO_GROUP_OK` erscheinen.** Ansonsten
Key/Rechte bzw. `usermod -aG sudo binokel-admin` korrigieren. Das sudo-Passwort des
Admins wird beim späteren `sudo` interaktiv abgefragt (gewollt).

> **Host-Key-Wechsel nach VM-Neuinstallation:** Wird eine bereits genutzte IP neu
> aufgesetzt (z. B. Wegwerf-VM → Prod auf derselben IP), meldet SSH beim ersten
> Connect `REMOTE HOST IDENTIFICATION HAS CHANGED`. Das ist hier erwartet (kein MITM).
> Alten Eintrag entfernen: `ssh-keygen -R 203.0.113.10`, dann neu verbinden und den
> neuen Host-Key bestätigen.

### Schritt 1.4 — sshd härten (Drop-in, kein Überschreiben der Hauptdatei)

```bash
# Auf der VM (als binokel-admin via sudo, root-Sitzung weiterhin offen halten):
# WICHTIG: Präfix 00- (nicht 99-)! sshd nimmt bei jedem Keyword den ERSTEN
# gefundenen Wert. Ubuntu-Cloud-Images liefern 50-cloud-init.conf mit
# `PasswordAuthentication yes`; eine 99-Datei würde ZU SPÄT gelesen und NICHT
# greifen. 00- wird vor allen Cloud-Dateien gelesen und gewinnt (siehe ENG-004).
sudo tee /etc/ssh/sshd_config.d/00-binokel-hardening.conf > /dev/null << 'EOF'
# Binokel Internet-Hardening-Baseline (ADR-009)
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
ChallengeResponseAuthentication no
PubkeyAuthentication yes
X11Forwarding no
MaxAuthTries 3
LoginGraceTime 30
# Optional: SSH auf nicht-Standardport (dann UFW-Regel + ssh-keyscan anpassen!)
# Port 2222
EOF

# Syntax prüfen — DARF keine Fehler zeigen:
sudo sshd -t

# Erst nach fehlerfreiem Test neu laden:
sudo systemctl reload ssh

# EFFEKTIVE Werte gegenprüfen (nicht nur die Datei!) — muss `no` für Passwort/Root zeigen:
sudo sshd -T | grep -Ei 'permitrootlogin|passwordauthentication|kbdinteractive|pubkeyauthentication'
```

> **Wenn `Port 2222` aktiviert wird:** In Phase 2 die UFW-Regel anpassen
> (`ufw allow 2222/proto tcp` statt `ufw allow ssh`) und in Phase 4 den Port beim
> `ssh-keyscan` und in `VM_HOST`/SSH-Aufrufen berücksichtigen. Für V1 wird der
> Standardport 22 empfohlen (fail2ban schützt ausreichend, weniger Fehlerquellen).

### Verifikation (Phase 1)

```bash
# Neues, DRITTES Terminal — bestätigt, dass Key-Login nach dem Reload noch geht:
ssh -i ~/.ssh/binokel_admin binokel-admin@203.0.113.10 'echo LOGIN_OK'

# Muss FEHLSCHLAGEN (Passwort-Login deaktiviert):
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no \
    binokel-admin@203.0.113.10 || echo "Passwort-Login korrekt deaktiviert"

# Muss FEHLSCHLAGEN (Root-Login deaktiviert):
ssh root@203.0.113.10 || echo "Root-Login korrekt deaktiviert"
```

**Erst wenn `LOGIN_OK` bestätigt ist**, die ursprüngliche root-Sitzung schließen.

### Rollback / Recovery (Phase 1)

- **SSH-Lockout-Absicherung:** Die root-Sitzung aus Schritt 1.1 bleibt offen, bis
  der Key-Login verifiziert ist. Bei Problemen dort das Drop-in entfernen:
  ```bash
  rm /etc/ssh/sshd_config.d/00-binokel-hardening.conf
  systemctl reload ssh
  ```
- **Totaler Lockout (alle Sitzungen zu):** Über die **Web-/VNC-Konsole im
  1&1/IONOS-Panel** anmelden (Notfall-Root-Zugang), Drop-in entfernen, sshd neu laden.
- **Zeitpuffer:** Kein Schritt in Phase 1 ist irreversibel, solange eine offene
  Sitzung oder die Provider-Konsole existiert.

---

## Phase 2 — App-Setup via `setup-server.sh`

**Ziel:** Betriebsbenutzer, Verzeichnisse, `uv`, systemd-Dienst, Nginx+TLS,
Firewall, Logrotation sowie `fail2ban`, `unattended-upgrades` und `chrony` einrichten.

### Schritt 2.1 — Skript ausführen

```bash
# Auf der VM als binokel-admin:
curl -LO https://raw.githubusercontent.com/LarsBerberich/Binokel_Score_Tracker_BDD/main/deploy/setup-server.sh
sudo bash setup-server.sh binokel.example.com https://github.com/LarsBerberich/Binokel_Score_Tracker_BDD.git
```

Das Skript ist idempotent und richtet ein:
- Betriebsbenutzer `binokel-app` (App) und `binokel-deploy` (CI/CD)
- Verzeichnisstruktur unter `/opt/binokel/` inkl. POSIX-ACLs für gemeinsamen
  Schreibzugriff auf `data`/`static` (App-Dienst + Deploy-User)
- systemd-Dienst + Nginx mit TLS (Let's Encrypt via Certbot)
- **fail2ban** (SSH-Brute-Force-Schutz)
- **unattended-upgrades** (automatische Sicherheitsupdates)
- **chrony** (Zeit-Sync)
- UFW-Firewall (nur SSH/HTTP/HTTPS), Logrotation, tägliches SQLite-Backup (`cron.d`)

> **Nginx/Certbot-Reihenfolge (Henne-Ei):** Das Skript rollt beim Erstlauf zunächst
> einen HTTP-only-Serverblock aus, fordert dann per `certbot --nginx` das Zertifikat
> an und aktiviert erst danach das vollständige Template mit 443/TLS. Dadurch
> scheitert `nginx -t` nicht an noch fehlenden Zertifikatsdateien (siehe ENG-004).

> **DNS-Abhängigkeit:** Certbot fordert das Zertifikat live an. `binokel.example.com`
> **muss** bereits auf die VM zeigen (Phase 0), sonst schlägt die ACME-Challenge fehl.

### Verifikation (Phase 2)

```bash
# Dienste laufen / sind aktiviert:
systemctl is-enabled binokel-tracker.service
systemctl status nginx --no-pager
systemctl status fail2ban --no-pager
systemctl status chrony --no-pager

# Automatische Sicherheitsupdates aktiv:
systemctl status unattended-upgrades --no-pager
sudo unattended-upgrades --dry-run --debug 2>&1 | tail -n 20

# fail2ban SSH-Jail aktiv:
sudo fail2ban-client status sshd

# Firewall-Status:
sudo ufw status verbose

# TLS-Zertifikat vorhanden:
sudo certbot certificates

# Preflight (wie im CD-Workflow) — alle vier Prüfungen müssen bestehen:
command -v uv && test -d /opt/binokel/app && test -f /etc/binokel/env \
  && test -f /etc/systemd/system/binokel-tracker.service && echo "PREFLIGHT_OK"
```

> Der Dienst `binokel-tracker` ist an dieser Stelle noch **nicht** funktionsfähig,
> weil `/etc/binokel/env` erst in Phase 3 befüllt wird — das ist erwartet.

### Rollback / Recovery (Phase 2)

- Das Skript ist idempotent → bei Abbruch erneut ausführbar.
- **Certbot fehlgeschlagen (DNS/Rate-Limit):** DNS korrigieren, dann nur TLS
  nachziehen: `sudo certbot --nginx -d binokel.example.com`. Let's-Encrypt-
  Rate-Limits beachten → zum Testen ggf. `--staging` verwenden.
- **Nginx-Fehlkonfiguration:** `sudo nginx -t` zeigt die Ursache; Symlink
  `/etc/nginx/sites-enabled/binokel-tracker` prüfen, `sudo systemctl reload nginx`.
- **Kompletter Fehlstart:** VM ist noch „leer" (keine Nutzdaten) → Neuinstallation
  der VM und Wiederholung ab Phase 1 ist ein valider Rollback.

---

## Phase 3 — `/etc/binokel/env` befüllen

**Ziel:** Produktionskonfiguration (12-Factor) setzen. Diese Datei enthält das
einzige Laufzeit-Secret der V1 (`DJANGO_SECRET_KEY`).

### Schritt 3.1 — SECRET_KEY erzeugen und Datei befüllen

```bash
# Auf der VM als binokel-admin:

# Sicheren Schlüssel erzeugen (Ausgabe in die Zwischenablage/Datei übernehmen):
python3 -c "import secrets; print(secrets.token_urlsafe(60))"

sudo nano /etc/binokel/env
```

Inhalt (Platzhalter ersetzen — **niemals** den Insecure-Default aus `settings.py`):

```env
DJANGO_SECRET_KEY=<erzeugter Schlüssel, min. 50 Zeichen>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=binokel.example.com
DJANGO_DB_PATH=/opt/binokel/data/db.sqlite3
DJANGO_STATIC_ROOT=/opt/binokel/static
DJANGO_CSRF_TRUSTED_ORIGINS=https://binokel.example.com
```

### Schritt 3.2 — Rechte setzen (Least Privilege)

```bash
# Nur root darf schreiben, binokel-app darf lesen — sonst niemand:
sudo chown root:binokel-app /etc/binokel/env
sudo chmod 640 /etc/binokel/env
```

### Verifikation (Phase 3)

```bash
# Rechte müssen -rw-r----- root binokel-app sein:
ls -l /etc/binokel/env

# Django-Deployment-Check gegen die echte Konfiguration (keine Warnungen erwartet):
sudo -u binokel-app bash -c '
  set -a; . /etc/binokel/env; set +a
  cd /opt/binokel/app/backend
  uv run python manage.py check --deploy
'
```

`check --deploy` darf **keine** sicherheitsrelevanten Warnungen zu `SECRET_KEY`,
`DEBUG`, `ALLOWED_HOSTS`, HSTS oder Secure-Cookies mehr melden.

### Rollback / Recovery (Phase 3)

- Datei ist rein lokal und reversibel → bei Fehlkonfiguration einfach neu editieren.
- **SECRET_KEY kompromittiert / versehentlich geleakt:** neuen Schlüssel erzeugen,
  eintragen, Dienst neu starten (`sudo systemctl restart binokel-tracker`).
  Folge: bestehende Sessions/CSRF-Tokens werden ungültig (in V1 unkritisch).
- **Falsche Rechte (zu offen):** sofort `chmod 640` + `chown root:binokel-app`
  korrigieren; prüfen, ob die Datei zwischenzeitlich für andere lesbar war.

---

## Phase 4 — Deploy-SSH-Key + GitHub-Secrets

**Ziel:** Der CD-Pipeline einen dedizierten, minimal berechtigten SSH-Zugang geben
und die zugehörigen GitHub-Secrets hinterlegen.

> **Eigenständige Detailanleitung:** [`secrets-setup.md`](secrets-setup.md) —
> lückenlose Schritt-für-Schritt-Prozedur mit den realen Werten dieses Deployments
> (Keypair erzeugen, Public-Key auf VM, `known_hosts`, GitHub-Environment `production`,
> die vier Secrets, Verifikation, Rotation, Troubleshooting). Die folgenden Schritte
> sind die Kurzfassung.


### Schritt 4.1 — Deploy-Key erzeugen (ohne Passphrase, da nicht-interaktiv)

```bash
# Empfohlen: LOKAL erzeugen, privaten Teil nur nach GitHub, öffentlichen auf die VM.
ssh-keygen -t ed25519 -a 100 -C "binokel-deploy@ci" -N "" -f ~/.ssh/binokel_deploy
```

### Schritt 4.2 — Öffentlichen Key auf der VM eintragen

```bash
# Auf der VM als binokel-admin — authorized_keys des Deploy-Users setzen:
sudo install -d -m 700 -o binokel-deploy -g binokel-deploy /home/binokel-deploy/.ssh
# Inhalt von ~/.ssh/binokel_deploy.pub einfügen:
sudo -u binokel-deploy nano /home/binokel-deploy/.ssh/authorized_keys
sudo chmod 600 /home/binokel-deploy/.ssh/authorized_keys
sudo chown binokel-deploy:binokel-deploy /home/binokel-deploy/.ssh/authorized_keys
```

> **Optionale Härtung** in `authorized_keys` (Prefix vor dem Key), da die Pipeline
> nur rsync + wenige Kommandos braucht: `from="140.82.112.0/20"` schränkt die
> Quell-IPs ein (GitHub-Actions-Ranges ändern sich jedoch — nur mit Pflege sinnvoll).

### Schritt 4.3 — Host-Keys für `known_hosts` einsammeln (MITM-Schutz)

```bash
# Lokal (liefert die echten Host-Keys der VM):
ssh-keyscan -H 203.0.113.10
# Bei custom Port: ssh-keyscan -H -p 2222 203.0.113.10
```

### Schritt 4.4 — GitHub-Secret + -Variables hinterlegen

Klassifikation nach Vertraulichkeit: **nur der private Key ist ein Secret**, der Rest
ist nicht-geheime Konfiguration (**Variables**). Empfohlen unter Environment
`production` (Detailanleitung: [`secrets-setup.md`](secrets-setup.md)).

**Settings → Environments → `production`:**

| Name | Typ | Inhalt |
|---|---|---|
| `VM_SSH_KEY` | **Secret** | **Privater** Key: kompletter Inhalt von `~/.ssh/binokel_deploy` |
| `VM_HOST` | **Variable** | `203.0.113.10` (oder `binokel.example.com`) |
| `VM_USER` | **Variable** | `binokel-deploy` |
| `VM_SSH_KNOWN_HOSTS` | **Variable** | **(Pflicht)** Ausgabe von `ssh-keyscan -H` aus Schritt 4.3 — ohne diesen Wert bricht der CD-Workflow bewusst ab (kein Laufzeit-`ssh-keyscan`-Fallback, MITM-Schutz). Öffentliche Host-Keys → kein Secret nötig. |

### Verifikation (Phase 4)

```bash
# Lokal: Deploy-Key funktioniert:
ssh -i ~/.ssh/binokel_deploy binokel-deploy@203.0.113.10 'echo DEPLOY_LOGIN_OK'

# Status läuft UNPRIVILEGIERT (kein sudo — die sudo-status-Regel wurde wegen
# Pager-Root-Escape entfernt, siehe ENG-004 K1):
ssh -i ~/.ssh/binokel_deploy binokel-deploy@203.0.113.10 \
    'systemctl status binokel-tracker.service --no-pager >/dev/null && echo STATUS_OK'

# Erlaubte sudo-Kommandos anzeigen — es dürfen NUR restart/stop erscheinen:
ssh -i ~/.ssh/binokel_deploy binokel-deploy@203.0.113.10 'sudo -n -l'

# Least-Privilege-Gegenprobe: darf KEIN beliebiges sudo:
ssh -i ~/.ssh/binokel_deploy binokel-deploy@203.0.113.10 \
    'sudo -n cat /etc/binokel/env 2>/dev/null && echo "FEHLER: zu viele Rechte!" || echo "OK: eingeschränkt"'
```

- In GitHub: alle vier Secrets sind angelegt (Werte nicht mehr einsehbar — korrekt).

### Rollback / Recovery (Phase 4)

- **Deploy-Key kompromittiert:** Zeile aus `/home/binokel-deploy/.ssh/authorized_keys`
  entfernen, neuen Key erzeugen, `VM_SSH_KEY` in GitHub rotieren.
- **Falsche `known_hosts`:** `VM_SSH_KNOWN_HOSTS` neu setzen. Es gibt **keinen**
  Laufzeit-`ssh-keyscan`-Fallback mehr — bei fehlendem/falschem Secret bricht der
  CD-Workflow bewusst ab (MITM-Schutz, ADR-009).
- Secrets sind jederzeit in GitHub überschreib-/löschbar → voll reversibel.

---

## Phase 5 — Branch Protection für `main`

**Ziel:** Kein Deploy ohne grüne CI. Absicherung des Auslieferungspfads (ADR-007).

### Schritt 5.1 — Regel setzen

**GitHub → Settings → Branches → Add branch protection rule** für `main`:

- [x] **Require status checks to pass before merging** → Checks `BDD Akzeptanztests`
      **und** `Deploy-Skripte prüfen (shellcheck + bash -n)`
- [x] **Require branches to be up to date before merging**
- [x] **Require a pull request before merging** (empfohlen)
- [x] **Do not allow bypassing the above settings** (empfohlen)

### Verifikation (Phase 5)

- Testweise ein PR mit absichtlich rotem CI-Lauf lässt sich **nicht** mergen.
- Beide Status-Checks (`BDD Akzeptanztests`, `Deploy-Skripte prüfen (shellcheck + bash -n)`)
  erscheinen als „Required".

### Rollback / Recovery (Phase 5)

- Reine GitHub-Einstellung → jederzeit reversibel.
- **Notfall-Hotfix blockiert:** Regel kurzfristig lockern (nur durch Admin,
  dokumentieren) und nach dem Hotfix sofort wieder aktivieren.

---

## Phase 6 — Ersten Deploy auslösen + verifizieren

**Ziel:** Erstmalige Auslieferung über die CD-Pipeline und vollständige Verifikation.

### Schritt 6.1 — Deploy manuell auslösen

**GitHub → Actions → „CD – Deploy auf 1&1 VM" → Run workflow:**
- Branch: `main`
- Input `confirm`: **`yes`**

Der Workflow führt aus: Preflight → rsync → `uv sync` → `migrate` →
`collectstatic` → `systemctl restart` → Readiness-Healthcheck auf `/health/` →
**Post-Deploy-Smoke-Test** (End-to-End über öffentliches HTTPS).

> **Automatisiert seit CI/CD-Ausbau:** Der Smoke-Test-Step in `cd.yml` prüft nach
> jedem Deploy selbsttätig: `/health/` = 200 über TLS, `/admin/` = 404 (RD-6),
> HTTP→HTTPS-Redirect und den HSTS-Header. Schlägt einer fehl, wird der Deploy
> **rot**. Die folgenden `curl`-Kommandos sind damit nur noch optionale
> Nachkontrolle bzw. für Dinge, die die Pipeline nicht abdeckt (TLS-Zertifikatsdaten).

### Verifikation (Phase 6)

```bash
# 1. Öffentlicher Healthcheck über HTTPS (extern, vom Betreiber-Rechner):
curl -fsS https://binokel.example.com/health/ && echo " HEALTH_OK"

# 2. HTTP→HTTPS-Redirect greift:
curl -sI http://binokel.example.com/health/ | grep -i "^location: https://"

# 3. TLS-Zertifikat gültig / richtige Domain:
echo | openssl s_client -connect binokel.example.com:443 -servername binokel.example.com 2>/dev/null \
  | openssl x509 -noout -subject -dates

# 4. Sicherheits-Header vorhanden (HSTS etc.):
curl -sI https://binokel.example.com/ | grep -iE "strict-transport-security|x-content-type-options|x-frame-options"
```

Auf der VM (als `binokel-admin`):

```bash
systemctl status binokel-tracker.service --no-pager
journalctl -u binokel-tracker.service -n 50 --no-pager
tail -n 20 /var/log/binokel/error.log
```

### Schritt 6.2 — Backup- und Restore-Probe (Pflicht vor Go-Live-Freigabe)

Beweist einmalig, dass der Backup-Pfad einen **konsistenten, wiederherstellbaren**
Snapshot erzeugt (Sicherheits-Audit #4/#20). Zerstörungsfrei — fasst die Live-DB
nicht an.

```bash
# Als binokel-admin, nach dem ersten Deploy (DB existiert):
which sqlite3                                              # Paket vorhanden
sudo -u binokel-app /usr/local/bin/binokel-backup.sh       # Backup sofort erzwingen
journalctl -t binokel-backup -n 5 --no-pager               # -> "Backup OK: …"

LATEST=$(ls -1t /opt/binokel/data/db.sqlite3.bak.* | head -n1)
cp "$LATEST" /tmp/restore-probe.sqlite3
sqlite3 /tmp/restore-probe.sqlite3 'PRAGMA integrity_check;' # -> ok
sqlite3 /tmp/restore-probe.sqlite3 '.tables'                # Tabellen lesbar
rm -f /tmp/restore-probe.sqlite3
```

**Erfolgskriterium:** `sqlite3` vorhanden, journald meldet `Backup OK: …`,
`integrity_check` liefert `ok`, Tabellen sind lesbar.

**Deploy gilt als erfolgreich, wenn:** GitHub-Actions-Job grün, externer
`/health/` liefert HTTP 200 über HTTPS, TLS gültig, Security-Header gesetzt,
keine Fehler im `error.log`/Journal, **und die Backup-/Restore-Probe (6.2) grün**.

### Rollback / Recovery (Phase 6)

Ein **automatischer** Rollback auf eine frühere App-Version ist in der Pipeline
**nicht** implementiert (siehe `deploy/README.md`). Vorgehen bei fehlgeschlagenem Deploy:

1. Diagnose im GitHub-Actions-Log (Healthcheck-Step gibt `systemctl status` +
   `journalctl` aus).
2. **Fix-forward:** Korrektur committen und auf `main` pushen → neuer Deploy.
3. **Oder Revert:** letzten guten Commit per `git revert` auf `main` bringen →
   CD deployt die vorherige, funktionierende Version.
4. **Manueller Not-Deploy** direkt auf der VM (aus `deploy/README.md`):
   ```bash
   # Als binokel-deploy:
   cd /opt/binokel/app && git pull origin main
   cd backend && uv sync --no-dev
   set -a; . /etc/binokel/env; set +a   # Prod-Konfig laden (gleiche Pfade wie Dienst)
   uv run python manage.py migrate --noinput
   uv run python manage.py collectstatic --noinput
   sudo systemctl restart binokel-tracker.service
   curl -s http://localhost/health/
   ```
5. **DB-Recovery** (falls eine Migration die SQLite-DB beschädigt):
   letztes Backup aus `/opt/binokel/data/db.sqlite3.bak.YYYYMMDD` zurückspielen
   (Backup-Cron siehe `deploy/README.md`), Dienst neu starten.

---

## Betriebsrisiken und Gegenmaßnahmen

| Risiko | Auswirkung | Gegenmaßnahme |
|---|---|---|
| **DNS noch nicht propagiert**, bevor Certbot läuft | Certbot/ACME-Challenge schlägt fehl, kein TLS | Phase 0 abschließen; `dig +short` gegenprüfen; Certbot ggf. mit `--staging` testen, dann echt |
| **Falsche Rechte auf `/etc/binokel/env`** (zu offen) | Secret (`SECRET_KEY`) lesbar für andere User | Immer `chmod 640` + `chown root:binokel-app`; Verifikation in Phase 3; bei Leak Schlüssel rotieren |
| **SSH-Lockout durch Hardening-Fehler** | Kein Admin-Zugang mehr zur VM | Zweite Sitzung offen halten (Phase 1.3/1.4); Drop-in statt Hauptdatei; Notfall über 1&1/IONOS-Web-/VNC-Konsole |
| **Firewall sperrt SSH aus** | Aussperrung nach `ufw enable` | `setup-server.sh` erlaubt SSH vor `ufw --force enable`; bei custom Port `ufw allow 2222/tcp` **vor** dem Aktivieren; Provider-Konsole als Fallback |
| **Fehlende/ falsche `known_hosts`** | MITM-Risiko beim ersten CD-Connect | `VM_SSH_KNOWN_HOSTS` ist **Pflicht** (via `ssh-keyscan -H`, Phase 4); ohne das Secret bricht der CD-Workflow ab — kein Laufzeit-Fallback |
| **Deploy-User hat zu viele Rechte** | Kompromittierter CI-Key = Vollzugriff | sudoers auf drei `systemctl`-Kommandos begrenzt (Skript); Least-Privilege-Gegenprobe in Phase 4 |
| **Migration beschädigt SQLite-DB** | Datenverlust / Dienst startet nicht | Konsistentes tägliches Backup via `sqlite3 .backup` + `integrity_check` (`binokel-backup.sh`, vom `setup-server.sh` installiert); Restore-Probe Phase 6.2; Migrationen zuerst per `check` prüfen |
| **Let's-Encrypt-Rate-Limit** (zu viele Cert-Versuche) | Temporär keine Zertifikatsausstellung | Beim Testen `--staging`; erst nach erfolgreichem Test echtes Zertifikat |
| **Kein Auto-Rollback in der Pipeline** | Fehlerhafter Deploy bleibt live | Fix-forward oder `git revert` (Phase 6); Healthcheck lässt den Job fehlschlagen und zeigt Diagnose |
| **`unattended-upgrades` startet Dienst/Kernel neu** | Ungeplante Kurz-Downtime | Reboot-Zeitfenster konfigurierbar (`Unattended-Upgrade::Automatic-Reboot-Time`); systemd `Restart=on-failure` fängt App-Neustart ab |

---

## Ausblick V2 — Migrationspfad Docker + PostgreSQL

> Reiner Ausblick. **Nicht** Teil von TASK-CI-006. Grundsatzentscheidung „SQLite
> für V1, Docker+PostgreSQL später" ist in [ADR-008](../docs/adr/ADR-008-vm-deployment-strategie.md)
> dokumentiert; die Hardening-Baseline in [ADR-009](../docs/adr/ADR-009-internet-hardening-baseline.md).

Bei einer späteren Umstellung ändern sich insbesondere:

| Bereich | V1 (heute) | V2 (Docker + PostgreSQL) |
|---|---|---|
| **Laufzeit** | Gunicorn als systemd-Dienst | Container (Compose) für App; Nginx als Proxy bleibt oder wird Container |
| **Datenbank** | SQLite-Datei `/opt/binokel/data/db.sqlite3` | PostgreSQL-Dienst/-Container; neue Env-Vars `DJANGO_DB_*` (Host, Port, Name, User, Passwort) |
| **Config/Secrets** | `/etc/binokel/env` (600 root:root + ACL für binokel-deploy) | zusätzliche DB-Credentials als Secrets; ggf. Docker-Secrets / `env_file` |
| **CD-Pipeline** | rsync + `uv sync` + systemd-Restart | `docker build`/Registry-Push + `docker compose pull && up -d`; Migrationen im Container |
| **Backup** | `sqlite3 .backup` + `integrity_check` (Cron, `binokel-backup.sh`) | `pg_dump` / WAL-Archivierung, getestete Restores |
| **Rollback** | Fix-forward / `git revert` | Image-Tag zurückrollen (`docker compose` auf vorheriges Tag) |
| **Settings** | `DATABASES` auf `sqlite3` | `DATABASES` auf `postgresql`; App muss neue Env-Vars lesen |

**Übergabe an den Coding-Agent** wird dann nötig, weil Django neue Umgebungsvariablen
(DB-Verbindung) lesen und `settings.py` den PostgreSQL-Backend-Pfad unterstützen muss
(neue App-seitige Service-Abhängigkeit). Auslöser für die Neubewertung von ADR-008
sind: produktionsreifes Vue-Frontend oder zusätzliche Services (PostgreSQL/Redis).

---

## Punkte für den Rubber-Duck-Review (vor echter Ausführung)

Gemäß Leitlinie 8 (`docs/agents/devops-agent.md`) soll der Rubber-Duck-Agent vor der
tatsächlichen Ausführung folgende Punkte prüfen:

1. **SSH-Hardening-Reihenfolge** (Phase 1): Ist die „zweite Sitzung offen halten"-
   Absicherung ausreichend, oder soll zusätzlich ein zeitgesteuerter Auto-Revert
   (z. B. `sshd`-Restore per `at`-Job) vorgesehen werden?
2. **Aufgabenteilung Script ↔ Runbook**: Ist die Entscheidung, sshd-Hardening manuell
   zu halten, aber `fail2ban`/`unattended-upgrades`/`chrony` zu automatisieren,
   tragfähig? (Begründung in ADR-009.)
3. **SSH-Port**: Standardport 22 (empfohlen) vs. custom Port 2222 — Nutzen vs.
   zusätzliche Fehlerquelle (UFW, known_hosts, keyscan) für V1.
4. **`known_hosts`-Strategie**: `VM_SSH_KNOWN_HOSTS` als Pflicht behandeln statt
   optionalem Laufzeit-`ssh-keyscan` im CD-Workflow?
5. **Deploy-User-Rechte**: Sind die drei erlaubten `systemctl`-Kommandos in der
   sudoers-Datei das Minimum, oder braucht der Deploy für migrate/collectstatic
   weitere (aktuell laufen diese als `binokel-deploy` ohne sudo — bewusst so)?
6. **Auto-Reboot durch `unattended-upgrades`**: Reboot-Fenster/Policy festlegen, um
   ungeplante Downtime zu vermeiden.
7. **Kein Auto-Rollback**: Ist Fix-forward/`git revert` für V1 akzeptabel, oder soll
   ein simpler Release-Symlink-Rollback (vorherige rsync-Version) ergänzt werden?
8. **Backup vor erstem Deploy**: Backup-Cron aus `deploy/README.md` bereits VOR
   Phase 6 einrichten, damit die erste Migration abgesichert ist?

### Ergebnis des Rubber-Duck-Reviews (21.07.2026)

**Votum vor den Fixes: NO-GO.** Die Hardening-Baseline (ADR-009) selbst ist solide;
die Blocker lagen im Zusammenspiel von Setup-Skript, Nginx/Django-Konfiguration und
CD-Workflow. Alle 5 Blocker wurden behoben, Tests bleiben GREEN (28 Behave + 19 Django).

| Punkt | Votum | Ergebnis / Umsetzung |
|---|---|---|
| 1 SSH-Hardening-Reihenfolge | OK (Restrisiko akzeptiert) | Zweitsitzung + Provider-Konsole genügen; kein `at`-Auto-Revert nötig |
| 2 Aufgabenteilung Script↔Runbook | OK | Unverändert; ADR-009 trägt |
| 3 SSH-Port 22 vs. 2222 | OK (Risiko akzeptiert) | Port 22 + fail2ban für V1 |
| 4 `known_hosts`-Strategie | **Geändert** | `VM_SSH_KNOWN_HOSTS` ist jetzt **Pflicht**; Laufzeit-`ssh-keyscan`-Fallback entfernt (`cd.yml`) |
| 5 Deploy-User-Rechte | **Geändert** | migrate/collectstatic schrieben mangels Rechten nicht → POSIX-ACLs für `binokel-app`+`binokel-deploy` (`setup-server.sh`); sudoers-Pfad `/usr/bin/systemctl` |
| 6 Auto-Reboot unattended-upgrades | OK (Risiko akzeptiert) | Kein Auto-Reboot als Default; Reboot-Fenster bei Bedarf |
| 7 Kein Auto-Rollback | OK (Risiko akzeptiert) | Fix-forward/`git revert` für V1 |
| 8 Backup vor erstem Deploy | **Geändert** | Backup-Cron wird jetzt vom `setup-server.sh` automatisch installiert (Phase 2) |

**Zusätzlich behobene Blocker (nicht in der ursprünglichen 8-Punkte-Liste):**
- Redirect-Loop: `SECURE_PROXY_SSL_HEADER` fehlte (`settings.py`).
- Certbot Henne-Ei: `nginx -t` scheiterte vor der Zertifikatsausstellung (`setup-server.sh`).
- Falscher `uv`-Installationspfad (`setup-server.sh`).
- Healthcheck gegen HTTPS-Erzwingung: `SECURE_REDIRECT_EXEMPT` + `localhost` in `ALLOWED_HOSTS` + `location = /health/` im Port-80-Block.

Details und Präventionsregeln: `docs/engineering-notes/ENG-004-deployment-hardening-fallstricke.md`.

**Nächster Schritt vor realem Deploy:** Trockenlauf gegen eine Wegwerf-VM mit
Certbot `--staging` — vollständige Schritt-für-Schritt-Anleitung in
`deploy/runbook-dry-run.md`. Erst nach erfolgreichem Trockenlauf die Ausführung nach
diesem Runbook.
```

