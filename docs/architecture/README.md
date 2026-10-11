# Architekturdokumentation (C4)

Die Modelle folgen dem [C4-Modell](https://c4model.com) (Simon Brown) und liegen als
draw.io-Dateien unter [c4/](c4/). Sie beschreiben den **IST-Stand** (Stand 11.10.2026,
Commit `cff5878`), nicht einen Zielzustand.

| Ebene | Datei | Inhalt |
|---|---|---|
| 1 – Systemkontext | [c4-1-system-kontext.drawio](c4/c4-1-system-kontext.drawio) | Spieler:in, Entwickler, GitHub, Let's Encrypt |
| 2 – Container | [c4-2-container.drawio](c4/c4-2-container.drawio) | Nginx, Vue-SPA, Django-API (Gunicorn), SQLite |
| 3 – Komponenten Backend | [c4-3-komponenten-backend.drawio](c4/c4-3-komponenten-backend.drawio) | urls, views, use_cases, domain, repositories, models |
| 3 – Komponenten Frontend | [c4-3-komponenten-frontend.drawio](c4/c4-3-komponenten-frontend.drawio) | Views, Komponenten, Store, API-Client, domain |
| Deployment | [c4-deployment.drawio](c4/c4-deployment.drawio) | Entwicklung, GitHub Actions, IONOS-VM |

Ebene 4 (Code) wird bewusst nicht gepflegt; [../datenmodell-v1.puml](../datenmodell-v1.puml)
deckt das Datenmodell ab.

## Bearbeiten

Die `.drawio`-Dateien sind unkomprimiertes XML und diff-bar. Bearbeitung in draw.io
Desktop oder der VS-Code-Erweiterung `hediet.vscode-drawio`. Pflege-Regel: Wer
Schichten, Container oder Deployment ändert, aktualisiert das betroffene Diagramm im
selben Commit.

## Konformitätsprüfung

Ergebnis der Prüfung gegen moderne Architekturmuster:
[architektur-konformitaet.md](architektur-konformitaet.md).
