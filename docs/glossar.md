# Glossar – Abkürzungen und Fachbegriffe

> Nachschlagewerk für die im Repository verwendeten Abkürzungen und technischen Begriffe.
> Für die **fachliche** Binokel-Sprache (Spielmacher, Reizwert, Abgehen, …) siehe
> `docs/ubiquitous-language.md`; für Schreibkonventionen `docs/language-conventions.md`.
>
> Ergänzen: Taucht in einer neuen Änderung eine bisher unerklärte Abkürzung auf, hier
> eintragen (vgl. PFLICHT-KONVENTION, `docs/project-foundation.md` §18).

---

## Projekt-interne Kennungen (Dokumenttypen & Codes)

| Kürzel | Bedeutung | Erläuterung |
|---|---|---|
| **ADR** | Architecture Decision Record | Dokumentierte Architekturentscheidung, `docs/adr/ADR-NNN-*.md`. Hält Kontext, Entscheidung, Begründung und Konsequenzen fest. |
| **ENG** | Engineering Note | Festgehaltener Umsetzungs-/Betriebs-Fallstrick, `docs/engineering-notes/ENG-NNN-*.md`. |
| **TASK** | Aufgabe im Backlog | Arbeitspaket in `BACKLOG.md` (z. B. TASK-007). `TASK-CI-NNN` = CI/CD-/Betriebsaufgabe. |
| **FUTURE** | Zurückgestellte Aufgabe | V2+-Idee im Backlog, noch nicht priorisiert (z. B. FUTURE-002). |
| **RD** | Rubber-Duck (Review) | Befund/Punkt aus einem Rubber-Duck-Review (z. B. RD-6, RD-8). |
| **K1/K2, E1–E5** | Review-Klassen | Aus dem Security-Review: **K** = blockierend (kritisch), **E** = empfohlene Verschärfung. |
| **B1–B3** | Infra-Blocker | Die drei Phase-0-Frontend-Infrastruktur-Blocker (nginx-SPA-Fallback, SAN-Serverblock, Frontend-ACL). |
| **§** | Paragraf/Abschnitt | Verweis auf einen nummerierten Abschnitt, meist in `docs/project-foundation.md`. |

## BDD, Tests & Entwicklungsprozess

| Kürzel | Bedeutung | Erläuterung |
|---|---|---|
| **BDD** | Behavior-Driven Development | Verhaltensgetriebene Entwicklung; Verhalten zuerst als Gherkin-Szenarien. |
| **Gherkin** | — | Given/When/Then-Sprache (dt. Angenommen/Wenn/Dann) für Feature-Dateien. |
| **behave** | — | Python-BDD-Runner, führt die `features/*.feature` gegen Step-Definitionen aus. |
| **E2E** | End-to-End (-Test) | Test durch die gesamte Anwendung (Browser → SPA → API), hier via Playwright + playwright-bdd. |
| **Outside-In** | — | Entwicklungsrichtung von der äußeren Schnittstelle nach innen (Akzeptanztest zuerst). |
| **RED-Green-Refactor** | — | TDD/BDD-Zyklus: erst fehlschlagender Test (rot), dann grün, dann aufräumen. |
| **Slice** | Vertikaler Schnitt | Fachlich vollständige Scheibe durch alle Schichten (ADR-002). |
| **Vitest** | — | Unit-/Komponenten-Testrunner für das Vite-/Vue-Frontend. |
| **Playwright** | — | Browser-Automatisierung für E2E-Tests. |
| **playwright-bdd** | — | Brücke, die Gherkin-`.feature`-Dateien in Playwright-Tests übersetzt (`bddgen`). |
| **Testpyramide** | — | Leitbild: viele schnelle Unit-/API-Tests, wenige teure E2E-Tests (ADR-013). |
| **Co-Location** | Test-Nähe | Unit-/Komponententest liegt neben der geprüften Einheit (`*.spec.ts` neben `.vue`/`.ts` in `src/`); Frontend-Konvention (ADR-013). |

