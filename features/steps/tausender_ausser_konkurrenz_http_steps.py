"""
Step-Definitionen für „Tausender laufen außer Konkurrenz" (HTTP, Blackbox, FND-006).

Prüft über die HTTP-API (ADR-006), dass ein Tausender eine eigene eindeutige
Sequenz erhält, aber keine gezählte Spielrunde (``zaehlrunde=None``): der Zähler
rückt erst durch eine reguläre Runde weiter, und der numerische Punktestand
friert bei einem Tausender ein (normativ: docs/rule-set-v1.md §15).
"""
import json

from behave import given, when, then


def _post(context, url: str, payload: dict):
    return context.client.post(
        url, data=json.dumps(payload), content_type="application/json"
    )


def _normale_runde(context, spielmacher: str, geber: str, gs1: str, gs2: str):
    """Eine gewonnene reguläre Runde (Summe 250, alle Werte Zehner)."""
    url = f"/api/spiele/{context.ak_spiel_id}/runden/"
    return _post(context, url, {
        "typ": "normal",
        "rundennummer": 1,  # wird serverseitig als Sequenz vergeben (ignoriert)
        "spielmacher": spielmacher,
        "geber": geber,
        "reizwert": 150,
        "meldepunkte": 150,
        "stichwerte": 100,
        "hat_eigenen_stich": True,
        "gegenspieler": [
            {"name": gs1, "meldepunkte": 0, "stichwerte": 90, "hat_eigenen_stich": True},
            {"name": gs2, "meldepunkte": 0, "stichwerte": 60, "hat_eigenen_stich": True},
        ],
    })


def _historie(context):
    return context.client.get(
        f"/api/spiele/{context.ak_spiel_id}/runden/"
    ).json()["runden"]


def _stand(context):
    return context.client.get(
        f"/api/spiele/{context.ak_spiel_id}/punktestaende/"
    ).json()["punktestaende"]


@given("ein neues Spiel mit 4 Runden ist angelegt")
def step_neues_spiel_4_runden(context):
    antwort = _post(context, "/api/spiele/", {
        "spieler": ["Anna", "Bernd", "Carla", "Dirk"],
        "rundenanzahl": 4,
    })
    assert antwort.status_code == 201, antwort.content
    context.ak_spiel_id = antwort.json()["id"]


@given("die erste reguläre Runde ist gespielt")
def step_erste_regulaere_runde(context):
    # Gezählte Runde 1: Geber Anna, Spielmacher Bernd, Gegenspieler Carla/Dirk.
    antwort = _normale_runde(context, "Bernd", "Anna", "Carla", "Dirk")
    assert antwort.status_code == 201, antwort.content
    context.ak_stand_vor_tausender = _stand(context)


@when("in derselben gezählten Runde ein Tausender ausgewertet wird")
def step_tausender_ausgewertet(context):
    url = f"/api/spiele/{context.ak_spiel_id}/runden/"
    # Gezählte Runde 2: Geber bleibt Bernd (Tausender verschiebt ihn nicht).
    antwort = _post(context, url, {
        "typ": "tausender_gewonnen",
        "rundennummer": 2,
        "spielmacher": "Carla",
        "geber": "Bernd",
    })
    assert antwort.status_code == 201, antwort.content


@then("trägt die Tausender-Runde keine gezählte Rundennummer")
def step_tausender_ohne_zaehlrunde(context):
    tausender = [r for r in _historie(context) if r["ist_tausender"]]
    assert len(tausender) == 1, _historie(context)
    assert tausender[0]["zaehlrunde"] is None, tausender[0]


@then("der numerische Punktestand ändert sich durch den Tausender nicht")
def step_stand_unveraendert(context):
    assert _stand(context) == context.ak_stand_vor_tausender, (
        context.ak_stand_vor_tausender, _stand(context)
    )


@then("die gezählte Rundennummer rückt erst durch die nächste reguläre Runde weiter")
def step_zaehler_rueckt_bei_regulaer(context):
    # Wiederholung der gezählten Runde 2: Geber weiterhin Bernd, Spielmacher Carla.
    antwort = _normale_runde(context, "Carla", "Bernd", "Anna", "Dirk")
    assert antwort.status_code == 201, antwort.content

    runden = _historie(context)
    assert [r["zaehlrunde"] for r in runden] == [1, None, 2], runden
    assert [r["ist_tausender"] for r in runden] == [False, True, False], runden
    assert [r["sequenz"] for r in runden] == [1, 2, 3], runden
