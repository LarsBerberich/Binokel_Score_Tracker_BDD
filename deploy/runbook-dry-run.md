# Trockenlauf (Dry-Run) — Erst-Deploy gegen eine Wegwerf-VM

> **Zweck:** Den kompletten Ausführungspfad aus `runbook-task-ci-006.md` **einmal
> risikofrei** durchspielen, bevor er auf der echten Produktions-VM läuft. Ziel ist,
> Reihenfolge-, Rechte- und Konfigurationsfehler zu finden, **ohne** Produktionsdaten,
> Produktions-Domain oder Let's-Encrypt-Produktions-Rate-Limits zu berühren.
>
> **Normative Quellen:** `runbook-task-ci-006.md` (Produktionsablauf),
> `docs/adr/ADR-009-internet-hardening-baseline.md`,
> `docs/engineering-notes/ENG-004-deployment-hardening-fallstricke.md`.

---

## Prinzip — warum so?

| Entscheidung | Warum |
|---|---|
| **Wegwerf-VM** (frisches Ubuntu 24.04 LTS) | Ein fehlgeschlagener Schritt darf keinen echten Betrieb gefährden. Die VM wird nach dem Test gelöscht — jeder Fehler ist folgenlos. |
| **Certbot `--staging`** | Die Produktions-CA von Let's Encrypt hat harte Rate-Limits (u. a. 5 Zertifikate/Domain/Woche). Wiederholte Trockenläufe würden diese verbrauchen. Die **Staging-CA** ist praktisch unlimitiert. Das ausgestellte Zertifikat ist **bewusst ungültig** (Test-Wurzel), TLS-Kette und Nginx-Reload werden aber **echt** getestet. |
| **Test-Subdomain** (z. B. `staging.binokel.example.com`) | Certbots HTTP-01-Challenge braucht einen DNS-Namen, der auf die VM zeigt. Eine eigene Subdomain hält die Produktions-Domain sauber. |
| **Zwei Tiers (A vor B)** | Tier A testet Setup + App lokal **ohne** GitHub-Secrets (kleinste Angriffs-/Fehlerfläche). Tier B testet zusätzlich die CD-Pipeline über ein separates `staging`-Environment, **ohne** Produktions-Secrets zu überschreiben. |

**Was der Trockenlauf validiert:**
- `setup-server.sh` läuft auf frischem 24.04 idempotent durch (Pakete, `uv`, User,
  ACLs, systemd, Nginx-Bootstrap → Certbot → volles Template, Firewall, Backup-Cron).
- Django startet unter Gunicorn/systemd mit `DEBUG=False`.
- Der Reverse-Proxy-Pfad funktioniert: HTTP→HTTPS-Redirect, `/health/` liefert 200,
  Security-Header sind gesetzt, **kein** Redirect-Loop.
- migrate/collectstatic schreiben als `binokel-deploy` (ACL-Rechte greifen).

**Was er bewusst NICHT prüft:** die Vertrauenswürdigkeit des TLS-Zertifikats
(Staging-Cert ist absichtlich untrusted — Browser/`curl` warnen; das ist erwartet).

---

## Phase 0 — Voraussetzungen für den Trockenlauf

- [ ] Wegwerf-VM bei 1&1/IONOS: **Ubuntu 24.04 LTS**, eigene öffentliche IP.
- [ ] **Test-Subdomain** per A-Record auf die Wegwerf-VM-IP gesetzt
      (`staging.binokel.example.com` → Test-VM-IP). Mit `dig +short` prüfen.
- [ ] Lokaler Admin-SSH-Key vorhanden (wie Produktion, Runbook Phase 0).
- [ ] Klar dokumentiert, dass diese VM **nach dem Test gelöscht** wird.

> **Hinweis:** Ohne DNS-Namen schlägt selbst die Staging-Challenge fehl. Alternativ
> ließe sich `certbot ... --staging` durch die **DNS-01**-Methode ersetzen, das ist
> für V1 aber unnötig komplex — eine simple Test-Subdomain genügt.

---

## Phase 1 — Hardening (identisch zur Produktion)

Vollständig wie `runbook-task-ci-006.md` Phase 1 durchführen (Admin-User,
SSH-Key-only, sshd-Drop-in, zweite Sitzung offen halten). Der Trockenlauf ist genau
der richtige Ort, um die **manuelle** Hardening-Prozedur einzuüben, bevor sie an der
echten VM stattfindet.

---

## Phase 2 — Setup im Staging-Modus

```bash
# Auf der Wegwerf-VM als binokel-admin:
curl -LO https://raw.githubusercontent.com/LarsBerberich/Binokel_Score_Tracker_BDD/main/deploy/setup-server.sh

# ENTSCHEIDEND: CERTBOT_STAGING=1 → Test-Zertifikat statt Produktions-Zertifikat
sudo CERTBOT_STAGING=1 bash setup-server.sh staging.binokel.example.com \
    https://github.com/LarsBerberich/Binokel_Score_Tracker_BDD.git
```

Das Skript gibt beim Start `⚠️ CERTBOT_STAGING aktiv: …` aus — diese Zeile **muss**
erscheinen, sonst würde ein Produktions-Zertifikat angefordert.

### Verifikation (Phase 2)

```bash
# Dienste aktiv:
systemctl is-enabled binokel-tracker.service
systemctl status nginx fail2ban chrony --no-pager

# Staging-Zertifikat vorhanden und als (STAGING) markiert:
sudo certbot certificates | grep -i staging || sudo certbot certificates

# ACL-Rechte auf data/static gesetzt (binokel-app + binokel-deploy):
getfacl /opt/binokel/data /opt/binokel/static

# Backup-Cron installiert:
cat /etc/cron.d/binokel-backup

# uv systemweit:
command -v uv
```

