"""
Step-Definitionen für: spiel_anlegen.feature
Slice 1 — erstes Feature, Grundlage für alle weiteren Slices.
"""
from behave import given, when, then, step

from scoring.use_cases import spiel_anlegen
from scoring.domain import UngueltigeSpielerzahl, UngueltigeRundenanzahl


# ---------------------------------------------------------------------------
# Hilfsfunktion
# ---------------------------------------------------------------------------

def _spieler_aus_string(reihenfolge: str) -> list[str]:
    """Parst 'Anna, Bernd, Carla, Dirk' in ['Anna', 'Bernd', 'Carla', 'Dirk']."""
    return [s.strip() for s in reihenfolge.split(",")]


# ---------------------------------------------------------------------------
# Given
# ---------------------------------------------------------------------------

@given("es wird ein neues V1-Spiel angelegt")
def step_neues_spiel(context):
    context.spieler = None
    context.rundenanzahl = None
    context.spiel = None
    context.fehler = None


@given('das Spiel wurde mit der Spielerreihenfolge "{reihenfolge}" angelegt')
def step_spiel_mit_reihenfolge(context, reihenfolge):
    context.spiel = spiel_anlegen(_spieler_aus_string(reihenfolge))


# ---------------------------------------------------------------------------
# When
# ---------------------------------------------------------------------------

@when('die Spielerreihenfolge "{reihenfolge}" gegen den Uhrzeigersinn erfasst wird')
def step_reihenfolge_erfassen(context, reihenfolge):
    context.spieler = _spieler_aus_string(reihenfolge)


@when('nur die Spieler "{spieler}" erfasst werden')
def step_ungueltige_spielerzahl(context, spieler):
    context.spieler = _spieler_aus_string(spieler)


# ---------------------------------------------------------------------------
# Then
# ---------------------------------------------------------------------------

@then("wird das Spiel mit {rundenanzahl:d} Runden angelegt")
def step_spiel_mit_runden(context, rundenanzahl):
    context.spiel = spiel_anlegen(context.spieler, context.rundenanzahl)
    assert context.spiel.rundenanzahl == rundenanzahl, (
        f"Erwartet {rundenanzahl} Runden, aber erhalten: {context.spiel.rundenanzahl}"
    )


@then("wird das Spiel nicht angelegt")
def step_spiel_nicht_angelegt(context):
    try:
        spiel_anlegen(context.spieler, context.rundenanzahl)
        assert False, "Kein Fehler wurde ausgelöst, obwohl einer erwartet wurde."
    except (UngueltigeSpielerzahl, UngueltigeRundenanzahl) as fehler:
        context.fehler = fehler


@then("ist {spieler} Geber in Runde {runde:d}")
def step_geber_then(context, spieler, runde):
    tatsaechlich = context.spiel.geber_in_runde(runde)
    assert tatsaechlich == spieler, (
        f"Runde {runde}: Erwartet '{spieler}' als Geber, aber erhalten: '{tatsaechlich}'"
    )


# ---------------------------------------------------------------------------
# And / Step (kontextneutral)
# ---------------------------------------------------------------------------

@step("keine abweichende Rundenzahl angegeben wird")
def step_standard_rundenzahl(context):
    context.rundenanzahl = None


@step("als Rundenzahl {rundenanzahl:d} angegeben wird")
def step_rundenzahl_angeben(context, rundenanzahl):
    context.rundenanzahl = rundenanzahl


@step('die Spielerreihenfolge bleibt als "{reihenfolge}" gespeichert')
def step_reihenfolge_gespeichert(context, reihenfolge):
    erwartet = _spieler_aus_string(reihenfolge)
    assert context.spiel.spieler_reihenfolge == erwartet, (
        f"Erwartet {erwartet}, aber erhalten: {context.spiel.spieler_reihenfolge}"
    )


@step("es wird ein Fehler zur ungültigen Spielerzahl angezeigt")
def step_fehler_spielerzahl(context):
    assert isinstance(context.fehler, UngueltigeSpielerzahl), (
        f"Erwartet UngueltigeSpielerzahl, aber erhalten: {type(context.fehler)}"
    )


@step("es wird ein Fehler angezeigt, dass die Rundenzahl ein Vielfaches von 4 sein muss")
def step_fehler_rundenzahl(context):
    assert isinstance(context.fehler, UngueltigeRundenanzahl), (
        f"Erwartet UngueltigeRundenanzahl, aber erhalten: {type(context.fehler)}"
    )


@step("{spieler} ist Geber in Runde {runde:d}")
def step_geber_step(context, spieler, runde):
    tatsaechlich = context.spiel.geber_in_runde(runde)
    assert tatsaechlich == spieler, (
        f"Runde {runde}: Erwartet '{spieler}' als Geber, aber erhalten: '{tatsaechlich}'"
    )


@step("{spieler} ist erneut Geber in Runde {runde:d}")
def step_geber_erneut_step(context, spieler, runde):
    tatsaechlich = context.spiel.geber_in_runde(runde)
    assert tatsaechlich == spieler, (
        f"Runde {runde}: Erwartet '{spieler}' erneut als Geber, aber erhalten: '{tatsaechlich}'"
    )
