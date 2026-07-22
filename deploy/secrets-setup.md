# GitHub-Secrets für den CD-Deploy — lückenlose Anleitung

> **Zweck:** Eigenständige, schnell auffindbare Schritt-für-Schritt-Anleitung, um der
> CD-Pipeline ([`.github/workflows/cd.yml`](../.github/workflows/cd.yml)) einen sicheren,
> minimal berechtigten Zugang zur Produktions-VM zu geben. Dies ist die Detailfassung
> von **Runbook Phase 4** ([`runbook-task-ci-006.md`](runbook-task-ci-006.md)) — bei
> Abweichungen gilt diese Datei für die Secrets-Prozedur.

**Grundregel:** Secrets kommen **niemals** ins Repository. Nur als **GitHub-Secrets**
(dieser Guide) oder in `/etc/binokel/env` auf der VM (Laufzeit-Secret `DJANGO_SECRET_KEY`,
Runbook Phase 3).

---

## 0. Reale Werte dieses Deployments

| Größe | Wert |
|---|---|
| Domain | `api.bebe-soft.de` |
| VM-IP | `212.132.119.150` |
| Admin-User (interaktiv, sudo) | `binokel-admin` (Key `~/.ssh/binokel_admin`) |
| Deploy-User (CI/CD, kein sudo außer `systemctl restart/stop`) | `binokel-deploy` |
| Deploy-Key (in diesem Guide erzeugt) | `~/.ssh/binokel_deploy` (privat) / `.pub` (öffentlich) |
| VM-Host-Fingerprint (ED25519, nach Neuinstallation) | `SHA256:gmde+XfM1l1gG6kdIyrD2ZBWFgyEiQLlVacmoyZ3cVc` |

---

## 1. Die vier Secrets im Überblick

Die Pipeline liest genau diese vier Namen (exakt so schreiben). Klassifikation nach
**Vertraulichkeit**: nur der private Schlüssel ist ein **Secret**, der Rest ist
nicht-geheime Konfiguration und wird als **Variable** hinterlegt.

| Name | Typ | Bedeutung | Quelle des Werts |
|---|---|---|---|
| `VM_SSH_KEY` | **Secret** | **Privater** SSH-Schlüssel des Deploy-Users | Inhalt von `~/.ssh/binokel_deploy` (Schritt 3) |
| `VM_HOST` | **Variable** | Ziel für SSH/rsync | `api.bebe-soft.de` (oder `212.132.119.150`) |
| `VM_USER` | **Variable** | Login-User der Pipeline | `binokel-deploy` |
| `VM_SSH_KNOWN_HOSTS` | **Variable** | Verifizierte Host-Keys der VM (MITM-Schutz, **Pflicht**) | Ausgabe von `ssh-keyscan -H` (Schritt 4) |

> **Warum nur `VM_SSH_KEY` ein Secret ist:** Secret = vertraulich, Variable =
> nicht-vertrauliche Konfiguration. `VM_HOST`/`VM_USER` stehen ohnehin öffentlich im
> Repo. `VM_SSH_KNOWN_HOSTS` enthält **öffentliche** Host-Keys — sein Schutz kommt aus
> dem **Pinning** (nur Maintainer dürfen die Variable ändern), nicht aus Geheimhaltung.
> cd.yml liest `VM_SSH_KEY` über `secrets.…`, die drei anderen über `vars.…`.

> **Bewusst akzeptiert (Rubber-Duck-Review, NIEDRIG):** Variables werden in den
> Actions-Logs **unmaskiert** ausgegeben. Da dieses Repo **public** ist, erscheinen
> `VM_HOST` (`api.bebe-soft.de`) und `VM_USER` (`binokel-deploy`) im Klartext in
> öffentlichen Logs. Das ist akzeptiert: Die Domain ist per DNS ohnehin öffentlich und
> der Deploy-User steht bereits im Repo/Runbook — der Information-Disclosure-Zugewinn ist
> ~0. Der **private** Schlüssel bleibt als Secret maskiert.

> **Warum `VM_SSH_KNOWN_HOSTS` Pflicht ist:** Die Pipeline hat **keinen**
> `ssh-keyscan`-Laufzeit-Fallback (bewusst, ADR-009). Fehlt/stimmt der Wert nicht,
> **bricht der Deploy ab** — statt blind einem beliebigen Host zu vertrauen.

---

## 2. Voraussetzungen (vorher erledigt)

- [ ] VM läuft, `binokel-admin` per Key erreichbar (Runbook Phase 1)
- [ ] `setup-server.sh` gelaufen → `binokel-deploy` existiert (Runbook Phase 2)
- [ ] `/etc/binokel/env` befüllt (Runbook Phase 3)
- [ ] Admin-Login funktioniert: `ssh -i ~/.ssh/binokel_admin binokel-admin@212.132.119.150 'echo OK'`

