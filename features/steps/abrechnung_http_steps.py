"""
Step-Definitionen für „Abrechnung bei Spielende" (HTTP, Blackbox, rule-set-v1.md §20).

Die API liefert die Beträge in **ganzen Cent** (``zu_zahlen_cent`` in der Rundenhistorie);
das Euro-Format steht hier nur als Test-Orakel, damit die Szenarien lesbar bleiben.

Die Given-/When-Schritte „ein neues Spiel mit der Spielerreihenfolge …", „eine reguläre
Runde mit Spielmacher … gespielt wird" und „… einen Tausender verliert" stammen aus
tausender_ausser_konkurrenz_http_steps.py bzw. runde_rollen_je_spielerzahl_http_steps.py.
"""
from behave import when, then

from steps.http_helfer import aktive_spieler, post


def _euro(cent: int) -> str:
    """Test-Orakel zum Darstellungsformat: deutsches Format, zwei Nachkommastellen, Euro-Zeichen."""
    return f"{cent // 100},{cent % 100:02d} €"


def _zu_zahlen_cent(context) -> dict[str, int]:
    antwort = context.client.get(f"/api/spiele/{context.ak_spiel_id}/runden/")
    assert antwort.status_code == 200, antwort.content
    return antwort.json()["zu_zahlen_cent"]


@when("{spielmacher} bei Geber {geber} einfach abgeht und die Gegenspieler je 40 Meldepunkte haben")
def step_einfaches_abgehen(context, spielmacher, geber):
    gegenspieler = [n for n in aktive_spieler(context.ak_spieler, geber) if n != spielmacher]
    antwort = post(context, f"/api/spiele/{context.ak_spiel_id}/runden/", {
        "typ": "einfaches_abgehen",
        "spielmacher": spielmacher,
        "geber": geber,
        "reizwert": 150,
        "gegenspieler": [{"name": name, "meldepunkte": 40} for name in gegenspieler],
    })
    assert antwort.status_code == 201, antwort.content


@then('zahlen die Spieler "{erwartet}"')
def step_zahlen(context, erwartet):
    """Erwartet 'Name Betrag; Name Betrag; …' – Reihenfolge egal, Beträge im Euro-Format."""
    soll = {}
    for teil in erwartet.split(";"):
        name, betrag = teil.strip().split(" ", 1)
        soll[name] = betrag
    cent = _zu_zahlen_cent(context)
    ist = {name: _euro(wert) for name, wert in cent.items()}
    assert ist == soll, f"Erwartet {soll}, aber erhalten: {ist} (Cent: {cent})"
