"""
Step-Definitionen für „Tausender laufen außer Konkurrenz" (HTTP, Blackbox, FND-006).

Prüft über die HTTP-API (ADR-006), dass ein Tausender eine eigene eindeutige
Sequenz erhält, aber keine gezählte Spielrunde (``zaehlrunde=None``): der Zähler
rückt erst durch eine reguläre Runde weiter, und der numerische Punktestand
friert bei einem Tausender ein (normativ: docs/rule-set-v1.md §15).

Läuft für 3 und 4 Spieler (ADR-017); die Rollen leiten sich aus der Spielerreihenfolge
ab (siehe http_helfer.rollen). Bei 3 Spielern ist der Geber der ersten Runde selbst
Spielmacher.
"""
from behave import given, when, then

from steps.http_helfer import (
    geber_nach,
    historie,
    normale_runde,
    post,
    punktestaende,
    rollen,
    spiel_anlegen,
    spieler_aus_string,
)


def _runden_url(context) -> str:
    return f"/api/spiele/{context.ak_spiel_id}/runden/"


@given('ein neues Spiel mit der Spielerreihenfolge "{reihenfolge}" und {runden:d} Runden ist angelegt')
def step_neues_spiel(context, reihenfolge, runden):
    context.ak_spieler = spieler_aus_string(reihenfolge)
    context.ak_runden = runden
    context.ak_spiel_id = spiel_anlegen(context, context.ak_spieler, runden)


@given("die erste reguläre Runde ist gespielt")
def step_erste_regulaere_runde(context):
    # Gezählte Runde 1: Geber ist der erste Spieler, Spielmacher der erste aktive Spieler.
    geber = geber_nach(context.ak_spieler, 0)
    spielmacher, gegenspieler = rollen(context.ak_spieler, geber, spielmacher_index=0)
    antwort = post(context, _runden_url(context), normale_runde(spielmacher, geber, gegenspieler))
    assert antwort.status_code == 201, antwort.content
    context.ak_stand_vor_tausender = punktestaende(context, context.ak_spiel_id)


@when("in derselben gezählten Runde ein Tausender ausgewertet wird")
def step_tausender_ausgewertet(context):
    # Gezählte Runde 2: der Geber rückt einmal weiter und bleibt dann über den Tausender stehen.
    geber = geber_nach(context.ak_spieler, 1)
    spielmacher, _ = rollen(context.ak_spieler, geber, spielmacher_index=1)
    antwort = post(context, _runden_url(context), {
        "typ": "tausender_gewonnen",
        "spielmacher": spielmacher,
        "geber": geber,
    })
    assert antwort.status_code == 201, antwort.content


@then("trägt die Tausender-Runde keine gezählte Rundennummer")
def step_tausender_ohne_zaehlrunde(context):
    runden = historie(context, context.ak_spiel_id)
    tausender = [r for r in runden if r["ist_tausender"]]
    assert len(tausender) == 1, runden
    assert tausender[0]["zaehlrunde"] is None, tausender[0]


@then("der numerische Punktestand ändert sich durch den Tausender nicht")
def step_stand_unveraendert(context):
    stand = punktestaende(context, context.ak_spiel_id)
    assert stand == context.ak_stand_vor_tausender, (context.ak_stand_vor_tausender, stand)


@then("die gezählte Rundennummer rückt erst durch die nächste reguläre Runde weiter")
def step_zaehler_rueckt_bei_regulaer(context):
    # Wiederholung der gezählten Runde 2: derselbe Geber, derselbe Spielmacher.
    geber = geber_nach(context.ak_spieler, 1)
    spielmacher, gegenspieler = rollen(context.ak_spieler, geber, spielmacher_index=1)
    antwort = post(context, _runden_url(context), normale_runde(spielmacher, geber, gegenspieler))
    assert antwort.status_code == 201, antwort.content

    runden = historie(context, context.ak_spiel_id)
    assert [r["zaehlrunde"] for r in runden] == [1, None, 2], runden
    assert [r["ist_tausender"] for r in runden] == [False, True, False], runden
    assert [r["sequenz"] for r in runden] == [1, 2, 3], runden
    # Der Geber bleibt über den Tausender hinweg derselbe (FND-006, §15.6).
    assert [r["geber"] for r in runden][1:] == [geber, geber], runden
