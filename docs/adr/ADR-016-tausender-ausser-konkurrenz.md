# ADR-016 – Tausender außer Konkurrenz: Sequenz vs. gezählte Spielrunde

## Status

Angenommen (27.08.2026)

## Kontext

Beim explorativen Durchspielen (FND-006, `docs/testing/explorative-testprotokoll.md`)
wurde festgestellt, dass ein **Tausender** fälschlich wie eine reguläre Runde behandelt
wurde: der Rundenzähler erhöhte sich, der Geber rotierte, und ein Tausender in der letzten
Runde beendete das Spiel.

Fachregel (USER-präzisiert, `rule-set-v1.md` §15.6): Ein Tausender läuft **außer Konkurrenz**
und zählt **nicht** als gespielte Runde. Rundenzähler und Geber bleiben stehen; es wird
wiederholt, bis eine reguläre Runde folgt. Die numerische Wertung war bereits korrekt
(`_runde_beitrag` schließt Tausender aus), der Fehler betraf ausschließlich **Zählung,
Geberrotation und Spielende**.

Ursache: In `RundeModel.rundennummer` verschmolzen zwei Konzepte —
die **Erfassungsreihenfolge/Identität** (jede Runde eindeutig, Grundlage der Korrektur der
letzten Runde, ADR-015) und die **gezählte Spielrunde** (Runde X/Y, treibt Geber und
Spielende über `spieler[(n-1) % 4]`).

## Entscheidung

Die beiden Konzepte werden entkoppelt:

- **`rundennummer` = Erfassungs-Sequenz.** Jede erfasste Runde – auch ein Tausender – erhält
  eine eindeutige, fortlaufende, **serverseitig vergebene** Sequenz (`max+1`). Der
  `UniqueConstraint(spiel, rundennummer)` bleibt. Damit sind mehrere Tausender in derselben
  gezählten Runde persistierbar, und die Korrektur der letzten Runde (höchste Sequenz, ADR-015)
  funktioniert unverändert.
- **Gezählte Spielrunde `zaehlrunde` = abgeleitet, nicht persistiert.** Sie ergibt sich als
  Anzahl der nicht-Tausender-Runden. Bewusst **kein neues DB-Feld** (keine Migration, kein
  Backfill-Drift): Ableitung ist immer konsistent, und ein Korrektur-Typwechsel
  (normal ↔ Tausender) wirkt automatisch korrekt. Tausender-Runden haben `zaehlrunde = null`.
- **Geber serverseitig aus der gezählten Runde.** `repositories.geber_fuer_sequenz(spiel_id, s)`
  = `spieler[(Anzahl nicht-Tausender-Runden mit Sequenz < s) % 4]`. Ohne Tausender identisch zur
  bisherigen Rotation (`Spiel.geber_in_runde`); mit Tausender bleibt der Geber über die außer-
  Konkurrenz-Runden stehen. Diese Ableitung nutzt die **Korrektur (PUT)**.
- **POST-Geber weiterhin aus dem Body.** Bewusste Abweichung von der vollständigen
  serverseitigen Ableitung: das **Frontend** leitet Geber und gezählte Runde aus der
  autoritativen Rundenhistorie ab (Anzahl nicht-Tausender-Runden) und sendet den korrekten
  Geber. Grund: eine serverseitige POST-Override hätte den bestehenden Geber-Contract und ~40
  Django-Integrationstests gebrochen, ohne fachlichen Mehrwert (Frontend und
  `geber_fuer_sequenz` nutzen dieselbe Formel; Vitest sichert die Frontend-Ableitung ab). Die
  vom Client mitgeschickte `rundennummer` wird ignoriert (Sequenz vergibt der Server).
- **Frontend leitet Fortschritt/Geber/Spielende aus der Historie ab**, kein lokaler Zähler
  mehr (`stores/spiel.ts` ohne `aktuelleRundennummer`/`naechsteRunde`). Nach jeder gespeicherten
  Runde wird die Historie neu geladen; gezählte Runde, Geber und `istBeendet` ergeben sich als
  Funktion der Historie. Ein Erfassungs-Schlüssel (Anzahl gespeicherter Runden) setzt das
  Formular auch nach einem Tausender zurück, obwohl die gezählte Runde gleich bleibt.

## Konsequenzen

- **Kein Datenmodell-Change/Migration.** Nur Semantik (`rundennummer` = Sequenz) und
  Ableitungslogik ändern sich; die Historie-Antwort trägt zusätzlich `sequenz`, `zaehlrunde`
  und (bereits vorhanden) `ist_tausender`.
- **Anschreibetabelle:** Tausender-Zeile mit `★` und „außer Konkurrenz" ohne gezählte Nummer;
  reguläre Zeilen mit fortlaufender `zaehlrunde`.
- **Altdaten:** Bestandsspiele mit historisch mitgezählten Tausendern zeigen nach dem Fix
  veränderte gezählte Rundennummern (die alte Zählung war der Bug) – bewusst akzeptiert.
- **Korrektur:** Ein Tausender ist editierbar, solange er die höchste Sequenz ist (ADR-015);
  danach → 409.

## Alternativen

- **`zaehlrunde` persistieren:** verworfen – erzwingt Migration/Backfill und muss bei jeder
  Korrektur neu berechnet werden (Drift-Risiko).
- **`UniqueConstraint` lockern / mehrere Runden je Nummer:** verworfen – bricht die Identität
  für die Korrektur der letzten Runde (ADR-015).
- **Vollständige serverseitige POST-Geber-Ableitung:** zurückgestellt (V2) – siehe oben.

## Referenzen

- FND-006 – `docs/testing/explorative-testprotokoll.md`
- `docs/rule-set-v1.md` §15.6
- ADR-004 (Repository-Pattern), ADR-015 (Korrektur nur letzte Runde), ADR-006 (Behave-HTTP-Blackbox)
