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

---

## Präventionsregel (übergreifend)

> Vor einem Erst-Deploy den gesamten Pfad **einmal gegen eine Wegwerf-VM** durchspielen
> (Certbot mit `--staging`, um Rate-Limits zu schonen). Statische Reviews finden
> Reihenfolge- und Rechte-Fallstricke zuverlässiger als jede Einzelbetrachtung.
