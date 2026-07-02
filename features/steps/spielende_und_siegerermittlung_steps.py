"""
Step-Definitionen für: spielende_und_siegerermittlung.feature
Slice 6 — setzt alle vorigen Slices voraus, Abschluss des Spiels.
"""
from behave import given, when, then, step

from scoring.use_cases import sieger_ermitteln


# ---------------------------------------------------------------------------
# Given
# ---------------------------------------------------------------------------

@given("die letzte Runde ist ausgewertet")
def step_letzte_runde_ausgewertet(context):
    context.punktestaende = {}
    context.sterne = {}
    context.exakte_stichwerte = None
    context.sieger = []


@given("in der letzten Runde ist ein Gleichstand um den Gesamtsieg möglich")
def step_gleichstand_moeglich(context):
    context.punktestaende = {"Anna": 600, "Bernd": 600}
    context.exakte_stichwerte = {"Anna": 12, "Bernd": 7}
    context.sieger = []


# ---------------------------------------------------------------------------
# When
# ---------------------------------------------------------------------------

@when("das Spiel abgeschlossen wird")
def step_spiel_abschliessen(context):
    exakte = getattr(context, "exakte_stichwerte", None)
    context.sieger = sieger_ermitteln(context.punktestaende, exakte)


# ---------------------------------------------------------------------------
# Then
# ---------------------------------------------------------------------------

@then("ist {spieler} alleiniger Sieger")
def step_alleiniger_sieger(context, spieler):
    assert context.sieger == [spieler], (
        f"Erwartet alleinigen Sieger [{spieler}], aber erhalten: {context.sieger}"
    )


@then("wird der Gesamtsieg nicht über die Sterne entschieden")
def step_kein_sieg_durch_sterne(context):
    assert "Bernd" in context.sieger, (
        "Bernd sollte Sieger sein, obwohl Anna mehr Sterne hat (Sterne zählen nicht)."
    )
    assert "Anna" in context.sieger, (
        "Anna sollte ebenfalls Sieger sein (gleicher Punktestand)."
    )


@then("wird die Siegerermittlung mit den exakten 1er-Werten durchgeführt")
def step_siegerermittlung_exakt(context):
    assert len(context.sieger) == 1, (
        f"Erwartet genau einen Sieger durch exakte Werte, aber erhalten: {context.sieger}"
    )
    assert context.sieger == ["Anna"], (
        f"Erwartet Anna als Sieger (höherer exakter Wert), aber erhalten: {context.sieger}"
    )


@then("gibt es mehrere Sieger")
def step_mehrere_sieger(context):
    assert len(context.sieger) > 1, (
        f"Erwartet mehrere Sieger, aber erhalten: {context.sieger}"
    )


# ---------------------------------------------------------------------------
# And / Step (kontextneutral)
# ---------------------------------------------------------------------------

@step("die Punktestände sind Anna {anna:d}, Bernd {bernd:d}, Carla {carla:d} und Dirk {dirk:d}")
def step_punktestaende(context, anna, bernd, carla, dirk):
    context.punktestaende = {"Anna": anna, "Bernd": bernd, "Carla": carla, "Dirk": dirk}


@step("Anna und Bernd haben denselben numerischen Punktestand")
def step_gleicher_punktestand(context):
    context.punktestaende = {"Anna": 600, "Bernd": 600, "Carla": 400, "Dirk": 200}
    context.sterne = {"Anna": 2, "Bernd": 0, "Carla": 0, "Dirk": 0}
    context.exakte_stichwerte = None


@step("Anna hat mehr Sterne aus Tausender-Runden als Bernd")
def step_mehr_sterne(context):
    assert context.sterne.get("Anna", 0) > context.sterne.get("Bernd", 0), (
        "Vorbedingung nicht erfüllt: Anna hat nicht mehr Sterne als Bernd."
    )


@step("für die betroffenen Spieler liegen exakte 1er-Stichwerte vor")
def step_exakte_stichwerte_vorhanden(context):
    assert context.exakte_stichwerte is not None, (
        "Vorbedingung nicht erfüllt: Keine exakten Stichwerte vorhanden."
    )


@step("nach Berücksichtigung exakter 1er-Werte besteht weiterhin Gleichstand")
def step_gleichstand_bleibt(context):
    context.punktestaende = {"Anna": 600, "Bernd": 600}
    context.exakte_stichwerte = {"Anna": 10, "Bernd": 10}
