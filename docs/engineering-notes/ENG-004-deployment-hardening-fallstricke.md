# ENG-004: Deployment- und Hardening-Fallstricke (TASK-CI-006)

**Datum:** 2026-07-21
**Kontext:** Rubber-Duck-Review des Erst-Deploy-Runbooks; Behebung von 5 Blockern in
`settings.py`, `setup-server.sh`, `nginx.conf.template` und `cd.yml`.

---

## Überblick

Die Hardening-Baseline (ADR-009) war konzeptionell korrekt, der *ausführbare* Pfad
enthielt jedoch fünf klassische Deployment-Fallstricke. Alle fünf hätten den ersten
realen Deploy zum Scheitern gebracht — teils bereits im Setup-Skript, teils erst beim
Healthcheck. Diese Note hält Ursache und Lösung fest, damit sie sich nicht wiederholen.

---

## Fallstrick 1 — Redirect-Loop hinter Reverse Proxy

**Symptom:** Mit `DEBUG=False` wird *jede* Anfrage endlos auf `https://` umgeleitet,
die Seite ist unerreichbar, der Healthcheck erreicht nie HTTP 200.

**Ursache:** `SECURE_SSL_REDIRECT = True` ohne `SECURE_PROXY_SSL_HEADER`. Gunicorn
spricht per UNIX-Socket **HTTP** mit Nginx, daher ist `request.is_secure()` in Django
immer `False` — auch für bereits über HTTPS eingelieferte Requests.

**Lösung:** `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')` setzen.
Nginx setzt `X-Forwarded-Proto` im Proxy-Block bereits.

**Regel:** Hinter einem TLS-terminierenden Proxy gehören `SECURE_SSL_REDIRECT` und
`SECURE_PROXY_SSL_HEADER` **immer zusammen**.

---

## Fallstrick 2 — Nginx/Certbot Henne-Ei beim Erstlauf

**Symptom:** `nginx -t` schlägt im Setup-Skript fehl (`set -euo pipefail` bricht ab),
bevor überhaupt ein Zertifikat existiert.

**Ursache:** Das vollständige Nginx-Template referenziert
`ssl_certificate …/fullchain.pem`, `options-ssl-nginx.conf` und `ssl-dhparams.pem`.
Beim Erstlauf existiert davon nichts — Certbot läuft ja erst *danach*.

**Lösung:** Zweistufig ausrollen. Zuerst einen minimalen **HTTP-only-Serverblock**
(nur Port 80 + ACME-Challenge-Location), damit Nginx startet und Certbot die Challenge
beantworten kann. `certbot --nginx` erzeugt dabei zusätzlich `options-ssl-nginx.conf`
und `ssl-dhparams.pem`. Erst danach das vollständige Template (inkl. 443-Block)
ausrollen. Über die Existenz von `fullchain.pem` guarded → idempotent.

**Regel:** Eine Nginx-Config, die auf noch nicht ausgestellte TLS-Zertifikate zeigt,
darf beim Bootstrap nicht aktiv sein.

---

## Fallstrick 3 — Angenommener Installationspfad eines Tools (`uv`)

**Symptom:** `install -m 0755 "$HOME/.cargo/bin/uv" …` schlägt fehl, Skript bricht ab.

**Ursache:** Aktuelle `uv`-Versionen installieren nach `~/.local/bin/uv`, nicht mehr
`~/.cargo/bin/uv`. Als root ist `$HOME=/root`, der Pfad existiert nicht.

**Lösung:** Beide Kandidatenpfade prüfen und den gefundenen verlinken; fehlt das
Binary, mit klarer Fehlermeldung abbrechen.

**Regel:** Installationspfade externer Installer nie hart annehmen — nach der
Installation das Binary suchen (`command -v` / Kandidatenliste), dann verwenden.

---

## Fallstrick 4 — Zwei Benutzer, ein Verzeichnisbaum (Schreibrechte)

**Symptom:** `migrate`/`collectstatic` scheitern mit *Permission denied*; oder der
Dienst kann die SQLite-DB zur Laufzeit nicht schreiben.

**Ursache:** `data`/`static` gehörten `binokel-app`, der CD-Workflow läuft die
Kommandos aber als `binokel-deploy`. Reines `chgrp`+`setgid` reicht nicht: Neue
Dateien erhalten wegen `umask 022` kein Gruppen-Schreibrecht, sodass anschließend der
jeweils andere Benutzer nicht mehr schreiben kann. SQLite braucht Schreibrecht auf
**Datei und Verzeichnis**.

