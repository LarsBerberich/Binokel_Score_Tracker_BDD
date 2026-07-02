# ENG-001: behave + Django – Initialisierung der Testumgebung

**Datum:** 2026-07-02
**Kontext:** Slice 0 – Projektinfrastruktur
**Symptom:** 27 `HOOK-ERROR` beim ersten `behave --no-capture`-Lauf

---

## Problem

`setup_test_environment()` wurde in `before_scenario` aufgerufen:

```python
# features/environment.py – FALSCH
def before_scenario(context, scenario):
    from django.test.utils import setup_test_environment
    setup_test_environment()  # wird 28x aufgerufen
```

Django setzt beim ersten Aufruf intern einen Flag:

```python
_setup_test_environment_called = True
```

Ab dem zweiten Aufruf wirft Django:

```
RuntimeError: setup_test_environment() was already called and
can't be called again without first calling teardown_test_environment().
```

Das ergab 27 `HOOK-ERROR` (ein Fehler pro Szenario, das zweite bis letzte).

---

## Ursache

`before_scenario` wird **einmal pro Szenario** aufgerufen – bei 28 Szenarien also 28x.
`setup_test_environment()` ist aber für **einen einzelnen Aufruf pro Python-Prozess** ausgelegt.

---

## Lösung

`setup_test_environment()` in `before_all` verschieben – dieser Hook läuft genau einmal
pro `behave`-Aufruf:

```python
# features/environment.py – KORREKT
def before_all(context):
    import django
    django.setup()

    from django.test.utils import setup_test_environment
    setup_test_environment()


def before_scenario(context, scenario):
    pass  # Datenbankisolation kommt später hinzu
```

---

## Was `setup_test_environment()` tut

`setup_test_environment()` ist eine **Framework-Funktion von Django** – sie konfiguriert
nicht die eigene App, sondern Django selbst für den Testbetrieb. Sie wird unabhängig
davon ausgeführt, welche Features die eigene App verwendet.

Konkret ersetzt sie:

| Subsystem | Was passiert |
|---|---|
| `EMAIL_BACKEND` | Wird durch `locmem.EmailBackend` ersetzt – kein echter Mailversand aus Tests |
| Request/Response-Signale | Test-Client kann HTTP-Requests simulieren |
| Interner Flag | Verhindert versehentliche Mehrfachinitialisierung |

Das Email-Backend wird also **immer** ersetzt – auch wenn die App keinen Mailversand
kennt. Das ist eine defensive Maßnahme auf Framework-Ebene: jeder `send_mail()`-Aufruf
aus irgendeiner Bibliothek wird in Tests automatisch abgefangen.

---

## Abgrenzung zu `django.setup()`

| Funktion | Zweck |
|---|---|
| `django.setup()` | Initialisiert Django-Framework: lädt Settings, registriert Apps aus `INSTALLED_APPS` |
| `setup_test_environment()` | Schaltet Django in Testmodus: ersetzt Produktions-Backends durch Test-Stubs |

Beide müssen aufgerufen werden, `django.setup()` zuerst.

---

## Datenbankisolation (noch offen)

Aktuell wird die Datenbank zwischen Szenarien **nicht** zurückgesetzt.
Sobald die erste Datenbankoperation in einem Step implementiert ist, muss
`before_scenario` / `after_scenario` um Transaktionsisolation ergänzt werden, z. B.:

```python
from django.test.utils import setup_test_environment
from django.db import transaction

def before_scenario(context, scenario):
    context.transaction = transaction.atomic()
    context.transaction.__enter__()

def after_scenario(context, scenario):
    context.transaction.__exit__(None, None, None)
    transaction.set_rollback(True)
```

Oder alternativ über `behave-django`'s eingebauten `--use-existing-database`-Modus.
Dies wird in einem separaten Engineering Note dokumentiert, sobald der Bedarf konkret wird.
