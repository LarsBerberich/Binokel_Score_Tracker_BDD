"""
Step-Definitionen für die Korrektur der letzten Runde (HTTP, Blackbox).

Deckt runde_korrektur_letzte_runde.feature ab (TASK-014, ADR-015): Nur die
höchste (zuletzt erfasste) Rundennummer ist per PUT editierbar. Eine Korrektur
aktualisiert den kumulierten STAND; eine frühere Runde wird abgelehnt (409).

Geberrotation (Spieler Anna,Bernd,Clara,Dieter): Runde 1→Anna, 2→Bernd.
"""
import json

from behave import given, when, then


def _post(context, url: str, payload: dict):
    return context.client.post(
        url, data=json.dumps(payload), content_type="application/json"
    )


def _put(context, url: str, payload: dict):
    return context.client.put(
        url, data=json.dumps(payload), content_type="application/json"
    )


def _neues_spiel(context) -> int:
    antwort = _post(context, "/api/spiele/", {
        "spieler": ["Anna", "Bernd", "Clara", "Dieter"],
        "rundenanzahl": 4,
    })
    assert antwort.status_code == 201, antwort.content
    return antwort.json()["id"]


@given("ein neues Spiel mit einer erfassten Runde für die Korrektur ist angelegt")
def step_spiel_mit_einer_runde(context):
    context.korrektur_spiel_id = _neues_spiel(context)
    url = f"/api/spiele/{context.korrektur_spiel_id}/runden/"
    # Runde 1: Geber Anna (deterministisch), Spielmacher Bernd gewinnt mit 210.
    antwort = _post(context, url, {
        "typ": "normal", "rundennummer": 1, "spielmacher": "Bernd", "geber": "Anna",
        "reizwert": 200, "meldepunkte": 110, "stichwerte": 100, "hat_eigenen_stich": True,
        "gegenspieler": [
            {"name": "Clara", "meldepunkte": 20, "stichwerte": 90, "hat_eigenen_stich": True},
            {"name": "Dieter", "meldepunkte": 0, "stichwerte": 60, "hat_eigenen_stich": True},
        ],
    })
    assert antwort.status_code == 201, antwort.content


@given("ein neues Spiel mit zwei erfassten Runden für die Korrektur ist angelegt")
def step_spiel_mit_zwei_runden(context):
    context.korrektur_spiel_id = _neues_spiel(context)
    url = f"/api/spiele/{context.korrektur_spiel_id}/runden/"
    r1 = _post(context, url, {
        "typ": "normal", "rundennummer": 1, "spielmacher": "Bernd", "geber": "Anna",
        "reizwert": 200, "meldepunkte": 110, "stichwerte": 100, "hat_eigenen_stich": True,
        "gegenspieler": [
            {"name": "Clara", "meldepunkte": 20, "stichwerte": 90, "hat_eigenen_stich": True},
            {"name": "Dieter", "meldepunkte": 0, "stichwerte": 60, "hat_eigenen_stich": True},
        ],
    })
    assert r1.status_code == 201, r1.content
    # Runde 2: Geber Bernd (deterministisch), Spielmacher Clara.
    r2 = _post(context, url, {
        "typ": "einfaches_abgehen", "rundennummer": 2, "spielmacher": "Clara", "geber": "Bernd",
        "reizwert": 250,
        "gegenspieler": [
            {"name": "Anna", "meldepunkte": 40},
            {"name": "Dieter", "meldepunkte": 20},
        ],
    })
    assert r2.status_code == 201, r2.content


@when("die letzte Runde mit einem höheren Spielmacher-Ergebnis korrigiert wird")
def step_letzte_runde_korrigieren(context):
    url = f"/api/spiele/{context.korrektur_spiel_id}/runden/1/"
    # Korrektur: Meldepunkte 110 → 150 (Spielmacher-Punkte damit 250 statt 210).
    context.korrektur_antwort = _put(context, url, {
        "typ": "normal", "spielmacher": "Bernd",
        "reizwert": 200, "meldepunkte": 150, "stichwerte": 100, "hat_eigenen_stich": True,
        "gegenspieler": [
            {"name": "Clara", "meldepunkte": 20, "stichwerte": 80, "hat_eigenen_stich": True},
            {"name": "Dieter", "meldepunkte": 0, "stichwerte": 70, "hat_eigenen_stich": True},
        ],
    })


@when("versucht wird, die erste Runde zu korrigieren")
def step_erste_runde_korrigieren(context):
    url = f"/api/spiele/{context.korrektur_spiel_id}/runden/1/"
    context.korrektur_antwort = _put(context, url, {
        "typ": "tausender_gewonnen", "spielmacher": "Bernd",
    })


@then("wird die Korrektur übernommen")
def step_korrektur_uebernommen(context):
    assert context.korrektur_antwort.status_code == 200, context.korrektur_antwort.content


@then("der kumulierte STAND des Spielmachers beträgt {erwartet:d}")
def step_stand_pruefen(context, erwartet):
    stand = context.client.get(
        f"/api/spiele/{context.korrektur_spiel_id}/punktestaende/"
    ).json()["punktestaende"]
    assert stand["Bernd"] == erwartet, (
        f"Erwartet STAND von Bernd = {erwartet}, aber erhalten: {stand['Bernd']}"
    )


@then("wird die Korrektur abgelehnt")
def step_korrektur_abgelehnt(context):
    assert context.korrektur_antwort.status_code == 409, (
        f"Erwartet 409 Conflict, aber erhalten: {context.korrektur_antwort.status_code} "
        f"({context.korrektur_antwort.content})"
    )