**Lösung:** POSIX-ACLs inklusive **Default-ACLs**:

```bash
setfacl -R -m u:binokel-app:rwX -m u:binokel-deploy:rwX  "$DATA_DIR" "$STATIC_DIR"
setfacl -R -d -m u:binokel-app:rwX -m u:binokel-deploy:rwX "$DATA_DIR" "$STATIC_DIR"
```

Die `-d`-Einträge vererben `rwX` an *neu erzeugte* Dateien/Verzeichnisse — umask-
unabhängig. Erfordert das `acl`-Paket.

**Regel:** Sollen sich zwei Nicht-root-Benutzer denselben Baum schreibend teilen und
neue Dateien beliebiger `umask` erzeugen, sind Default-ACLs die robuste Lösung —
nicht `setgid` allein.

---

## Fallstrick 5 — Healthcheck läuft gegen die HTTPS-Erzwingung

**Symptom:** `curl http://localhost/health/` liefert 301 (Redirect) oder 400
(`DisallowedHost`) statt 200.

**Ursache:** Der Port-80-Block leitete auch `/health/` per `return 301` auf HTTPS um;
zusätzlich fehlte `localhost` in `ALLOWED_HOSTS`, und Djangos SSL-Redirect hätte den
Request ohnehin umgeleitet.

**Lösung (drei zusammenspielende Teile):**
1. Nginx: `location = /health/` im Port-80-Block proxyt direkt (kein Redirect).
2. Django: `SECURE_REDIRECT_EXEMPT = [r'^health/$']` nimmt den Pfad vom SSL-Redirect aus.
3. Django: `localhost`/`127.0.0.1` immer in `ALLOWED_HOSTS`, da der Check lokal aufruft.

**Regel:** Ein lokaler HTTP-Healthcheck und eine globale HTTPS-Erzwingung müssen
explizit aufeinander abgestimmt werden — sonst blockiert die Härtung den Check.

---

## Nebenpunkt — sudoers-Pfad `/usr/bin/systemctl`

Auf Ubuntu 24.04 (usrmerge) ist der kanonische Pfad `/usr/bin/systemctl`; sudo löst
ihn über `secure_path` auf und vergleicht literal. Die sudoers-Regel muss daher
`/usr/bin/systemctl` (nicht `/bin/systemctl`) nennen, sonst wird
`sudo systemctl restart` abgewiesen.

---

## Nebenpunkt — `gunicorn` fehlte in den Projekt-Dependencies

**Symptom (bei Vorbereitung des Trockenlaufs entdeckt):** Der systemd-Dienst startet
`/opt/binokel/app/backend/.venv/bin/gunicorn`, aber `gunicorn` stand nicht in den
`dependencies` von `backend/pyproject.toml`. `uv sync --no-dev` hätte die Binary daher
nie installiert → der Dienst wäre beim ersten Start mit *„No such file"* gescheitert.

**Ursache:** Gunicorn war zwar in `binokel-tracker.service`, ADR-008 und der
Doku als Laufzeit referenziert, aber nie als tatsächliche Abhängigkeit deklariert.

**Lösung:** `gunicorn>=23.0.0` zu `dependencies` hinzugefügt und `uv.lock`
aktualisiert (`gunicorn 26.0.0`). Verifiziert: `.venv/bin/gunicorn` vorhanden,
28 Behave + 19 Django weiterhin GREEN.

**Regel:** Jede in `*.service`/Deploy referenzierte Laufzeit-Binary muss als echte
Projekt-Dependency deklariert und in der Lockfile fixiert sein — Doku-Erwähnung
allein installiert nichts.

---

## Nebenpunkt — Deploy lief ohne Produktionskonfiguration

**Symptom (bei Vorbereitung des Trockenlaufs entdeckt):** Der Deploy „läuft grün
durch", die App ist danach aber kaputt — Laufzeitfehler *„no such table"* und leere
Static-Auslieferung.

**Ursache:** `migrate`/`collectstatic` liefen als `binokel-deploy` **ohne**
`/etc/binokel/env` zu laden. In `settings.py` fielen `DJANGO_DB_PATH` und
`DJANGO_STATIC_ROOT` daher auf die Repo-Defaults (`backend/db.sqlite3`,
`backend/staticfiles`) zurück — der systemd-Dienst nutzt aber
`/opt/binokel/data/db.sqlite3` und `/opt/binokel/static`. Migrationen und Static
landeten also am falschen Ort; der Dienst startete gegen eine leere DB.