---

## Phase 3 — `/etc/binokel/env` befüllen

Wie Produktion, aber mit den **Staging-Werten**:

```env
DJANGO_SECRET_KEY=<zufällig, min. 50 Zeichen — nur für den Test>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=staging.binokel.example.com
DJANGO_DB_PATH=/opt/binokel/data/db.sqlite3
DJANGO_STATIC_ROOT=/opt/binokel/static
DJANGO_CSRF_TRUSTED_ORIGINS=https://staging.binokel.example.com
```

`sudo chown root:binokel-app /etc/binokel/env && sudo chmod 640 /etc/binokel/env`

---

## Tier A — Deploy lokal auf der VM (ohne GitHub-Secrets)

Der schnellste, risikoärmste Trockenlauf: die CD-Kommandos **von Hand** als
`binokel-deploy` ausführen. Das validiert Setup, App-Start, ACL-Schreibrechte und
Healthcheck, **ohne** GitHub-Secrets anzufassen.

```bash
# Auf der VM als binokel-deploy (oder via sudo -iu binokel-deploy):
cd /opt/binokel/app && git pull origin main
cd backend
uv sync --no-dev
# Produktionskonfiguration laden — sonst landen DB/Static in den Repo-Defaults
# statt in /opt/binokel/data bzw. /opt/binokel/static (siehe ENG-004):
set -a; . /etc/binokel/env; set +a
uv run python manage.py migrate --noinput        # ACL-Test: muss ohne "Permission denied" laufen
uv run python manage.py collectstatic --noinput  # ACL-Test: schreibt nach /opt/binokel/static
sudo systemctl restart binokel-tracker.service
```

### Verifikation (Tier A)

```bash
# 1. Lokaler Healthcheck (wie im CD-Workflow) — MUSS 200 liefern (kein Redirect-Loop!):
curl -s -o /dev/null -w '%{http_code}\n' http://localhost/health/     # erwartet: 200

# 2. HTTP→HTTPS-Redirect für normale Pfade greift:
curl -sI http://staging.binokel.example.com/ | grep -i '^location: https://'

# 3. HTTPS erreichbar — Staging-Cert ist untrusted, daher -k (erwartete Warnung):
curl -k -s -o /dev/null -w '%{http_code}\n' https://staging.binokel.example.com/health/

# 4. Security-Header gesetzt:
curl -k -sI https://staging.binokel.example.com/ | grep -iE 'strict-transport-security|x-content-type-options|x-frame-options'

# 5. Keine Fehler im App-Log:
tail -n 20 /var/log/binokel/error.log
journalctl -u binokel-tracker.service -n 30 --no-pager
```

**Grün, wenn:** `/health/` über HTTP **200** liefert (beweist: kein Redirect-Loop,
`SECURE_REDIRECT_EXEMPT` + `location = /health/` greifen), Redirect für `/` auf HTTPS
zeigt, HTTPS antwortet (Cert-Warnung erwartet), Security-Header vorhanden, Log sauber.

---

## Tier B (optional) — Volle CD-Pipeline über ein `staging`-Environment

Nur nötig, wenn auch der GitHub-Actions-Deploypfad selbst getestet werden soll.
**Wichtig:** Produktions-Secrets NICHT überschreiben — stattdessen ein separates
GitHub **Environment `staging`** mit eigenen Secrets anlegen.

1. GitHub → Settings → Environments → **`staging`** anlegen, Secrets dort setzen:
   `VM_SSH_KEY` (Deploy-Key der Wegwerf-VM), `VM_HOST` (Test-VM-IP),
   `VM_USER=binokel-deploy`, `VM_SSH_KNOWN_HOSTS` (`ssh-keyscan -H <Test-VM-IP>`).
2. Deploy-Key + `authorized_keys` auf der Wegwerf-VM wie Runbook Phase 4 einrichten.
3. Den CD-Workflow gegen das `staging`-Environment auslösen (dazu genügt für den Test
   ein temporärer Branch oder ein manuell angepasster `environment: staging`-Wert;
   **keine** Änderung am Produktions-`main` nötig).

> Der Healthcheck im CD-Workflow ruft `http://localhost/health/` auf der VM auf —
> unabhängig vom (untrusted) Staging-Zertifikat. Er muss **200** liefern.

---

## Teardown — nach dem Trockenlauf zwingend

- [ ] **Wegwerf-VM löschen** (IONOS-Panel). Damit verschwinden Test-Cert, Test-Key
      und alle Test-Daten restlos.
- [ ] **Test-DNS-Record** (`staging.binokel.example.com`) entfernen.
- [ ] Falls Tier B genutzt: **`staging`-Environment/Secrets** in GitHub entfernen und
      den Test-Deploy-Key verwerfen.
- [ ] Erkenntnisse (Fehler/Anpassungen) in `docs/engineering-notes/` festhalten und
      ggf. `setup-server.sh`/Runbook nachziehen.

---

## Übergang zum echten Deploy

Nach erfolgreichem Trockenlauf ändert sich für die Produktion nur:

| Aspekt | Trockenlauf | Produktion |
|---|---|---|
| VM | Wegwerf-VM (wird gelöscht) | dauerhafte Produktions-VM |
| Domain | `staging.binokel.example.com` | echte Domain |
| Certbot | `CERTBOT_STAGING=1` (Test-CA, untrusted) | **ohne** die Variable (Produktions-CA, gültig) |
| Secrets | GitHub-Environment `staging` | Produktions-Secrets |
| Daten | Wegwerf | echt (Backup-Cron aktiv) |

Der eigentliche Ablauf bleibt **identisch** zu `runbook-task-ci-006.md` — genau das
ist der Sinn des Trockenlaufs: denselben Pfad einmal ohne Risiko zu gehen.
