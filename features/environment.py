import sys
import os

# backend/ zum Python-Pfad hinzufügen, damit Django die Settings findet
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'binokel_tracker.settings')


def before_all(context):
    """Wird einmalig vor allen Szenarien ausgeführt."""
    import django
    django.setup()


def before_scenario(context, scenario):
    """Wird vor jedem Szenario ausgeführt — hält die Datenbank sauber."""
    from django.test.utils import setup_test_environment
    setup_test_environment()


def after_scenario(context, scenario):
    """Wird nach jedem Szenario ausgeführt."""
    pass