**Lösung:** Deploy-Schritte (`cd.yml`, manueller Not-Deploy, Tier-A-Trockenlauf) laden
die Env vor den Kommandos (`set -a; . /etc/binokel/env; set +a`). Damit
`binokel-deploy` die Datei lesen kann, vergibt `setup-server.sh` gezielten
ACL-Lesezugriff (`setfacl -m u:binokel-deploy:r /etc/binokel/env`). Least Privilege
bleibt gewahrt (der Deploy-User kontrolliert ohnehin Code und Dienst — siehe
ADR-009-Nachtrag).

**Nachtrag (im Trockenlauf aufgetreten):** Die Datei-ACL allein genügt nicht — das
**Verzeichnis** `/etc/binokel` gehört `root:root` (750) und gab Nicht-root-Usern kein
Such-/Traversal-Recht. `. /etc/binokel/env` als `binokel-deploy` scheiterte daher mit
*Permission denied*, obwohl die Datei-ACL Lesen erlaubte (der systemd-Dienst war nicht
betroffen, da er die Datei als root liest). Zusätzlich nötig:
`setfacl -m u:binokel-app:x -m u:binokel-deploy:x /etc/binokel` (nur `x`, kein Lesen
des Verzeichnisinhalts).

**Regel:** Offline-Management-Kommandos (`migrate`, `collectstatic`) müssen mit
**derselben** Konfiguration laufen wie der Dienst — sonst divergieren DB-/Static-Pfade
lautlos. Und: Datei-ACLs greifen nur, wenn **jedes Elternverzeichnis** das
Such-Recht (`x`) für den Zugreifenden gewährt.

---

## Nebenpunkt — Dienst-User darf die `gunicorn`-Binary nicht ausführen (203/EXEC)

**Symptom (im Trockenlauf aufgetreten):** Der systemd-Dienst startet nicht,
`systemctl status` zeigt `status=203/EXEC`, das Journal:
`Failed to execute …/.venv/bin/gunicorn: Permission denied`. Der Healthcheck liefert
`502` (Nginx läuft, App-Socket fehlt). Kein `error.log`, da Gunicorn nie startet.

**Ursache:** Der Dienst läuft als `binokel-app`, das `.venv` (inkl. `gunicorn`) wird
aber vom Deploy-User `binokel-deploy` unter `APP_DIR` erzeugt. Je nach `umask` des
Deploy-Users sind die neuen Dateien für „other" nicht les-/ausführbar, sodass
`binokel-app` die Binary nicht starten kann.

**Lösung:** `binokel-app` per ACL Lese-/Ausführungsrecht auf den App-Baum geben,
inklusive **Default-ACL**, damit von `git clone`/`uv sync` neu erzeugte Dateien es
erben — umask-unabhängig:

```bash
setfacl -R -m u:binokel-app:rX /opt/binokel/app
setfacl -R -d -m u:binokel-app:rX /opt/binokel/app
```

`rX` (großes X) vergibt das x-Bit nur auf Verzeichnissen und ohnehin ausführbaren
Dateien — der Dienst-User bekommt Traversal + Ausführung, ohne Schreibrecht (Least
Privilege; er schreibt zur Laufzeit nur in `data`/`static`).

**Regel:** Wenn ein Dienst-User Code/venv eines *anderen* Erzeuger-Users ausführt,
muss sein Lese-/Ausführungsrecht per Default-ACL abgesichert sein — sonst entscheidet
die zufällige `umask` des Deploy-Users über den Dienststart.

**Nachtrag — der eigentliche Übeltäter: uv-Interpreter im Deploy-Home:** Die App-Baum-ACL
allein behob den `203/EXEC` **nicht**. `namei -l` auf die gunicorn-Binary zeigte, dass alle
Pfad-Komponenten und die Binary selbst world-executable waren — trotzdem `EACCES` beim
`execve`. Grund: gunicorn ist ein Skript mit Shebang
`#!/opt/binokel/app/backend/.venv/bin/python`, und dieser venv-Python ist nur ein **Symlink**
auf den von uv verwalteten Interpreter unter
`/home/binokel-deploy/.local/share/uv/python/cpython-3.14.../bin/python3.14`. Das
Deploy-Home ist `0750` (`drwxr-x---`); `binokel-app` ist nicht in dessen Gruppe und „other"
hat kein Traversal-Recht → der Interpreter ist unerreichbar → der Kernel scheitert beim
`execve` des Skripts mit *Permission denied*. Diagnose-Kommando:
`namei -l "$(readlink -f .venv/bin/python)"` — es deckt das `drwxr-x---`-Home sofort auf.