## Web, API & Sicherheit

| Kürzel | Bedeutung | Erläuterung |
|---|---|---|
| **API** | Application Programming Interface | Programmierschnittstelle; hier die JSON-HTTP-Schnittstelle des Backends. |
| **REST** | Representational State Transfer | Architekturstil für HTTP-APIs. |
| **HTTP/HTTPS** | HyperText Transfer Protocol (Secure) | Web-Protokoll; HTTPS = TLS-verschlüsselt. |
| **JSON** | JavaScript Object Notation | Datenformat der API-Antworten. |
| **SPA** | Single-Page Application | Client-seitige Web-App (hier Vue), die Views ohne Vollreload wechselt. |
| **PWA** | Progressive Web App | Installier-/offlinefähige Web-App (via `vite-plugin-pwa`). |
| **Same-Origin** | Gleiche Herkunft | SPA und API unter derselben Domain → kein CORS (ADR-010). |
| **Dev-Proxy** | Entwicklungs-Weiterleitung | Vite reicht `/api`+`/health` lokal an Django (`127.0.0.1:8000`) weiter → Dev = Prod-Same-Origin. |
| **CORS** | Cross-Origin Resource Sharing | Browser-Regeln für Anfragen über Herkunftsgrenzen; durch Same-Origin vermieden. |
| **CSRF** | Cross-Site Request Forgery | Angriffsklasse; Django schützt per CSRF-Token/`CSRF_TRUSTED_ORIGINS`. |
| **XSS** | Cross-Site Scripting | Einschleusen von Fremd-JS; u. a. via `X-Content-Type-Options`/CSP gemindert. |
| **TLS/SSL** | Transport Layer Security | Transportverschlüsselung (SSL = veralteter Vorgängername). |
| **HSTS** | HTTP Strict Transport Security | Header, der Browser dauerhaft auf HTTPS zwingt. |
| **SAN** | Subject Alternative Name | Mehrere Domains in **einem** TLS-Zertifikat (ADR-010). |
| **LE** | Let's Encrypt | Kostenlose Zertifizierungsstelle; Zertifikate via Certbot. |
| **CSP** | Content Security Policy | Header, der erlaubte Quellen für Skripte/Assets einschränkt. |
| **OWASP** | Open Worldwide Application Security Project | Referenz für Web-Sicherheitsrisiken (OWASP Top 10). |
| **CA** | Certificate Authority | Zertifizierungsstelle (Staging-CA = Test-Zertifikate). |

## Backend, Infrastruktur & Betrieb

