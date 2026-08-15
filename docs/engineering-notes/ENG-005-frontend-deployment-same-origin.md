# ENG-005: Frontend-Deployment (Same-Origin) — Fallstricke (Phase 2, B1–B3)

**Datum:** 2026-07-23
**Kontext:** Phase-0-Infrastruktur für die Vue-SPA (ADR-010, ADR-011). Umbau von
`deploy/nginx.conf.template` und `deploy/setup-server.sh` von reinem Backend-Betrieb
auf Same-Origin-Auslieferung von SPA + API auf einer Domain.

---

## Überblick

Die bestehende Nginx-/Setup-Konfiguration war **Backend-only**: eine Domain, `/`
proxied direkt an Django. Für die SPA-Ära (eine Domain serviert statische SPA-Dateien
**und** proxied `/api/`) waren drei Infrastruktur-Blocker (B1–B3) zu beheben. Diese
Note hält die dabei relevanten Fallstricke fest.

---

## Fallstrick 1 (B1) — SPA-History-Routing braucht `try_files`-Fallback

**Symptom:** Der direkte Aufruf oder Reload einer Client-Route (z. B.
`/spiele/42`) liefert HTTP 404, obwohl die Route in der SPA existiert.

**Ursache:** Ohne Fallback sucht Nginx eine echte Datei/ein Verzeichnis für den Pfad.
Bei History-Mode-Routing gibt es die nicht — nur `index.html` kennt die Route.

**Lösung:** `location / { try_files $uri $uri/ /index.html; }`. Unbekannte Pfade
liefern die SPA-Shell; das Client-Routing übernimmt danach.

**Regel:** SPA-Shell (`index.html`) mit `Cache-Control: no-cache` ausliefern, die
content-gehashten `/assets/` dagegen `immutable` langlebig cachen. Sonst sehen Clients
nach einem Deploy eine veraltete `index.html`, die auf nicht mehr existierende
Asset-Hashes zeigt.

---

## Fallstrick 2 (B2) — Zweite Domain braucht denselben SAN-Cert-Pfad

**Symptom:** Der zweite Server-Block (Redirect der alten API-Domain) referenziert einen
eigenen `live/<api-domain>/`-Zertifikatspfad, den es nicht gibt → `nginx -t` scheitert.

**Ursache:** Ein SAN-Zertifikat für mehrere Domains wird von Certbot unter **einer**
Lineage abgelegt — der des **ersten** `-d`-Arguments. Beide Server-Blöcke müssen daher
denselben `live/<primärdomain>/`-Pfad nutzen.

**Lösung:** `certbot --nginx -d PRIMÄRDOMAIN -d API_DOMAIN`; beide Server-Blöcke
verweisen auf `live/PRIMÄRDOMAIN/`. Der HTTP-Bootstrap-Block deckt im `server_name`
**beide** Domains ab, damit die ACME-Challenge für beide beantwortet wird.

**Regel:** Bei SAN-Zertifikaten ist die Cert-Lineage die des ersten `-d`; nie einen
separaten Pfad pro SAN-Host annehmen.

**Live-VM-Besonderheit:** `api.bebe-soft.de` ist bereits eine eigenständige
Certbot-Lineage. Die Umstellung auf ein gemeinsames SAN-Zertifikat mit der neuen
Primärdomain erfordert einen einmaligen, dokumentierten Migrationsschritt (Cert
expandieren/neu ausstellen) — nicht einfach `setup-server.sh` erneut ausführen.

---

## Fallstrick 3 (B3) — Nginx (`www-data`) braucht Leserechte auf das SPA-Verzeichnis

**Symptom:** Nach dem Deploy liefert Nginx HTTP 403 für die SPA, obwohl die Dateien in
`/opt/binokel/frontend` liegen.

**Ursache:** `binokel-deploy` schreibt das Bundle (Eigentümer); je nach umask hat
`www-data` (der Nginx-Worker) keinen Lesezugriff auf die neu erzeugten Dateien.

**Lösung:** `setfacl -R -m u:www-data:rX` **plus Default-ACL** (`-d`) auf
`/opt/binokel/frontend`, damit von rsync neu erzeugte Dateien das Recht erben —
umask-unabhängig (vgl. ENG-004, ACL-Fallstrick für den Dienst-User).

**Least Privilege:** Der internet-exponierte App-Dienst `binokel-app` erhält
**keinen** Zugriff auf das Frontend-Verzeichnis (Nginx liefert die SPA aus, nicht
Gunicorn) — analog zur `/static/`-Trennung aus ADR-009 (E1).

---

## Fallstrick 4 — Platzhalter-Rest im Ein-Domain-Modus

**Symptom:** Wird `setup-server.sh` ohne `API_DOMAIN` aufgerufen, bleibt im
Port-80-`server_name` das Literal `REPLACE_WITH_API_DOMAIN` als „Hostname" stehen.

**Ursache:** Das Template trägt beide Platzhalter; das Entfernen nur des
Redirect-Serverblocks (Sentinel-Marker `# >>> API_REDIRECT_BLOCK` … `# <<<`) tilgt den
Rest-Platzhalter im gemeinsamen Port-80-Block nicht.

**Lösung:** Im Ein-Domain-Zweig zusätzlich `sed 's/ REPLACE_WITH_API_DOMAIN//g;
s/REPLACE_WITH_API_DOMAIN//g'` anwenden. Verifiziert: `bash -n` OK, 0 Rest-Platzhalter
in beiden Modi.

---

## Offene Betriebspunkte (für den Live-Cut-Over)

- **Smoke-Test (`cd.yml`):** prüft aktuell `api.bebe-soft.de`. Nach dem Cut-Over ist der
  Redirect (301 auf die Primärdomain) zu berücksichtigen bzw. der Smoke-Test auf die
  Primärdomain umzustellen. `/health/` bleibt bewusst auch auf der API-Domain bedienbar.
- **`DJANGO_ALLOWED_HOSTS` / `DJANGO_CSRF_TRUSTED_ORIGINS`:** beide Domains eintragen
  (der `/health/`-Proxy der API-Domain erreicht Django mit deren Host-Header).
