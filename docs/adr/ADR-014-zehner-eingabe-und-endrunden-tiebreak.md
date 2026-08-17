# ADR-014 – Zehner-Eingabe des STAND (Option 1) und Endrunden-1er-Tiebreak (Variante 2b)

## Status

Angenommen (17.08.2026)

Ersetzt/überstimmt: die frühere step=1-Entscheidung aus **TASK-012.2** („Stichwerte
durchgängig 1er-genau") sowie den ersten, hinfälligen Rubber-Duck-Review zur
**Aggregations-Rundung** (kaufmännische Zehner-Rundung beim Summieren + akzeptierte
250-Divergenz) aus dem Testprotokoll (FND-002).

## Kontext

Aus der manuellen Test-Session (Tester-Agent, 17.08.2026, `docs/testing/explorative-testprotokoll.md`)
stammt **FND-002 (HOCH):** Der kumulierte STAND (Zwischen- und Endstand) zeigte Einerstellen
(Beleg `Dirk 239`). Die Anschreibe-Kernregel verlangt aber, dass der STAND **immer auf Zehner**
geführt wird (Anschreibetabelle §5).

Ein erster Lösungsweg (kaufmännische Rundung **beim Aggregieren**, `punktestaende_gerundet_laden`)
hätte eine 250-Divergenz je Runde zugelassen (95+95+60 → 100+100+60 = 260). Der Repo-Eigentümer
hat diese Divergenz **überstimmt:** Die 250 muss auch im Rundungsfall exakt eingehalten werden.

Zugleich sind 1er-genaue Stichwerte weiterhin **sieg-relevant**: In der letzten Runde entscheidet
bei Gleichstand der exakte Auszählwert (§9.3). Dieses exakte Zählen darf nicht verlorengehen,
sondern wird an die Stelle **relokalisiert**, an der es wirklich zählt — die Endrunde.

## Entscheidung

**Option 1 — Zehner-Rundung an der EINGABE (nicht bei der Aggregation).**
Normale Runden werden in vollen Zehnern erfasst (Eingabeschritt 10). Damit ist jeder in den
STAND einfließende Wert (Stichwerte, Meldepunkte, Reizwert) ein Vielfaches von 10, der STAND
automatisch auf Zehner (**STAND-Zehner-Invariante**) und die 250er-Kontrollsumme gilt trivial
auf Zehnern. Grenzfälle löst der Mensch bei der Eingabe (95/95/60 → 100/90/60). Es gibt **keine**
Rundungsfunktion beim Summieren und **keine** 260-Divergenz.

**Variante 2b — 1er nur in der letzten Runde für den Tiebreak.**
1er-genaue Stichwerte werden ausschließlich in der letzten Runde und ausschließlich für den
Gleichstand-Tiebreak erfasst. Sie fließen **nicht** in den STAND ein und werden über den bereits
vorhandenen Backend-Mechanismus `sieger_ermitteln(exakte_stichwerte=…)` bzw. die Query
`?exakte_stichwerte=Name:Wert,…` ausgewertet.

### Durchsetzung (nach Rubber-Duck-Design-Review, CONDITIONAL GO)

- **Frontend (`RundeForm.vue`):** Stichwert-Felder `step=10`. `step=10` allein genügt nicht —
  getipptes `99` (99+91+60=250) würde durchrutschen. Daher **explizite Modulo-10-Validierung**
  als Absperr-Bedingung + Hinweis (`stichwerte-modulo-fehler`) für Stichwerte, Meldepunkte und
  Reizwert. In der letzten Runde zusätzliche **separate, optionale 1er-Tiebreak-Felder** je aktivem
  Spieler; deren Werte werden im Pinia-`spiel`-Store abgelegt und von `SpielendeView` als
  `"Name:Wert,…"` an `siegerErmitteln` durchgereicht.
- **Backend (`use_cases.stichwerte_validieren` + `views.runden_view`):** Modulo-10 (+ 250-Kontrollsumme)
  werden im HTTP-Pfad für die Rundentypen `normal` und `doppeltes_abgehen` erzwungen (HTTP 400 bei
  Verstoß), passend zu ADR-006/013 (fachliche Wahrheit auf API-Ebene, nicht nur Frontend).

## Konsequenzen

- Der STAND ist per Konstruktion immer auf Zehner; FND-002 ist im Kern behoben.
- Kein Schema-/Datenmodell-Umbau für diese Aufgabe: `spielmacher_stichwerte` ist für die
  STAND-Rundung **nicht** nötig (nur für die M|S-Aufschlüsselung von TASK-014).
- Bestehende Django-/Behave-Fixtures nutzen bereits Zehner-Werte und bleiben grün.
- **Residualrisiko (NIEDRIG-1):** Der in der letzten Runde aussetzende Geber bringt keinen
  Endrunden-Stich ein und nimmt am 1er-Tiebreak nicht teil (§9.3). Ein Gleichstand, an dem der
  Geber beteiligt wäre, ist über die letzten 1er nicht auflösbar — für V1 akzeptiert.

## Normative Quellen

- `docs/rule-set-v1.md` §9.1 (Zehner-Eingabe), §9.3 (Endrunden-Tiebreak), §9.4 (1er nur Endrunde), §17.2
- `docs/ubiquitous-language.md` (STAND-Rundung, Zehner-Eingabe, Endrunden-Tiebreak)
- `docs/testing/explorative-testprotokoll.md` (FND-001, FND-002)
- ADR-006 (Behave HTTP-Blackbox), ADR-013 (Teststrategie)
