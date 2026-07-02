"""
Step-Definitionen für: runde_tausender.feature
Slice 5 — Sonderspiel ohne numerische Wertung, nur Sternvergabe.
"""
from behave import given, when, then, step

from scoring.domain import Rundenausgang

_TAUSENDER_AUSGANG_MAP = {
    "gewonnen": Rundenausgang.TAUSENDER_GEWONNEN,
    "verloren": Rundenausgang.TAUSENDER_VERLOREN,
}


# ---------------------------------------------------------------------------
# Given
# ---------------------------------------------------------------------------

@given("eine Runde ist als Tausender angesagt")
def step_tausender_angesagt(context):
    context.ist_tausender = True
    context.rundenausgang_vorgabe = None
    context.fehler = None


# ---------------------------------------------------------------------------
# Then
# ---------------------------------------------------------------------------

@then("erhält nur der Spielmacher einen Stern")
def step_spielmacher_stern(context):
    assert context.spielmacher_stern is True, "Erwartet: Spielmacher erhält Stern."
    assert context.gegenspieler_stern is False, "Erwartet: Gegenspieler erhalten keinen Stern."


@then("erhalten die beiden aktiven Gegenspieler jeweils einen Stern")
def step_gegenspieler_sterne(context):
    assert context.gegenspieler_stern is True, "Erwartet: Gegenspieler erhalten Stern."
    assert context.spielmacher_stern is False, "Erwartet: Spielmacher erhält keinen Stern."


@then("werden keine Meldepunkte erfasst")
def step_keine_meldepunkte(context):
    assert context.tausender_meldepunkte_gewertet is None, (
        f"Erwartet None, aber erhalten: {context.tausender_meldepunkte_gewertet}"
    )


@then("bleibt der numerische Punktestand für alle Spieler unverändert")
def step_punktestand_unveraendert(context):
    assert context.numerischer_punktestand_nachher == context.numerischer_punktestand, (
        "Punktestand hat sich bei Tausender verändert."
    )


# ---------------------------------------------------------------------------
# And / Step (kontextneutral)
# ---------------------------------------------------------------------------

@step('der Tausender-Ausgang ist "{ausgang}"')
def step_tausender_ausgang(context, ausgang):
    context.rundenausgang_vorgabe = _TAUSENDER_AUSGANG_MAP[ausgang]


@step("die aktiven Gegenspieler erhalten keinen Stern")
def step_gegenspieler_kein_stern(context):
    assert context.gegenspieler_stern is False, "Erwartet: Gegenspieler erhalten keinen Stern."


@step("der Spielmacher erhält keinen Stern")
def step_spielmacher_kein_stern(context):
    assert context.spielmacher_stern is False, "Erwartet: Spielmacher erhält keinen Stern."


@step("es werden keine Stichwerte erfasst")
def step_keine_stichwerte(context):
    assert context.tausender_stichwerte_gewertet is None, (
        f"Erwartet None, aber erhalten: {context.tausender_stichwerte_gewertet}"
    )


@step("es werden keine Mitpunkte erfasst")
def step_keine_mitpunkte(context):
    assert context.tausender_mitpunkte_gewertet is None, (
        f"Erwartet None, aber erhalten: {context.tausender_mitpunkte_gewertet}"
    )


@step("der numerische Punktestand vor der Runde ist bekannt")
def step_punktestand_bekannt(context):
    context.numerischer_punktestand = {"Anna": 100, "Bernd": 200, "Carla": 150, "Dirk": 80}
