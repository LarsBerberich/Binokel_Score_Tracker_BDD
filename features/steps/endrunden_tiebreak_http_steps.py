"""
Step-Definitionen für den Endrunden-Gleichstand-Tiebreak (HTTP, Blackbox).

Ergänzt spielende_und_siegerermittlung.feature um ein HTTP-Szenario (ADR-006):
Der kumulierte STAND wird in Zehnern geführt (§9.1/§9.4); bei Gleichstand in
Zehnern entscheiden die exakten 1er-Stichwerte der letzten Runde per
`?exakte_stichwerte=`-Query (§9.3).
"""
import json

from behave import given, when, then


def _post(context, url: str, payload: dict):
    return context.client.post(
        url, data=json.dumps(payload), content_type="application/json"
    )


@given("ein neues Spiel für den Endrunden-Tiebreak ist angelegt")
def step_neues_spiel_tiebreak(context):
    antwort = _post(context, "/api/spiele/", {
        "spieler": ["Anna", "Bernd", "Carla", "Dirk"],
        "rundenanzahl": 4,
    })
    assert antwort.status_code == 201, antwort.content
    context.tiebreak_spiel_id = antwort.json()["id"]


@given("die letzte Runde führt zu einem Gleichstand in Zehnern zwischen Bernd und Carla")
def step_gleichstand_in_zehnern(context):
    url = f"/api/spiele/{context.tiebreak_spiel_id}/runden/"
    # Anna geht doppelt ab (M+S = 150 < Reizwert 200); alle Werte sind Zehner.
    # Bernd: 20 + 80 + 30 = 130, Carla: 30 + 70 + 30 = 130 → Gleichstand in Zehnern.
    antwort = _post(context, url, {
        "typ": "normal",
        "rundennummer": 1,
        "spielmacher": "Anna",
        "geber": "Dirk",
        "reizwert": 200,
        "meldepunkte": 50,
        "stichwerte": 100,
        "hat_eigenen_stich": True,
        "gegenspieler": [
            {"name": "Bernd", "meldepunkte": 20, "stichwerte": 80, "hat_eigenen_stich": True},
            {"name": "Carla", "meldepunkte": 30, "stichwerte": 70, "hat_eigenen_stich": True},
        ],
    })
    assert antwort.status_code == 201, antwort.content

    stand = context.client.get(
        f"/api/spiele/{context.tiebreak_spiel_id}/punktestaende/"
    ).json()["punktestaende"]
    assert stand["Bernd"] == stand["Carla"] == 130, stand


@when("der Sieger mit exakten 1er-Stichwerten Bernd {bernd:d} und Carla {carla:d} ermittelt wird")
def step_sieger_mit_exakten_1ern(context, bernd, carla):
    antwort = context.client.get(
        f"/api/spiele/{context.tiebreak_spiel_id}/sieger/",
        {"exakte_stichwerte": f"Bernd:{bernd},Carla:{carla}"},
    )
    assert antwort.status_code == 200, antwort.content
    context.tiebreak_sieger = antwort.json()["sieger"]


@then("ist Bernd der alleinige Sieger des Spiels")
def step_bernd_alleiniger_sieger(context):
    assert context.tiebreak_sieger == ["Bernd"], (
        f"Erwartet alleinigen Sieger [Bernd], aber erhalten: {context.tiebreak_sieger}"
    )