**Lösung:** uv anweisen, den verwalteten Interpreter in ein **geteiltes**, world-traversierbares
Verzeichnis unter `/opt` zu legen, statt ins Deploy-Home. In `/etc/binokel/env`:

```bash
UV_PYTHON_INSTALL_DIR=/opt/binokel/python
```

Der CD-Deploy und der manuelle Deploy sourcen die env-Datei vor `uv sync`, sodass
Interpreter-Installation **und** venv-Symlink dorthin zeigen. `setup-server.sh` legt
`/opt/binokel/python` an und vergibt `setfacl -R (-d) -m u:binokel-app:rX` (Default-ACL,
damit der von uv als binokel-deploy entpackte Interpreter-Baum das Recht erbt). **Wichtig
bei bestehenden VMs:** Ein bereits erzeugtes `.venv` behält seinen alten Interpreter-Symlink;
`uv sync` repointet ihn nicht. Einmalig `.venv` löschen und neu synchen:
`rm -rf .venv && uv sync --no-dev` (mit gesourcter env). Bei einem frischen Produktions-Deploy
existiert noch kein `.venv`, sodass der Symlink von Anfang an korrekt zeigt.

**Regel:** venv-Interpreter sind Symlinks auf einen **externen** Basis-Python. Wenn ein
anderer User als der venv-Erzeuger den venv ausführt, muss dieser externe Interpreter in
einem für ihn erreichbaren Pfad liegen — Home-Verzeichnisse (`0750`) sind es nicht.
Werkzeug-verwaltete Interpreter (uv, pyenv, asdf) gehören bei Multi-User-Deployment in ein
geteiltes Verzeichnis (`UV_PYTHON_INSTALL_DIR` o. Ä.).

---

## Nebenpunkt — Gunicorn-Control-Server scheitert am fehlenden Home (Errno 13)

**Symptom (im Trockenlauf aufgetreten):** Der Dienst läuft und liefert über HTTP-localhost
`200`, aber `error.log` enthält bei jedem Start:
`[ERROR] Control server error: [Errno 13] Permission denied: '/home/binokel-app'`.

**Ursache:** Gunicorn ≥26 startet einen internen „Control Server" und legt dafür einen
Socket unter `$HOME` an. Der Dienst-User `binokel-app` ist ein System-User **ohne** Home
(`useradd --no-create-home`); `$HOME` zeigt auf das nicht existierende `/home/binokel-app`,
das Anlegen scheitert mit `EACCES`. Die Worker laufen zwar trotzdem, aber der Fehler
wiederholt sich bei jedem (Re)Start und verrauscht das Log.

**Lösung:** In der systemd-Unit `HOME` auf ein beschreibbares Verzeichnis setzen — das
ohnehin vorhandene `RuntimeDirectory` (`/run/binokel`, gehört `binokel-app`) bietet sich an:

```ini
Environment="HOME=/run/binokel"
```

**Regel:** System-User ohne Home (`--no-create-home`) brauchen für Prozesse, die in `$HOME`
schreiben (Gunicorn-Control-Server, Caches, `.config`), ein explizit gesetztes, beschreibbares
`HOME` in der systemd-Unit.

---

## Nebenpunkt — HTTPS liefert 400, obwohl HTTP-localhost 200 liefert (DisallowedHost)

**Symptom (im Trockenlauf aufgetreten):** `curl http://localhost/health/` → `200`, aber
`curl -k https://<domain>/health/` → `400`.

**Ursache:** Über localhost trägt der Request `Host: localhost` (in `settings.py` immer in
`ALLOWED_HOSTS`), über die Domain aber `Host: <domain>`. Steht die reale Domain nicht in
`DJANGO_ALLOWED_HOSTS` (`/etc/binokel/env`, Platzhalter `REPLACE_WITH_YOUR_DOMAIN` nicht
ersetzt), antwortet Django mit `400 Bad Request` (`DisallowedHost`). Der HTTP-localhost-Health
verdeckt das, weil localhost immer erlaubt ist.

**Lösung:** `DJANGO_ALLOWED_HOSTS` (und `DJANGO_CSRF_TRUSTED_ORIGINS`) in `/etc/binokel/env`
auf die echte Domain setzen, Dienst neu starten.

**Regel:** Den Healthcheck immer **auch** über den echten Host-Namen (nicht nur localhost)
prüfen — sonst bleibt ein leeres/falsches `ALLOWED_HOSTS` bis zum ersten echten Browser-Zugriff
unbemerkt.

