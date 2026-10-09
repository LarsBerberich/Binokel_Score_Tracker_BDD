"""
Step-Definitionen für den Endrunden-Gleichstand-Tiebreak (HTTP, Blackbox).

Ergänzt spielende_und_siegerermittlung.feature um ein HTTP-Szenario (ADR-006):
Der kumulierte STAND wird in Zehnern geführt (§9.1/§9.4); bei Gleichstand in
Zehnern entscheiden die exakten 1er-Stichwerte der letzten Runde per
`?exakte_stichwerte=`-Query (§9.3).

Läuft für 3 und 4 Spieler (ADR-017). Der Given-Step „ein neues Spiel mit der
Spielerreihenfolge … ist angelegt" stammt aus tausender_ausser_konkurrenz_http_steps.py.
Bei 3 Spielern ist der Geber der letzten Runde selbst Gegenspieler und nimmt am
1er-Tiebreak teil; bei 4 Spielern setzt er aus.
"""
from behave import given, when, then

from steps.http_helfer import geber_nach, post, punktestaende, rollen


@given("die letzte Runde führt zu einem Gleichstand in Zehnern zwischen {gs1} und {gs2}")
def step_gleichstand_in_zehnern(context, gs1, gs2):
    spieler = context.ak_spieler
    # Geber der letzten gezählten Runde (das Spiel hat context.ak_runden Runden).
    geber = geber_nach(spieler, context.ak_runden - 1)
    # Der erste aktive Spieler geht doppelt ab (M+S = 150 < Reizwert 200); alle Werte sind Zehner.
    # Gegenspieler: 20 + 80 + 30 = 130 und 30 + 70 + 30 = 130 → Gleichstand in Zehnern.
    spielmacher, gegenspieler = rollen(spieler, geber, spielmacher_index=0)
    assert set(gegenspieler) == {gs1, gs2}, (
        f"Die Gegenspieler der Runde sind {gegenspieler}, das Szenario nennt {gs1}, {gs2}"
    )
    antwort = post(context, f"/api/spiele/{context.ak_spiel_id}/runden/", {
        "typ": "normal",
        "spielmacher": spielmacher,
        "geber": geber,
        "reizwert": 200,
        "meldepunkte": 50,
        "stichwerte": 100,
        "hat_eigenen_stich": True,
        "gegenspieler": [
            {"name": gs1, "meldepunkte": 20, "stichwerte": 80, "hat_eigenen_stich": True},
            {"name": gs2, "meldepunkte": 30, "stichwerte": 70, "hat_eigenen_stich": True},
        ],
    })
    assert antwort.status_code == 201, antwort.content

    stand = punktestaende(context, context.ak_spiel_id)
    assert stand[gs1] == stand[gs2] == 130, stand


@when("der Sieger mit exakten 1er-Stichwerten {gs1} {wert1:d} und {gs2} {wert2:d} ermittelt wird")
def step_sieger_mit_exakten_1ern(context, gs1, wert1, gs2, wert2):
    antwort = context.client.get(
        f"/api/spiele/{context.ak_spiel_id}/sieger/",
        {"exakte_stichwerte": f"{gs1}:{wert1},{gs2}:{wert2}"},
    )
    assert antwort.status_code == 200, antwort.content
    context.tiebreak_sieger = antwort.json()["sieger"]


@then("ist {name} der alleinige Sieger des Spiels")
def step_alleiniger_sieger(context, name):
    assert context.tiebreak_sieger == [name], (
        f"Erwartet alleinigen Sieger [{name}], aber erhalten: {context.tiebreak_sieger}"
    )
