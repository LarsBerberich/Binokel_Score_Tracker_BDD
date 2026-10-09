# ADR-017 – Drei-Spieler-Variante: Geber spielt mit

## Status

Angenommen (09.10.2026)

## Kontext

V1 unterstützte ausschließlich 4 Spieler, bei denen pro Runde der Geber aussetzt
(`rule-set-v1.md` §2). Gespielt wird Binokel aber häufig auch zu dritt. Der Wunsch war, das
**so einfach wie möglich** zu ermöglichen — ohne zusätzliche Eingaben, ohne zweiten
Spielmodus im Bedienablauf.

Die Analyse des Bestands zeigte: Die **gesamte Wertung ist spielerzahl-unabhängig**, weil in
beiden Varianten genau **3 Spieler aktiv** sind (Spielmacher + 2 Gegenspieler). Reizwert,
Meldepunkte, Stichwerte, Mitpunkte, Stich-Zwang, 250er-Kontrollsumme, Tausender und
Siegerermittlung bleiben unverändert. Fest verdrahtet war die Spielerzahl nur an drei Stellen:

1. **Validierung** beim Anlegen (genau 4 Spieler, Rundenzahl Vielfaches von 4),
2. **Rotation** der Geber (`% 4`) und
3. **Aktive Spieler** als „alle − Geber" (Repositories, Frontend), samt der Regel
   „Spielmacher ≠ Geber".

## Entscheidung

**Die Spielerzahl (3 oder 4) bestimmt die Variante; es gibt keine separate Auswahl.**

| | 4 Spieler | 3 Spieler |
|---|---|---|
| Geber | setzt aus | spielt mit |
| Aktive Spieler | alle außer Geber | alle |
| Rundenzahl | Vielfaches von 4 | Vielfaches von 3 |

- **Rundenzahl:** muss ein Vielfaches der Spielerzahl sein (jeder Spieler gleich oft Geber).
  Der **Standardwert 12** bleibt unverändert, denn er ist durch 3 und 4 teilbar.
- **Geber bei 3 Spielern:** kann Spielmacher oder Gegenspieler sein. Die Regel „Spielmacher darf
  nicht Geber sein" gilt nur, solange der Geber aussetzt.
- **Domänenmodell:** Die Frage „wer ist aktiv?" wird **einmal** im Domänenobjekt `Spiel`
  beantwortet (`aktive_spieler`, `gegenspieler`, `geber_setzt_aus`). Repositories, Views und
  Use Cases fragen dieses Objekt, statt selbst „alle − Geber" zu rechnen. Das ist die
  DDD-konforme Konsequenz: Die Regel gehört in die Domäne, nicht in jede Schicht einzeln.
- **API (additiv, rückwärtskompatibel):** `POST /api/spiele/` akzeptiert 3 oder 4 Spieler. Die
  Rundenhistorie liefert je Spieler zusätzlich `ist_geber`. Die `rolle` `geber` bedeutet weiterhin
  „setzt aus" und kommt daher nur bei 4 Spielern vor.
- **Persistenz:** keine Migration. `SpielerModel.position` ist bereits eine freie Zahl; die
  Obergrenze „0..3" stand nur im Docstring.

## Konsequenzen

### Positiv

- Die Bedienung bleibt gleich: Wer nur drei Namen einträgt, spielt zu dritt.
- Die Wertungslogik wird **nicht** angefasst — das Risiko fachlicher Regressionen ist klein,
  weil die bestehenden Wertungs-Szenarien unverändert gültig bleiben.
- Beim Endrunden-Tiebreak (ADR-014) entfällt zu dritt das dort akzeptierte Restrisiko, dass der
  aussetzende Geber nicht teilnehmen kann: Alle drei Spieler sind aktiv.

### Negativ / Risiken

- **Spielerzahl nachträglich nicht änderbar:** Ein angelegtes Spiel behält seine Variante.
- **Bestehende 4-Spieler-Spiele** bleiben unverändert (Variante ergibt sich aus der Anzahl der
  gespeicherten Spieler; keine Datenmigration nötig).
- **Dateiname `Anschreibetabelle_4_Spieler.md`** ist nun missverständlich; er bleibt zugunsten
  stabiler Verweise erhalten, das Dokument erhält einen Abschnitt für die Drei-Spieler-Tabelle.
- **Strengere Validierung beim Anlegen (Folge der Umsetzung):** Bisher lehnte nur die Korrektur
  (PUT) „Spielmacher = Geber" ab; das Anlegen (POST) prüfte keine Rollen, und nur das Frontend
  verhinderte den Fall. Die Lesepfade (Sterne, Anschreibetabelle) leiten die Gegenspieler jedoch
  aus dem Spielmacher ab und müssen sich auf eine am Schreibpfad geprüfte Invariante verlassen
  können. Deshalb prüfen jetzt **POST und PUT** über dieselbe Funktion (`_rollen_pruefen`), dass der
  Spielmacher aktiv mitspielt. Das ist bei 4 Spielern eine Verschärfung gegenüber dem Vorzustand:
  ein Aufruf mit Spielmacher = Geber wird nun mit 400 abgelehnt statt stillschweigend
  gespeichert. Die Weboberfläche ist nicht betroffen, sie bietet den Geber nicht zur Auswahl an;
  im Bestand existierten keine solchen Daten.

### Nicht Teil dieser Entscheidung

Andere Spielerzahlen (2, 5 und mehr) und Teamwertung bleiben ausgeschlossen
(`rule-set-v1.md` §2).

## Alternativen

- **Separater Spielmodus „Dreier" mit eigener Auswahl:** verworfen — mehr Bedienung, mehr
  Zustand, kein fachlicher Mehrwert, da die Variante eindeutig aus der Spielerzahl folgt.
- **Spielerzahl als eigenes Feld im Spiel speichern:** verworfen — wäre redundant zur Anzahl der
  `SpielerModel`-Zeilen und könnte mit ihr auseinanderlaufen.
- **Neues Regelwerk `rule-set-v2.md`:** verworfen — die Wertungsregeln sind identisch; ein
  zweites Dokument würde sie duplizieren. Stattdessen wird `rule-set-v1.md` um §3.4 erweitert.

## Referenzen

- `docs/rule-set-v1.md` §2, §3.4, §4, §9.3, §15.3, §18.1
- `docs/ubiquitous-language.md` §4.4, §4.5
- ADR-004 (Repository Pattern), ADR-014 (Endrunden-Tiebreak), ADR-016 (Tausender außer Konkurrenz)