**Nachtrag — die eigentliche 400-Ursache: fehlender `proxy_set_header Host` im 443-Block:**
`ALLOWED_HOSTS` enthielt die Domain korrekt, HTTPS-Health blieb dennoch `400`. Ursache war
nicht Django, sondern **Nginx**: der `location /health/`-Block im 443-Server rief `proxy_pass`
**ohne** `proxy_set_header Host` auf. Nginx setzt dann den Default `Host: $proxy_host` — und das
ist der **Upstream-Block-Name** (`binokel_app`), nicht die Domain. Django empfing also
`Host: binokel_app` → nicht in `ALLOWED_HOSTS` → `DisallowedHost` → `400`. Der Port-80-Health-Block
setzte `Host $host` bereits korrekt, weshalb HTTP-localhost `200` lieferte und den Fehler verdeckte.
Fix: im 443-Health-Block `proxy_set_header Host $host;` (+ `X-Forwarded-Proto $scheme;`) ergänzen.

**Regel:** Jeder `proxy_pass`-Block, der eine `upstream {}`-Gruppe anspricht, muss den
`Host`-Header explizit setzen (`proxy_set_header Host $host;`) — sonst leakt der Upstream-Name als
Host-Header und Djangos `ALLOWED_HOSTS`-Prüfung schlägt fehl.

---

## Fallstrick — sudo-Regel für `systemctl status` = Root-Escape via Pager (K1)

**Symptom (im Security-Review gefunden):** Kein Laufzeitfehler — eine latente
Privilege-Escalation. Die sudoers-Regel
`binokel-deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl status binokel-tracker.service`
erlaubt scheinbar harmlose Statusabfragen.

**Ursache:** `systemctl status` leitet lange Ausgaben per Default durch einen Pager
(`less`). `binokel-deploy` hat SSH-Login + `/bin/bash`; ruft er die Regel interaktiv über
eine TTY auf, öffnet sich der Pager — und aus `less` heraus startet `!sh` eine **Shell als
root**. Ein kompromittierter Deploy-SSH-Key eskaliert damit von Non-root zu **vollem Root**
und hebelt die gesamte Nutzertrennung aus.

**Lösung:** Die `status`-Regel aus `/etc/sudoers.d/binokel-deploy` **streichen**. NOPASSWD nur
für `restart`/`stop`. Statusdiagnose läuft unprivilegiert: `systemctl status --no-pager`,
`journalctl`, und das world-lesbare `/var/log/binokel/error.log`. Der CD-Failure-Pfad
([.github/workflows/cd.yml](../../.github/workflows/cd.yml)) nutzt entsprechend `systemctl
status --no-pager` (kein sudo) + `tail` des Logs.

**Regel:** NOPASSWD-sudo-Regeln nur für Kommandos vergeben, die **keinen** Pager/Editor/keine
Shell-Escape-Möglichkeit haben. `systemctl status`, `less`, `more`, `man`, `vi`, `git`
(via `!`, `PAGER`, `-o core.pager`) sind klassische Pager-/Shell-Escape-Vektoren. Im Zweifel
`--no-pager`/`SYSTEMD_PAGER=cat` erzwingen oder das Kommando ganz aus sudoers weglassen.

---

## Fallstrick — fail-open SECRET_KEY/DEBUG (K2)

**Symptom (im Security-Review gefunden):** Fehlt in Production `DJANGO_SECRET_KEY` (env nicht
gesourct, Tippfehler, leere Variable), läuft Django **still** mit dem öffentlich im Repo
stehenden Insecure-Default-Key weiter — Session-/CSRF-/Signing-Tokens sind kompromittierbar.
Analog aktiviert ein fehlendes `DJANGO_DEBUG` bei falschem Default `DEBUG=True` (Stacktrace-/
Settings-Leak).

**Ursache:** `os.environ.get('DJANGO_SECRET_KEY', '<insecure-default>')` ist **fail-open** —
der unsichere Fallback greift lautlos.

**Lösung:** Bei `DEBUG=False` **hart abbrechen**, wenn der Key dem Insecure-Default entspricht:
```python
if not DEBUG and SECRET_KEY == _INSECURE_SECRET_KEY:
    raise ImproperlyConfigured('DJANGO_SECRET_KEY … in Production setzen')
```
Der `DEBUG`-Default bleibt `'True'` (dev/test-freundlich); Production erzwingt `DJANGO_DEBUG=False`
über das env-Template, wodurch der Riegel scharf wird.

