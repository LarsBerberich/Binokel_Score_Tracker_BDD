"""
Step-Definitionen für „Rollen einer Runde je nach Spielerzahl" (HTTP, Blackbox, ADR-017).

Der Given-Step „ein neues Spiel mit der Spielerreihenfolge … ist angelegt" stammt aus
tausender_ausser_konkurrenz_http_steps.py und setzt ``ak_spieler`` / ``ak_spiel_id``.

Die Gegenspieler werden hier aus Spielmacher und Geber über das Test-Orakel
(http_helfer.aktive_spieler) abgeleitet: Bei 4 Spielern fällt der Geber heraus, bei
3 Spielern bleibt er – als Spielmacher oder als Gegenspieler – im Spiel.
"""
from behave import when, then

from steps.http_helfer import (
    aktive_spieler,
    historie,
    normale_runde,
    post,
    punktestaende,
    spieler_aus_string,
    sterne,
)


def _runden_url(context) -> str:
    return f"/api/spiele/{context.ak_spiel_id}/runden/"


def _gegenspieler(context, spielmacher: str, geber: str) -> list[str]:
    aktive = aktive_spieler(context.ak_spieler, geber)
    assert spielmacher in aktive, (
        f"{spielmacher} kann bei Geber {geber} nicht Spielmacher sein (aktiv: {aktive})"
    )
    return [name for name in aktive if name != spielmacher]


@when("{spielmacher} bei Geber {geber} einen Tausender verliert")
def step_tausender_verloren(context, spielmacher, geber):
    antwort = post(context, _runden_url(context), {
        "typ": "tausender_verloren",
        "spielmacher": spielmacher,
        "geber": geber,
    })
    assert antwort.status_code == 201, antwort.content


@then("erhalten genau {empfaenger} je einen Stern")
def step_sterne_genau(context, empfaenger):
    erwartet = set(spieler_aus_string(empfaenger))
    tatsaechlich = {name for name, anzahl in sterne(context, context.ak_spiel_id).items() if anzahl}
    assert tatsaechlich == erwartet, (
        f"Erwartet Sterne für {sorted(erwartet)}, aber erhalten: "
        f"{sterne(context, context.ak_spiel_id)}"
    )
    assert all(
        anzahl == 1
        for name, anzahl in sterne(context, context.ak_spiel_id).items()
        if name in erwartet
    )


@when("eine reguläre Runde mit Spielmacher {spielmacher} und Geber {geber} gespielt wird")
def step_regulaere_runde(context, spielmacher, geber):
    gegenspieler = _gegenspieler(context, spielmacher, geber)
    antwort = post(
        context, _runden_url(context), normale_runde(spielmacher, geber, gegenspieler)
    )
    assert antwort.status_code == 201, antwort.content


@then('hat {geber} in der Rundenhistorie die Rolle "{rolle}" und ist als Geber gekennzeichnet')
def step_rolle_des_gebers(context, geber, rolle):
    runde = historie(context, context.ak_spiel_id)[-1]
    eintrag = runde["spieler"][geber]
    assert eintrag["rolle"] == rolle, (
        f"Erwartet Rolle '{rolle}' für {geber}, aber erhalten: '{eintrag['rolle']}'"
    )
    assert eintrag["ist_geber"] is True, eintrag
    uebrige = [n for n, e in runde["spieler"].items() if n != geber]
    assert not any(runde["spieler"][n]["ist_geber"] for n in uebrige), runde["spieler"]


@then("hat {name} den Punktestand {punkte:d}")
def step_punktestand(context, name, punkte):
    stand = punktestaende(context, context.ak_spiel_id)
    assert stand[name] == punkte, f"Erwartet Punktestand {punkte} für {name}, erhalten: {stand}"
