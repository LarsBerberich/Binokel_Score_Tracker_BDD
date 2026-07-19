"""
Behave-Testumgebung für den Binokel Score Tracker.

Richtet die Django-Test-Datenbank und einen HTTP-Client pro Szenario ein.
Ab TASK-006 (ADR-006) läuft Slice 1 vollständig über HTTP.
Normative Quelle: docs/adr/ADR-006-behave-http-blackbox-tests.md
"""
import os
import sys

# backend/ zum Python-Pfad hinzufügen, damit Django die Settings findet
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'binokel_tracker.settings')

import django
django.setup()


def before_all(context):
    """Einmalig: Test-Datenbank anlegen und alle Migrationen anwenden."""
    from django.test.utils import setup_test_environment, setup_databases
    setup_test_environment()
    context._db_config = setup_databases(verbosity=0, interactive=False)


def after_all(context):
    """Einmalig: Test-Datenbank abräumen."""
    from django.test.utils import teardown_databases
    teardown_databases(context._db_config, verbosity=0)


def before_scenario(context, scenario):
    """Pro Szenario: HTTP-Client bereitstellen."""
    from django.test import Client
    context.client = Client()


def after_scenario(context, scenario):
    """Pro Szenario: alle Spieldaten löschen (Cascade auf Runden, Spieler etc.)."""
    from scoring.models import SpielModel
    SpielModel.objects.all().delete()
