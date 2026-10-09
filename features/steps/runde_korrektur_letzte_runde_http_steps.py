"""
Step-Definitionen für die Korrektur der letzten Runde (HTTP, Blackbox).

Deckt runde_korrektur_letzte_runde.feature ab (TASK-014, ADR-015): Nur die
höchste (zuletzt erfasste) Rundennummer ist per PUT editierbar. Eine Korrektur
aktualisiert den kumulierten STAND; eine frühere Runde wird abgelehnt (409).

Läuft für 3 und 4 Spieler (ADR-017). Der Given-Step „ein neues Spiel mit der
Spielerreihenfolge … ist angelegt" stammt aus tausender_ausser_konkurrenz_http_steps.py
und setzt ``ak_spieler`` / ``ak_spiel_id``. Bei 3 Spielern ist der Geber der ersten
Runde selbst Spielmacher – die Korrektur muss das akzeptieren.
"""
from behave import given, when, then

from steps.http_helfer import (
    geber_nach,
    normale_runde,
    post,
    punktestaende,
    put,
    rollen,
)


def _runden_url(context) -> str:
    return f"/api/spiele/{context.ak_spiel_id}/runden/"


def _runde_1_erfassen(context) -> None:
    """Runde 1: Spielmacher gewinnt mit 210 (Reizwert 200, M 110 + S 100)."""
    geber = geber_nach(context.ak_spieler, 0)
    spielmacher, (gs1, gs2) = rollen(context.ak_spieler, geber, spielmacher_index=0)
    context.korrektur_spielmacher = spielmacher
    context.korrektur_gegenspieler = (gs1, gs2)
    antwort = post(context, _runden_url(context), {
        "typ": "normal", "spielmacher": spielmacher, "geber": geber,
        "reizwert": 200, "meldepunkte": 110, "stichwerte": 100, "hat_eigenen_stich": True,
        "gegenspieler": [
            {"name": gs1, "meldepunkte": 20, "stichwerte": 90, "hat_eigenen_stich": True},
            {"name": gs2, "meldepunkte": 0, "stichwerte": 60, "hat_eigenen_stich": True},
        ],
    })
    assert antwort.status_code == 201, antwort.content


@given("eine reguläre Runde ist für die Korrektur erfasst")
def step_eine_runde(context):
    _runde_1_erfassen(context)


@given("zwei reguläre Runden sind für die Korrektur erfasst")
def step_zwei_runden(context):
    _runde_1_erfassen(context)
    # Runde 2: der Geber rückt eine Position weiter; einfaches Abgehen des zweiten aktiven Spielers.
    geber = geber_nach(context.ak_spieler, 1)
    spielmacher, (gs1, gs2) = rollen(context.ak_spieler, geber, spielmacher_index=1)
    antwort = post(context, _runden_url(context), {
        "typ": "einfaches_abgehen", "spielmacher": spielmacher, "geber": geber,
        "reizwert": 250,
        "gegenspieler": [
            {"name": gs1, "meldepunkte": 40},
            {"name": gs2, "meldepunkte": 20},
        ],
    })
    assert antwort.status_code == 201, antwort.content


@when("die letzte Runde mit einem höheren Spielmacher-Ergebnis korrigiert wird")
def step_letzte_runde_korrigieren(context):
    gs1, gs2 = context.korrektur_gegenspieler
    # Korrektur: Meldepunkte 110 → 150 (Spielmacher-Punkte damit 250 statt 210).
    context.korrektur_antwort = put(context, f"{_runden_url(context)}1/", {
        "typ": "normal", "spielmacher": context.korrektur_spielmacher,
        "reizwert": 200, "meldepunkte": 150, "stichwerte": 100, "hat_eigenen_stich": True,
        "gegenspieler": [
            {"name": gs1, "meldepunkte": 20, "stichwerte": 80, "hat_eigenen_stich": True},
            {"name": gs2, "meldepunkte": 0, "stichwerte": 70, "hat_eigenen_stich": True},
        ],
    })


@when("versucht wird, die erste Runde zu korrigieren")
def step_erste_runde_korrigieren(context):
    context.korrektur_antwort = put(context, f"{_runden_url(context)}1/", {
        "typ": "tausender_gewonnen", "spielmacher": context.korrektur_spielmacher,
    })


@then("wird die Korrektur übernommen")
def step_korrektur_uebernommen(context):
    assert context.korrektur_antwort.status_code == 200, context.korrektur_antwort.content


@then("der kumulierte STAND des Spielmachers beträgt {erwartet:d}")
def step_stand_pruefen(context, erwartet):
    stand = punktestaende(context, context.ak_spiel_id)
    name = context.korrektur_spielmacher
    assert stand[name] == erwartet, (
        f"Erwartet STAND von {name} = {erwartet}, aber erhalten: {stand[name]}"
    )


@then("wird die Korrektur abgelehnt")
def step_korrektur_abgelehnt(context):
    assert context.korrektur_antwort.status_code == 409, (
        f"Erwartet 409 Conflict, aber erhalten: {context.korrektur_antwort.status_code} "
        f"({context.korrektur_antwort.content})"
    )