---

## 3. Deploy-Keypair erzeugen (lokal, ohne Passphrase)

Die Pipeline läuft nicht-interaktiv → der Key darf **keine** Passphrase haben.

```bash
ssh-keygen -t ed25519 -a 100 -C "binokel-deploy@ci" -N "" -f ~/.ssh/binokel_deploy
```

Ergebnis: `~/.ssh/binokel_deploy` (privat, → `VM_SSH_KEY`) und
`~/.ssh/binokel_deploy.pub` (öffentlich, → auf die VM).

> **Getrennt vom Admin-Key:** Der Deploy-Key ist bewusst ein **anderer** Schlüssel als
> `~/.ssh/binokel_admin`. So kann der CI-Key rotiert/widerrufen werden, ohne den
> Admin-Zugang zu berühren.

---

## 4. Öffentlichen Deploy-Key auf der VM eintragen

Auf der VM (als `binokel-admin`) den **öffentlichen** Key in die `authorized_keys` des
Deploy-Users legen. Zuerst lokal den Public-Key anzeigen und kopieren:

```bash
# LOKAL:
cat ~/.ssh/binokel_deploy.pub
```

Dann auf der VM:

```bash
# Auf der VM (ssh -i ~/.ssh/binokel_admin binokel-admin@212.132.119.150):
sudo install -d -m 700 -o binokel-deploy -g binokel-deploy /home/binokel-deploy/.ssh
sudo -u binokel-deploy tee /home/binokel-deploy/.ssh/authorized_keys >/dev/null <<'PUBKEY'
<hier den kompletten Inhalt von binokel_deploy.pub einfügen>
PUBKEY
sudo chmod 600 /home/binokel-deploy/.ssh/authorized_keys
sudo chown binokel-deploy:binokel-deploy /home/binokel-deploy/.ssh/authorized_keys
```

> **Optionale Härtung** (Prefix vor dem Key in `authorized_keys`): `from="<IP-Range>"`
> schränkt Quell-IPs ein. GitHub-Actions-Ranges ändern sich jedoch — nur mit Pflege
> sinnvoll, daher für V1 nicht gesetzt.

---

## 5. Host-Keys für `known_hosts` einsammeln (MITM-Schutz)

```bash
# LOKAL — liefert die echten Host-Keys der VM:
ssh-keyscan -H api.bebe-soft.de
```

**Verifikation gegen den bekannten Fingerprint** (Schutz gegen einen bereits beim
Scan untergeschobenen falschen Host-Key):

```bash
ssh-keyscan api.bebe-soft.de 2>/dev/null | ssh-keygen -lf -
# Die ED25519-Zeile MUSS lauten:
#   SHA256:gmde+XfM1l1gG6kdIyrD2ZBWFgyEiQLlVacmoyZ3cVc
```

Die **komplette Ausgabe** von `ssh-keyscan -H api.bebe-soft.de` (alle Zeilen) wird
später der Wert von `VM_SSH_KNOWN_HOSTS`.

> Bei nicht-Standard-SSH-Port: `ssh-keyscan -H -p 2222 api.bebe-soft.de` und den Port
> konsistent in `VM_HOST`-Nutzung/SSH-Aufrufen berücksichtigen.

---

## 6. GitHub-Environment `production` anlegen (Pflicht)

Die Pipeline deklariert `environment: name: production` ([cd.yml](../.github/workflows/cd.yml)).
Environment-Secrets/-Variables sind gegenüber Repo-weiten **zu bevorzugen**, weil sie auf
Produktion **scoped** sind und **Schutzregeln** (Freigabe-Reviewer, Branch-Beschränkung)
erlauben.

> **Sicherheitshinweis (Rubber-Duck-Review, MITTEL):** Der CD-Trigger `workflow_run`
> läuft im Kontext des Default-Branch **mit Zugriff auf die Prod-Secrets**. Der einzige
> harte Riegel gegen einen ungewollten Prod-Deploy ist die Kombination aus **Required
> reviewers** und **Branch-Beschränkung auf `main`**. Beides ist daher **verpflichtend**
> (Abnahmekriterium), nicht optional.

**GitHub → Repository → Settings → Environments → New environment:**

1. Name: `production` → **Configure environment**
2. **Pflicht** (beide setzen):
   - **Required reviewers** → dich selbst (jeder Prod-Deploy muss manuell bestätigt werden)
   - **Deployment branches and tags** → *Selected branches* → nur `main`
3. Speichern.
4. **Verifizieren:** Nach dem ersten CD-Lauf erscheint in **Actions → Deploy → Review
   deployments** ein Freigabe-Dialog. Kommt kein Dialog, greift Required reviewers nicht →
   nachbessern, **bevor** produktiv scharfgeschaltet wird.