| Kürzel | Bedeutung | Erläuterung |
|---|---|---|
| **ORM** | Object-Relational Mapping | Djangos Abbildung Objekte ↔ Datenbanktabellen. |
| **DRF** | Django REST Framework | Bewusst NICHT genutzt (ADR-005); stattdessen `JsonResponse`. |
| **CI** | Continuous Integration | Automatisches Bauen/Testen bei jedem Push/PR (GitHub Actions). |
| **CD** | Continuous Delivery/Deployment | Automatische Auslieferung auf die VM nach grünem CI. |
| **Gate / gaten** | Qualitäts-Schranke | Ein Schritt „gatet" den nächsten, wenn dieser nur bei grüner Bedingung läuft (die CI gatet den Deploy). |
| **VM** | Virtual Machine | Der 1&1/IONOS-Server, auf dem die App läuft (ADR-008). |
| **SSH** | Secure Shell | Verschlüsselter Fernzugriff auf die VM. |
| **DNS** | Domain Name System | Namensauflösung (Domain → IP). |
| **UFW** | Uncomplicated Firewall | Ubuntu-Firewall-Frontend. |
| **ACL** | Access Control List | Feingranulare POSIX-Dateirechte (setfacl), umask-unabhängig via Default-ACL. |
| **POSIX** | Portable Operating System Interface | Unix-Standard; hier für ACL-/Dateirechte-Semantik. |
| **systemd** | — | Linux-Dienstverwaltung; die App läuft als `binokel-tracker.service`. |
| **Gunicorn** | — | WSGI-Server, der Django-Prozesse hinter Nginx betreibt. |
| **WSGI/ASGI** | (A)Synchronous Server Gateway Interface | Schnittstelle Python-Webapp ↔ Server. |
| **Nginx** | — | Reverse Proxy + Auslieferung statischer Dateien/SPA. |
| **SQLite** | — | Dateibasierte Datenbank für V1 (PostgreSQL später, ADR-008). |
| **WAL** | Write-Ahead Logging | SQLite-Journalmodus; relevant für konsistente Backups. |
| **LTS** | Long-Term Support | Langzeit-unterstützte Version (Ubuntu 24.04, Node 22). |
| **ESM** | (1) Extended Security Maintenance / (2) ECMAScript Modules | (1) Ubuntu-Langzeit-Sicherheitssupport; (2) JS-Modulsystem `import`/`export`. Bedeutung aus Kontext. |
| **DR** | Disaster Recovery | Notfallwiederherstellung (Offsite-Backup, FUTURE-003). |
| **MVP** | Minimum Viable Product | Kleinste nutzbare Produktversion. |
| **ADR-Lineage / Lineage** | Zertifikats-Abstammung | Certbot-Ordner `live/<domain>/`; bei SAN die des ersten `-d` (ENG-005). |

## Werkzeuge & Frontend-Ökosystem

| Kürzel/Begriff | Bedeutung | Erläuterung |
|---|---|---|
| **uv** | — | Schneller Python-Paket-/Interpreter-Manager (Backend), pinnt via `.python-version`. |
| **venv** | Virtual Environment | Isolierte Python-Umgebung (`.venv/`). Node-Äquivalent: `node_modules/`. |
| **fnm** | Fast Node Manager | Node-Versions-Manager (User-Space), liest `.node-version` (ADR-012). |
| **npm** | Node Package Manager | Paketmanager für Node; Sperrdatei `package-lock.json`. |
| **corepack** | — | Node-Werkzeug zum Bereitstellen/Pinnen des Paketmanagers. |
| **Node.js** | — | JavaScript-Laufzeit für Build/Tests des Frontends. |
| **Vite** | — | Build-Tool + Dev-Server für die Vue-SPA. |
| **Vue** | — | Frontend-Framework (Version 3.5, Composition API). |
| **Pinia** | — | State-Management für Vue. |
| **Tailwind CSS** | — | Utility-first-CSS-Framework (mobil-first). |
| **TS** | TypeScript | Typisiertes JavaScript. |
| **Capacitor** | — | Verpackt die Web-App später als native App. |
| **Pinnen (pin)** | Version festnageln | Exakte Version festlegen (statt „neueste") für Reproduzierbarkeit — z. B. `.node-version`, `package-lock.json`, Actions auf Commit-SHA. |
| **SHA / SHA256** | Secure Hash Algorithm | Prüfsumme zur Integritätsverifikation von Downloads. |
| **GPG** | GNU Privacy Guard | Signatur-/Verschlüsselungswerkzeug (Signaturkette bei Paketen). |

## Sonstiges

| Kürzel | Bedeutung | Erläuterung |
|---|---|---|
| **PR** | Pull Request | Änderungsantrag/Review-Einheit auf GitHub. |
| **UI/UX** | User Interface / User Experience | Oberfläche bzw. Nutzungserlebnis. |
| **OpenAPI** | — | Maschinenlesbarer API-Vertrag (hier handgeschrieben, 3.1; Auto-Schema = FUTURE-002). |
| **KaTeX** | — | Formelsatz in Markdown (Doku). |
| **1&1 / IONOS** | — | Hosting-Anbieter der Produktions-VM. |
