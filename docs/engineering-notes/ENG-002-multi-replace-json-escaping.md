# ENG-002: multi_replace_string_in_file – JSON-Escaping von Zeilenumbrüchen

**Datum:** 2026-07-02
**Kontext:** Implementierung Slices 2–6, Step-Definitionen

---

## Problem

`multi_replace_string_in_file` schlug mit "String not found" fehl, obwohl der
gesuchte Text visuell korrekt aussah.

---

## Ursache

In JSON-Strings innerhalb des Tool-Parameters bedeutet `\\n` ein **literales
Backslash-n** (zwei Zeichen: `\` + `n`). Die Datei auf Disk enthält aber
**echte Zeilenumbrüche** (Byte `0x0A`).

```
Datei (Disk):  "raise NotImplementedError(...)\n\n\n@then..."   ← echtes 0x0A
oldString:     "raise NotImplementedError(...)\\n\\n\\n@then..."  ← kein Match
```

Der Matcher findet keinen Treffer und gibt "not found" zurück – ohne
weiteren Hinweis auf die Ursache.

---

## Ablenkungsfehler

`cat -A` wurde als Diagnosewerkzeug aufgerufen, um Windows-Zeilenenden (`\r\n`)
oder Encoding-Probleme auszuschließen. Die Ausgabe war unauffällig (`$` am
Zeilenende = normale Unix-Zeilenenden, `M-CM-<` = reguläres UTF-8). Die
eigentliche Ursache war trivial und hätte vor dem Tool-Aufruf erkannt werden
sollen.

---

## Lösung

Bei vollständig zu ersetzenden Dateien (z. B. Stubs → Implementierung) ist
`pathlib.Path.write_text()` via Python-Skript das robustere Mittel:

```python
import pathlib
path = pathlib.Path("features/steps/meine_steps.py")
path.write_text(neuer_inhalt, encoding="utf-8")
```

Für **Teil-Ersetzungen** mit `replace_string_in_file` gilt:
- `oldString` muss exakt mit dem Dateiinhalt übereinstimmen
- Zeilenumbrüche im `oldString` sind **echte `\n`** im JSON, nicht `\\n`
- Mindestens 3 Zeilen Kontext vor und nach der Zielstelle einschließen
- Bei Unsicherheit vorher mit `read_file` den genauen Inhalt prüfen

---

## Präventionsregel

> Vor jedem `multi_replace_string_in_file`-Aufruf mit mehrzeiligem `oldString`:
> Den exakten Dateiinhalt mit `read_file` lesen und erst dann den `oldString`
> wortwörtlich aus dem gelesenen Inhalt übernehmen.