> **Zusätzlich (Fork-PR-Absicherung):** Unter **Settings → Actions → General → Fork pull
> request workflows** die Option **„Require approval for all external contributors"** (bzw.
> „…for first-time contributors") aktiv lassen. Nur in der GitHub-UI prüfbar, nicht im Repo
> sichtbar.

> Auf der Environment-Seite gibt es getrennte Abschnitte **Environment secrets** und
> **Environment variables**. Das eine Secret kommt in den Secrets-Abschnitt, die drei
> Variables in den Variables-Abschnitt.

---

## 7. Die Werte eintragen (1 Secret + 3 Variables)

**Settings → Environments → `production`** — dort:
- **Environment secrets → Add secret** für `VM_SSH_KEY`
- **Environment variables → Add variable** für `VM_HOST`, `VM_USER`, `VM_SSH_KNOWN_HOSTS`

### 7.1 `VM_SSH_KEY` (Secret — privater Key, sorgfältig kopieren)

Der **komplette** Inhalt inklusive `-----BEGIN OPENSSH PRIVATE KEY-----` und
`-----END OPENSSH PRIVATE KEY-----` und abschließendem Zeilenumbruch.

```bash
# LOKAL in die Zwischenablage (eine Variante wählen):
xclip -selection clipboard < ~/.ssh/binokel_deploy      # X11
wl-copy < ~/.ssh/binokel_deploy                          # Wayland
cat ~/.ssh/binokel_deploy                                # zur Kontrolle anzeigen
```

- Name: `VM_SSH_KEY`
- Value: eingefügter privater Key
- **Niemals** den `.pub`-Key hier eintragen; **niemals** den privaten Key committen/teilen.

### 7.2 `VM_HOST` (Variable)

- **Environment variables → Add variable**
- Name: `VM_HOST`
- Value: `api.bebe-soft.de`

### 7.3 `VM_USER` (Variable)

- **Environment variables → Add variable**
- Name: `VM_USER`
- Value: `binokel-deploy`

### 7.4 `VM_SSH_KNOWN_HOSTS` (Variable)

- **Environment variables → Add variable**
- Name: `VM_SSH_KNOWN_HOSTS`
- Value: die **komplette** Ausgabe von `ssh-keyscan -H api.bebe-soft.de` aus Schritt 5
  (alle Zeilen; führende `#`-Kommentarzeilen dürfen mit rein).

---

## 8. Verifikation

### 8.1 Deploy-Key funktioniert (lokal)

```bash
ssh -i ~/.ssh/binokel_deploy binokel-deploy@api.bebe-soft.de 'echo DEPLOY_LOGIN_OK'
```

### 8.2 Least-Privilege-Gegenprobe

```bash
# Erlaubte sudo-Kommandos — es dürfen NUR restart/stop erscheinen:
ssh -i ~/.ssh/binokel_deploy binokel-deploy@api.bebe-soft.de 'sudo -n -l'

# Darf KEIN beliebiges sudo (Secret-Datei bleibt unlesbar):
ssh -i ~/.ssh/binokel_deploy binokel-deploy@api.bebe-soft.de \
    'sudo -n cat /etc/binokel/env 2>/dev/null && echo "FEHLER: zu viele Rechte!" || echo "OK: eingeschränkt"'

# Status läuft unprivilegiert (kein sudo, siehe ENG-004 K1):
ssh -i ~/.ssh/binokel_deploy binokel-deploy@api.bebe-soft.de \
    'systemctl status binokel-tracker.service --no-pager >/dev/null && echo STATUS_OK'
```

### 8.3 GitHub-seitig

- Alle vier Secrets erscheinen unter `production` (Werte nicht mehr einsehbar — korrekt).
- Erst danach ist ein echter CD-Lauf sinnvoll (Runbook Phase 6, `workflow_dispatch`
  mit `confirm=yes`). Der Preflight-Step prüft `uv`, App-Verzeichnis, `/etc/binokel/env`
  und die systemd-Unit, bevor irgendetwas ausgeliefert wird.

---

## 8b. Key-Aufbewahrung & Recovery-Pfad

**Grundsatz:** Private SSH-Keys werden **nicht** klassisch gebackupt. Jede zusätzliche
Kopie vergrößert die Angriffsfläche. Statt Backup gilt **Rotierbarkeit**: ein verlorener
Key wird in Sekunden neu erzeugt und der öffentliche Teil ausgetauscht.