**Regel:** Sicherheitskritische Defaults müssen **fail-safe** sein. Ein fehlender Secret darf in
Production nicht durch einen im Repo sichtbaren Platzhalter ersetzt werden — lieber laut abbrechen
als still unsicher laufen.

---

## Weitere Review-Nachschärfungen (E1–E5)

Nicht-blockierend, aber umgesetzt (Details in [ADR-009](../adr/ADR-009-internet-hardening-baseline.md),
Nachtrag „Security-Review-Nachschärfungen"):
- **E1** `binokel-app` nur `rX` auf `STATIC_DIR` (Eigentümer `binokel-deploy`) — der exponierte
  Dienst kann nicht ins ausgelieferte Static-Verzeichnis schreiben (Phishing-/JS-Injection-Schutz).
- **E2** Security-Header-Ownership: Django für proxied Antworten, Nginx exklusiv im `/static/`-Block;
  Referrer-Policy angeglichen (vorher zwei widersprüchliche Werte). Wichtig: Nginx vererbt
  `add_header` **nicht** in `location`-Blöcke mit eigenem `add_header` — Header dort wiederholen.
- **E3** systemd-Härtung: `ProtectSystem=strict` + `ReadWritePaths`, `ProtectHome`, `PrivateDevices`,
  `SystemCallFilter=@system-service`, `RestrictAddressFamilies` u. a.
- **E4** `server_tokens off;`.
- **E5** CD liest den echten `SECRET_KEY` nicht mehr — migrate/collectstatic laufen mit einem
  Wegwerf-Schlüssel (schlüssel-unabhängig); nur nicht-geheime Pfad-Variablen werden aus der env gelesen.

---

## Fallstrick: cloud-init übersteuert das sshd-Hardening (Erst-Deploy 22.07.2026)

**Symptom:** Nach dem Ausrollen des Hardening-Drop-ins `99-binokel-hardening.conf`
(`PasswordAuthentication no`) und `systemctl reload ssh` zeigte
`sshd -T | grep passwordauthentication` weiterhin **`passwordauthentication yes`** —
Passwort-Login blieb also offen, obwohl die Datei korrekt geschrieben war.

**Ursache:** Ubuntu-Cloud-Images legen unter `/etc/ssh/sshd_config.d/` eigene
Drop-ins an, u. a. `50-cloud-init.conf` mit `PasswordAuthentication yes`. sshd liest
die Drop-ins über `Include …/*.conf` in **lexikografischer** Reihenfolge und nimmt für
jedes Keyword den **ersten** gefundenen Wert (man `sshd_config`: „the first obtained
value will be used"). `50-cloud-init.conf` wird also **vor** `99-binokel-hardening.conf`
gelesen und gewinnt. `PermitRootLogin no` griff nur deshalb, weil cloud-init dieses
Keyword nicht setzt.

**Lösung:** Das Hardening-Drop-in so benennen, dass es **zuerst** gelesen wird:
`00-binokel-hardening.conf`. Damit gewinnen die sicherheitskritischen Werte
unabhängig von cloud-init-/Cloud-Image-Dateien (`50-cloud-init.conf`,
`60-cloudimg-settings.conf`).

**Verifikation (Pflicht):** Nach `reload` **nicht** nur die Datei prüfen, sondern die
**effektive** Konfiguration:
```bash
sudo sshd -T | grep -Ei 'permitrootlogin|passwordauthentication|kbdinteractive'
```
Zusätzlich lockout-sicher gegenprüfen (zweites Terminal): Key-Login muss gehen,
`-o PreferredAuthentications=password -o PubkeyAuthentication=no` muss
`Permission denied (publickey)` liefern.

**Regel:** Bei Drop-in-Konfigurationsverzeichnissen mit First-Match-Semantik
(`sshd_config.d`, ähnlich `sysctl.d`) zählt die **Lese-Reihenfolge**, nicht die
Absicht. Sicherheits-Overrides mit niedrigem Präfix (`00-`) nach vorne ziehen und
immer den **effektiven** Zustand verifizieren, nie nur die geschriebene Datei.

---

## Präventionsregel (übergreifend)

> Vor einem Erst-Deploy den gesamten Pfad **einmal gegen eine Wegwerf-VM** durchspielen
> (Certbot mit `--staging`, um Rate-Limits zu schonen). Statische Reviews finden
> Reihenfolge- und Rechte-Fallstricke zuverlässiger als jede Einzelbetrachtung.
