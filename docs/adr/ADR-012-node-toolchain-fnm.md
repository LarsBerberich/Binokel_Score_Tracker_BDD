# ADR-012 – Node-Toolchain: fnm (verifizierte Binary) für die Frontend-Entwicklung

## Status

Angenommen (23.07.2026)

## Kontext

Phase 2 (Vue-SPA, ADR-011) benötigt eine **Node.js**-Laufzeit für Vite, den
Build-Prozess, Vitest und Playwright. Zu klären war, **wie Node bereitgestellt wird**:

- **isoliert und pro Projekt versionierbar** (Analogie zu `uv`/`.python-version` im Backend),
- **ohne systemweite Änderungen/`sudo`** (dieselbe Philosophie wie die uv-Installation),
- **mit nachvollziehbarer Integritätsprüfung** (kein blindes `curl … | bash`).

Betrachtete Optionen:

1. **`fnm`** (Fast Node Manager) — User-Space-Binary, liest `.node-version`, kein sudo.
2. **`nvm`** — shell-basiert, langsamer, ebenfalls User-Space.
3. **`volta`** — pinnt zusätzlich den Paketmanager, etwas mehr Automatik/„Magie".
4. **`apt` (Ubuntu-Paket `nodejs`)** — systemweit, `sudo`, aber nur **Node 18** (EOL,
   zu alt für aktuelles Vite 7, das Node 20+ verlangt).
5. **`apt` + NodeSource-Repo** — aktuelles Node, aber systemweit, `sudo`, und die
   Repo-Einbindung erfolgt selbst per `curl … | bash`.

## Entscheidung

**`fnm`, installiert über eine verifizierte Release-Binary** (nicht per `curl | bash`):

1. Release-Metadaten über die GitHub-API abrufen (Version + serverseitig berechneter
   SHA256-`digest` des Assets).
2. `fnm-linux.zip` von der GitHub-Releases-URL herunterladen.
3. **SHA256 der heruntergeladenen Datei gegen den GitHub-Digest verifizieren** — nur bei
   Übereinstimmung fortfahren.
4. Binary nach `~/.local/bin/fnm` installieren (User-Space, kein sudo).
5. Node **22 LTS** installieren und als Default setzen; `fnm env --use-on-cd` idempotent
   in `~/.bashrc` verankern.

**Konkret verwendet (23.07.2026):** fnm `v1.39.0`, Node `v22.23.1`, npm `10.9.8`.

Die Node-Version wird pro Projekt über **`.node-version`** (im künftigen `frontend/`)
gepinnt. Die Paketisolation übernimmt das projekt-lokale **`node_modules/`** (das
Node-Äquivalent zum Python-`.venv`), gesperrt über **`package-lock.json`**.

## Begründung

- **Konsistenz mit dem Backend:** `fnm` + `.node-version` verhält sich zu Node wie
  `uv` + `.python-version` zu Python — projekt-lokal, reproduzierbar, ohne sudo.
- **Sicherheit:** Der verifizierte-Binary-Weg vermeidet die Hauptschwäche der üblichen
  `curl … | bash`-Installer (Ausführung ungeprüften Codes). Die SHA256-Prüfung gegen
  den GitHub-Digest ankert die Integrität des Downloads.
- **Aktualität:** freie Wahl des aktuellen LTS (22) statt des veralteten apt-Node 18.
- **Least footprint:** keine systemweiten Änderungen, vollständig im Home reversibel
  (`~/.local/bin/fnm`, `~/.local/share/fnm`, `.bashrc`-Block).

### Ehrliche Einordnung des Vertrauensmodells

Der GitHub-`digest` wird von GitHub berechnet, und der Download stammt ebenfalls von
GitHub — die Prüfung sichert damit die **Übertragungs-/Ablageintegrität**, ersetzt aber
keine unabhängige Signatur des Herausgebers (fnm signiert Releases nicht per GPG). Das
ist ein bewusst akzeptierter Kompromiss und klar besser als ein ungeprüftes `curl|bash`.
Das **größere** laufende Risiko sind ohnehin die **npm-Pakete** in `node_modules/`
(Supply-Chain) — Gegenmaßnahmen: `package-lock.json` committen, Versionen pinnen,
`npm audit`, wenige Abhängigkeiten.

## Konsequenzen

### Positiv
- Reproduzierbare, projekt-lokale Node-Version ohne sudo; identisch zu CI (`actions/setup-node`).
- Nachvollziehbare Integritätsprüfung bei der Installation.
- Vollständig im Home-Verzeichnis reversibel.

### Negativ / Risiken
- Kein GPG-signierter Herausgebernachweis für fnm (durch Digest-Prüfung gemildert).
- Node-/npm-Supply-Chain bleibt als eigenständiges Risiko bestehen (siehe oben).
- Ein Versions-Upgrade von fnm/Node erfordert erneutes Pinnen + Verifikation.

### CI-Abgrenzung
In GitHub Actions wird Node **nicht** über fnm, sondern über die offizielle, auf
Commit-SHA gepinnte Action `actions/setup-node` bereitgestellt (liest dieselbe
`.node-version`). Die lokale Manager-Wahl ist davon entkoppelt.

## Betroffene Artefakte
- `~/.local/bin/fnm`, `~/.bashrc` (Entwicklermaschine; nicht im Repo).
- Künftig: `frontend/.node-version` (gepinnt), `frontend/package.json` + `package-lock.json`.
- CI später: `.github/workflows/ci.yml` → `actions/setup-node` (TASK-007).

## Verweise
- ADR-010 (Same-Origin-Deployment), ADR-011 (Vue-Stack + BDD-Toolchain),
  `docs/development-approach-v1.md`, `docs/glossar.md`.
