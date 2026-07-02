"""
Step-Definitionen für: runde_deoppeltes_abgehen.feature
Slice 4 — Runde vollständig ausgespielt, Reizwert nicht erreicht.
"""
from behave import given, when, then, step


# ---------------------------------------------------------------------------
# Given
# ---------------------------------------------------------------------------

@given("eine regulär vollständig ausgespielte Runde mit Reizwert {reizwert:d}")
def step_vollstaendig_ausgespielte_runde(context, reizwert):
    context.reizwert = reizwert
    context.spielmacher_meldepunkte = None
    context.spielmacher_stichwerte = None
    context.bekannte_stichwerte = []
    context.gegenspieler_meldepunkte = None
    context.gegenspieler_stiche = None
    context.gegenspieler_stichwerte = None
    context.rundenausgang_vorgabe = None
    context.fehler = None


# ---------------------------------------------------------------------------
# Then
# ---------------------------------------------------------------------------

@then("werden die {stichwerte:d} Stichwerte des Gegenspielers gewertet")
def step_gegenspieler_stichwerte_gewertet(context, stichwerte):
    assert context.gegenspieler_stichwerte_gewertet == stichwerte, (
        f"Erwartet {stichwerte} Stichwerte, "
        f"aber erhalten: {context.gegenspieler_stichwerte_gewertet}"
    )


@then("werden die Meldepunkte des Gegenspielers mit 0 gewertet")
def step_gegenspieler_meldepunkte_null(context):
    assert context.gegenspieler_meldepunkte_gewertet == 0, (
        f"Erwartet 0 Meldepunkte, aber erhalten: {context.gegenspieler_meldepunkte_gewertet}"
    )


# ---------------------------------------------------------------------------
# And / Step (kontextneutral)
# ---------------------------------------------------------------------------

@step("ein Gegenspieler hat {stichwerte:d} Stichwerte")
def step_gegenspieler_stichwerte(context, stichwerte):
    context.gegenspieler_stichwerte = stichwerte


@step("jeder aktive Gegenspieler erhält 30 Mitpunkte")
def step_gegenspieler_mitpunkte_doppelt(context):
    assert context.mitpunkte_pro_gegenspieler == 30, (
        f"Erwartet 30 Mitpunkte, aber erhalten: {context.mitpunkte_pro_gegenspieler}"
    )
