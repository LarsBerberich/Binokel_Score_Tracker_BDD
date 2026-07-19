# ENG-003 — Behave: Zusammenspiel von Gherkin-Feature und Step-Definitionen

**Datum:** 19.07.2026  
**Kontext:** Frage zum Zusammenspiel von `spiel_anlegen.feature` und `spiel_anlegen_steps.py`

---

## Das Framework: Behave

**Behave** ist ein Python-BDD-Framework. BDD = Behaviour-Driven Development. Es nutzt die **Gherkin-Sprache** für Feature-Dateien und verbindet jede Zeile darin mit einer Python-Funktion über Musterabgleich.

---

## Wie Feature-Datei und Steps-Datei zusammenpassen

```
spiel_anlegen.feature          Behave-Runner             spiel_anlegen_steps.py
(Was soll passieren?)    →   (Sucht passenden Step)  →  (Wie es passiert)
                         ←   (Ergebnis: PASS/FAIL)   ←  (assert)
```

Die Feature-Datei beschreibt **Was** — die Steps-Datei beschreibt **Wie**. Behave sucht beim Ausführen jede Szenario-Zeile in ALLEN `steps/*.py`-Dateien und führt die erste Übereinstimmung aus.

---

## Ein konkretes Beispiel durchgehen

**Feature-Zeile:**
```gherkin
Wenn die Spielerreihenfolge "Anna, Bernd, Carla, Dirk" gegen den Uhrzeigersinn erfasst wird
```

**Passender Step:**
```python
@when('die Spielerreihenfolge "{reihenfolge}" gegen den Uhrzeigersinn erfasst wird')
def step_reihenfolge_erfassen(context, reihenfolge):
    context.spieler = _spieler_aus_string(reihenfolge)
```

Behave macht hier zwei Dinge:
1. **Musterabgleich**: Der String in `@when(...)` wird als Muster behandelt. `{reihenfolge}` ist ein **benannter Parameter** — alles zwischen den Anführungszeichen wird daraus extrahiert.
2. **Übergabe**: Der extrahierte Wert `"Anna, Bernd, Carla, Dirk"` landet als Argument `reihenfolge` in der Funktion.

---

## Die `@`-Dekoratoren — vier Varianten

```python
@given(...)   # Angenommen  — Ausgangszustand herstellen
@when(...)    # Wenn        — Aktion ausführen
@then(...)    # Dann        — Ergebnis prüfen
@step(...)    # Und / Aber  — Kontextneutral, passt überall
```

Diese vier sind **Python-Dekoratoren** aus `from behave import given, when, then, step`. Ein Dekorator ist eine Funktion, die eine andere Funktion modifiziert. Hier registriert jeder Dekorator die Funktion in Behaves **Step-Registry** — einer internen Tabelle, die Muster auf Funktionen abbildet:

```
"es wird ein neues V1-Spiel angelegt"  →  step_neues_spiel
"die Spielerreihenfolge {x} erfasst"   →  step_reihenfolge_erfassen
"wird das Spiel mit {n:d} Runden ..."  →  step_spiel_mit_runden
```

**`{n:d}`** ist ein typisierter Parameter: `:d` bedeutet `int`. Behave wandelt den String aus der Feature-Zeile automatisch in eine Ganzzahl um.

---

## Der `context`-Parameter

`context` ist Behaves **Shared State** — ein Objekt, das über alle Steps eines Szenarios geteilt wird. Es ist kein globaler State; nach jedem Szenario wird die Ebene geleert (`after_scenario`).

```python
@when('die Spielerreihenfolge "{reihenfolge}" ...')
def step_reihenfolge_erfassen(context, reihenfolge):
    context.spieler = _spieler_aus_string(reihenfolge)   # ① schreiben

@then("wird das Spiel mit {rundenanzahl:d} Runden angelegt")
def step_spiel_mit_runden(context, rundenanzahl):
    antwort = _post_json(context, "/api/spiele/", {"spieler": context.spieler})  # ② lesen
```

Step ① schreibt auf `context.spieler`, Step ② liest davon. Genau so "fließen" Daten zwischen Gherkin-Zeilen durch.

---

## Warum `@given` statt `@when` für manche Steps egal ist

```python
@step("{spieler} ist Geber in Runde {runde:d}")
def step_geber_step(context, spieler, runde):
    ...
```

`@step` registriert die Funktion für **alle vier Keywords** (Angenommen/Wenn/Dann/Und). Das ist nötig, wenn derselbe Text in verschiedenen Positionen vorkommt — hier z.B. einmal als `Und Anna ist Geber in Runde 1` (Given-Block) und einmal als `Dann ist Bernd Geber in Runde 2` (Then-Block).

---

## Ausführungsreihenfolge eines Szenarios

```
spiel_anlegen.feature: Szenario "Spiel mit 4 Spielern..."
│
├─ before_scenario()        ← environment.py: context.client = Client()
│
├─ "Angenommen es wird ein neues V1-Spiel angelegt"
│     → step_neues_spiel()     — setzt context.spieler = None usw.
│
├─ "Wenn die Spielerreihenfolge ... erfasst wird"
│     → step_reihenfolge_erfassen()  — setzt context.spieler = [...]
│
├─ "Und keine abweichende Rundenzahl angegeben wird"
│     → step_standard_rundenzahl()   — setzt context.rundenanzahl = None
│
├─ "Dann wird das Spiel mit 12 Runden angelegt"
│     → step_spiel_mit_runden()      — POST /api/spiele/, assert 201
│
├─ "Und die Spielerreihenfolge bleibt als ... gespeichert"
│     → step_reihenfolge_gespeichert() — assert context.spiel.spieler...
│
└─ after_scenario()         ← environment.py: SpielModel.objects.all().delete()
```

---

## Zusammenfassung

| Gherkin | Python | Zweck |
|---|---|---|
| `Funktionalität:` | — | Dokumentation |
| `Szenario:` | — | Testfall-Grenze |
| `Angenommen/Wenn/Dann/Und` | `@given/@when/@then/@step` | Binding-Schlüsselwort |
| `{parameter}` | Funktionsargument | Wertübergabe |
| `{n:d}` | `int`-Argument | Typisierter Parameter |
| — | `context` | Shared State im Szenario |
