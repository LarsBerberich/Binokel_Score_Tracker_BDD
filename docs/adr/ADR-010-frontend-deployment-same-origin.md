# ADR-010 – Frontend-Deployment: Same-Origin auf einer Domain

## Status

Angenommen (23.07.2026)

## Kontext

Mit Phase 2 kommt eine Vue-Single-Page-Application (SPA) hinzu, die die bestehende
JSON-API konsumiert. Das Backend läuft bereits produktiv auf `api.bebe-soft.de`
(systemd-Gunicorn hinter Nginx, TLS via Let's Encrypt, siehe ADR-005, ADR-008).

Zu klären war, **wie SPA und API zueinander ausgeliefert werden**:

1. **Getrennte Origins:** SPA auf `binokel.bebe-soft.de`, API weiterhin auf
   `api.bebe-soft.de`. Cross-Origin-Requests → CORS-Konfiguration, Preflights,
   Cookie-`SameSite`-Sonderfälle.
2. **Same-Origin:** Eine Domain (`binokel.bebe-soft.de`) liefert die SPA-Dateien
   **und** proxied `/api/` an Django. Die alte API-Domain wird per 301 dorthin
   umgeleitet.
3. **Getrenntes Frontend-Hosting** (CDN/Static-Host, z. B. Netlify): eigener
   Build-/Deploy-Pfad, erneut Cross-Origin zur API.

## Entscheidung

**Same-Origin auf einer Domain** (`binokel.bebe-soft.de`), gleiche VM:

- Nginx serviert die gebaute SPA aus `/opt/binokel/frontend` (Vite-Output).
- `/api/` und `/health/` werden an denselben Gunicorn-Upstream proxied wie bisher.
- SPA-Fallback via `try_files $uri $uri/ /index.html` (History-Mode-Routing).
- Die bisherige API-Domain `api.bebe-soft.de` wird per **301** dauerhaft auf die
  Primärdomain umgeleitet und ins **SAN-Zertifikat** aufgenommen.
- `binokel-deploy` schreibt das SPA-Bundle; **nur** `www-data` (Nginx) erhält
  Lesezugriff darauf (`binokel-app` bewusst nicht — Least Privilege, siehe ADR-009).

## Begründung

| Kriterium | Same-Origin | Getrennte Origins | Externes Hosting |
|---|---|---|---|
| CORS/Preflights | entfällt | nötig | nötig |
| CSRF-/`SameSite`-Cookies | trivial | Sonderfälle | Sonderfälle |
| TLS-Zertifikate | 1 SAN-Cert | 2 Domains | extern + API |
| Betriebskomplexität | niedrig (bestehende VM) | mittel | zwei Systeme |
| Passt zu ADR-008 (eine VM, systemd) | ja | ja | nein |

Die Anwendung ist ein einzelnes, mobil-first genutztes MVP ohne dritte API-Clients.
Der einzige API-Konsument ist die eigene SPA. Same-Origin eliminiert eine ganze
Klasse von Konfigurations- und Sicherheitsfallstricken (CORS, Cookie-Attribute) ohne
Nachteile für den aktuellen Umfang.

## Konsequenzen

### Positiv
- Kein CORS, keine Preflights; CSRF/`SameSite`-Cookies funktionieren ohne Sonderfälle.
- Ein TLS-Zertifikat (SAN) deckt beide Domains ab.
- Die bestehende Deploy-/Betriebsinfrastruktur (systemd, Nginx, ACLs) bleibt tragend.
- Kanonische Herkunft: Bookmarks/Altlinks auf `api.bebe-soft.de` bleiben per 301 gültig.

### Negativ / Risiken
- SPA und API teilen sich Domain und TLS-Terminierung; keine unabhängige Skalierung.
- Der Redirect ändert bei POST-Anfragen an die Alt-Domain die Methode (301 → GET);
  akzeptabel, da keine externen Clients existieren (nur die Same-Origin-SPA).
- `api.bebe-soft.de` ist bereits eine eigene Certbot-Lineage — die Umstellung auf ein
  gemeinsames SAN-Zertifikat mit `binokel.bebe-soft.de` als Primär-Lineage erfordert
  einen einmaligen, dokumentierten Migrationsschritt auf der Live-VM (Runbook).

### Meilenstein für Überprüfung dieser Entscheidung
Sobald ein dritter, externer API-Client (z. B. native App über öffentliche API) oder
getrennte Skalierung von SPA und API nötig wird, ist eine getrennte-Origin-Architektur
mit expliziter CORS-Policy neu zu bewerten.

## Betroffene Artefakte
- `deploy/nginx.conf.template` — Same-Origin-Layout (SPA-Root, `/api/`-Proxy,
  SPA-Fallback, 301-Serverblock für die API-Domain).
- `deploy/setup-server.sh` — `/opt/binokel/frontend` + `www-data`-rX-ACL, optionale
  `API_DOMAIN` (SAN-Cert + Zwei-Domain-Substitution).
- `docs/engineering-notes/ENG-005-frontend-deployment-same-origin.md` — Fallstricke.

## Verweise
- ADR-005 (JsonResponse statt DRF), ADR-008 (VM-Deployment), ADR-009 (Hardening/ACLs),
  ADR-011 (Vue-Frontend-Stack).
