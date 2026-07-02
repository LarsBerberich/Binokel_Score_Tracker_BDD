"""
Step-Definitionen für: runde_einfaches_abgehen_auswerten.feature
Slice 3 — einfachster Verlustfall, Ausnahme vom Stich-Zwang für Gegenspieler.
"""
from behave import given, when, then, step

from scoring.domain import Rundenausgang


# ---------------------------------------------------------------------------
# Given
# ---------------------------------------------------------------------------

@given("der Spielmacher hat den Dapp gesehen")
def step_dapp_gesehen(context):
    context.dapp_gesehen = True
    context.fehler = None


# ---------------------------------------------------------------------------
# When
# ---------------------------------------------------------------------------

@when("der Spielmacher einfach abgeht")
def step_einfach_abgehen(context):
    context.rundenausgang = Rundenausgang.EINFACHES_ABGEHEN


# ---------------------------------------------------------------------------
# Then
# ---------------------------------------------------------------------------

@then("werden die Meldepunkte des Gegenspielers gewertet")
def step_gegenspieler_meldepunkte_gewertet(context):
    assert context.gegenspieler_meldepunkte_gewertet == context.gegenspieler_meldepunkte, (
        f"Erwartet Meldepunkte {context.gegenspieler_meldepunkte}, "
        f"aber erhalten: {context.gegenspieler_meldepunkte_gewertet}"
    )


@then("erhält jeder aktive Gegenspieler 30 Mitpunkte")
def step_gegenspieler_mitpunkte_einfach(context):
    assert context.mitpunkte_pro_gegenspieler == 30, (
        f"Erwartet 30 Mitpunkte, aber erhalten: {context.mitpunkte_pro_gegenspieler}"
    )


# ---------------------------------------------------------------------------
# And / Step (kontextneutral)
# ---------------------------------------------------------------------------

@step("es wurde noch kein Stich gespielt")
def step_kein_stich_gespielt(context):
    context.kein_stich_gespielt = True
