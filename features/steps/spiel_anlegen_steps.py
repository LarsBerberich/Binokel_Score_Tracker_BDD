"""
Step-Definitionen für: spiel_anlegen.feature
Slice 1 — HTTP-Blackbox-Migration (ADR-006).

Alle Spieloperationen laufen über die REST-API (POST /api/spiele/).
Domänenobjekt `Spiel` wird aus der API-Antwort rekonstruiert, damit
die reine Berechnungslogik (geber_in_runde) weiterhin getestet werden kann.
"""
import json

from behave import given, when, then, step

from scoring.domain import Spiel


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _spieler_aus_string(reihenfolge: str) -> list[str]:
    """Parst 'Anna, Bernd, Carla, Dirk' in ['Anna', 'Bernd', 'Carla', 'Dirk']."""
    return [s.strip() for s in reihenfolge.split(",")]


def _post_json(context, url: str, payload: dict):
    """Sendet eine JSON-POST-Anfrage über den Test-HTTP-Client."""
    return context.client.post(
        url,
        data=json.dumps(payload),
        content_type="application/json",
    )


def _spiel_anlegen_http(context, spieler: list[str], rundenanzahl: int | None = None):
    """POST /api/spiele/ und context.spiel + context.spiel_id setzen."""
    payload: dict = {"spieler": spieler}
    if rundenanzahl is not None:
        payload["rundenanzahl"] = rundenanzahl
    antwort = _post_json(context, "/api/spiele/", payload)
    assert antwort.status_code == 201, (
        f"Erwartet HTTP 201, aber erhalten: {antwort.status_code} — {antwort.content}"
    )
    daten = antwort.json()
    context.spiel_id = daten["id"]
    # Domänenobjekt aus API-Antwort rekonstruieren (für geber_in_runde)
    context.spiel = Spiel(
        spieler_reihenfolge=daten["spieler"],
        rundenanzahl=daten["rundenanzahl"],
    )
    return antwort


# ---------------------------------------------------------------------------
# Given
# ---------------------------------------------------------------------------

@given("es wird ein neues V1-Spiel angelegt")
def step_neues_spiel(context):
    context.spieler = None
    context.rundenanzahl = None
    context.spiel = None
    context.spiel_id = None
    context.antwort = None
    context.fehler = None


@given('das Spiel wurde mit der Spielerreihenfolge "{reihenfolge}" angelegt')
def step_spiel_mit_reihenfolge(context, reihenfolge):
    _spiel_anlegen_http(context, _spieler_aus_string(reihenfolge))


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
    antwort = _spiel_anlegen_http(context, context.spieler, context.rundenanzahl)
    daten = antwort.json()
    assert daten["rundenanzahl"] == rundenanzahl, (
        f"Erwartet {rundenanzahl} Runden, aber erhalten: {daten['rundenanzahl']}"
    )


@then("wird das Spiel nicht angelegt")
def step_spiel_nicht_angelegt(context):
    payload: dict = {"spieler": context.spieler}
    if context.rundenanzahl is not None:
        payload["rundenanzahl"] = context.rundenanzahl
    antwort = _post_json(context, "/api/spiele/", payload)
    assert antwort.status_code == 400, (
        f"Erwartet HTTP 400, aber erhalten: {antwort.status_code}"
    )
    context.antwort = antwort


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
    daten = context.antwort.json()
    assert "fehler" in daten, f"Kein 'fehler'-Feld im Response: {daten}"
    nachricht = daten["fehler"].lower()
    assert "spieler" in nachricht or "4" in nachricht, (
        f"Unerwartete Fehlermeldung: {daten['fehler']}"
    )


@step("es wird ein Fehler angezeigt, dass die Rundenzahl ein Vielfaches von 4 sein muss")
def step_fehler_rundenzahl(context):
    daten = context.antwort.json()
    assert "fehler" in daten, f"Kein 'fehler'-Feld im Response: {daten}"
    nachricht = daten["fehler"].lower()
    assert "vielfaches" in nachricht or "4" in nachricht, (
        f"Unerwartete Fehlermeldung: {daten['fehler']}"
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