| Key | Aufbewahrung | Bei Verlust |
|---|---|---|
| `~/.ssh/binokel_admin` (Admin) | Nur lokal in `~/.ssh/`. **Kein** Extra-Backup. Zweiter Zugang via IONOS-Cloud-Panel / VNC-Konsole als Not-Aus. | Neuen Key erzeugen, `.pub` über die IONOS-VNC-Konsole in `~binokel-admin/.ssh/authorized_keys` eintragen. |
| `~/.ssh/binokel_deploy` (CI/CD) | Privater Teil liegt als `VM_SSH_KEY` in GitHub (nicht auslesbar). **Kein** Extra-Backup. | Rotieren (siehe §9): neues Paar, `authorized_keys` tauschen, `VM_SSH_KEY` überschreiben. |
| `.pub`-Dateien | Nicht geheim, liegen ohnehin in `authorized_keys` auf der VM. | Aus dem privaten Key rekonstruierbar: `ssh-keygen -y -f ~/.ssh/binokel_deploy`. |

**Recovery-Pfad bei komplettem Key-Verlust (Aussperr-Schutz):**

1. Über das **IONOS-Cloud-Panel → VNC-/Web-Konsole** an der VM anmelden (Login mit
   Benutzer + Passwort direkt an der virtuellen Konsole, unabhängig von SSH).
2. Auf dem lokalen Rechner neuen Admin-Key erzeugen:
   `ssh-keygen -t ed25519 -a 100 -C "binokel-admin@recovery" -f ~/.ssh/binokel_admin`
3. In der VNC-Konsole den neuen `.pub`-Inhalt eintragen:
   `install -d -m 700 ~/.ssh && nano ~/.ssh/authorized_keys` (alte Zeile ersetzen),
   `chmod 600 ~/.ssh/authorized_keys`.
4. SSH-Login mit dem neuen Key testen, danach ggf. Deploy-Key ebenfalls rotieren (§9).

> **Wichtig:** Sicherstellen, dass der VNC-Konsolen-Login (Passwort) im IONOS-Panel
> funktioniert, **bevor** er gebraucht wird — sonst ist der Not-Aus im Ernstfall zu.
> Das `DJANGO_SECRET_KEY` in `/etc/binokel/env` wird ebenfalls nicht gebackupt,
> sondern ist reproduzierbar (neu generieren invalidiert nur bestehende Sessions).

---

## 9. Rotation & Widerruf (jederzeit reversibel)

> **Rotations-Kadenz (Rubber-Duck-Review, NIEDRIG):** Den Deploy-Key **planmäßig alle
> 180 Tage** rotieren (nicht nur bei Verdacht). Reminder als wiederkehrendes GitHub-Issue
> oder Kalendereintrag anlegen. So bleibt die Prozedur geübt und ein unbemerkt
> abhandengekommener Key ist zeitlich begrenzt gültig.

- **Deploy-Key rotieren/kompromittiert:** neuen Key erzeugen (Schritt 3), alten Eintrag
  aus `/home/binokel-deploy/.ssh/authorized_keys` entfernen, neuen `.pub` eintragen,
  `VM_SSH_KEY` in GitHub überschreiben. Admin-Zugang bleibt unberührt.
- **Host-Key geändert** (z. B. VM-Neuinstallation): `ssh-keyscan` erneut ausführen,
  Fingerprint prüfen, `VM_SSH_KNOWN_HOSTS` überschreiben. Lokal ggf.
  `ssh-keygen -R api.bebe-soft.de` bzw. `-R 212.132.119.150`.
- **Secrets löschen:** in GitHub jederzeit möglich → Pipeline bricht dann kontrolliert ab.

---

## 10. Troubleshooting

| Symptom im CD-Log | Ursache | Behebung |
|---|---|---|
| `VM_SSH_KNOWN_HOSTS ist nicht gesetzt` + Abbruch | Variable fehlt | Schritt 5 + 7.4 |
| `Host key verification failed` | `VM_SSH_KNOWN_HOSTS` veraltet/falsch (VM neu installiert) | Schritt 5 wiederholen, Secret überschreiben |
| `Permission denied (publickey)` | `.pub` nicht/falsch in `authorized_keys` **oder** falscher `VM_USER` | Schritt 4 prüfen; `VM_USER` = `binokel-deploy` |
| Preflight `test -f /etc/binokel/env` schlägt fehl | Phase 3 nicht erledigt | `/etc/binokel/env` befüllen |
| `sudo -n -l` zeigt mehr als restart/stop | sudoers zu weit | `setup-server.sh`/sudoers prüfen (ENG-004 K1) |

---

## Sicherheitsprinzipien (Kurzfassung)

- **Least Privilege:** `binokel-deploy` hat kein allgemeines sudo, nur
  `systemctl restart/stop binokel-tracker.service`.
- **Kein TOFU:** `known_hosts` ist Pflicht, kein Laufzeit-`ssh-keyscan` (ADR-009).
- **Key-Trennung:** Deploy-Key ≠ Admin-Key ≠ Laufzeit-`SECRET_KEY`.
- **CD liest den echten `SECRET_KEY` nie** (nur nicht-geheime Pfad-Variablen; Wegwerf-Key
  für `migrate`/`collectstatic`, siehe ENG-004 E5).
</invoke>
