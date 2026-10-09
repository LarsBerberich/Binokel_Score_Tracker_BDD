"""
Gemeinsame Hilfen der HTTP-Blackbox-Steps (ADR-006) – enthält selbst keine Steps.

Die Szenarien laufen für 3 **und** 4 Spieler (ADR-017). Damit die Steps nicht je Variante
dupliziert werden, leiten sie die Rollen einer Runde aus der Spielerreihenfolge ab.

Wichtig: Die Rollenregel (``aktive_spieler``) ist hier bewusst **unabhängig** von der
Domänenfunktion formuliert, die in den Szenarien geprüft wird. Sie ist das Test-Orakel
und gibt rule-set-v1.md §3.4 wieder:

- 4 Spieler: der Geber setzt aus, aktiv sind die drei übrigen.
- 3 Spieler: der Geber spielt mit, aktiv sind alle drei.
"""
import json


def spieler_aus_string(reihenfolge: str) -> list[str]:
    """Parst 'Anna, Bernd, Carla' in ['Anna', 'Bernd', 'Carla']."""
    return [name.strip() for name in reihenfolge.split(",")]


def post(context, url: str, payload: dict):
    return context.client.post(
        url, data=json.dumps(payload), content_type="application/json"
    )


def put(context, url: str, payload: dict):
    return context.client.put(
        url, data=json.dumps(payload), content_type="application/json"
    )


def aktive_spieler(spieler: list[str], geber: str) -> list[str]:
    """Aktive Spieler einer Runde (Test-Orakel zu rule-set-v1.md §3.4)."""
    if len(spieler) == 4:
        return [name for name in spieler if name != geber]
    return list(spieler)


def geber_nach(spieler: list[str], gezaehlte_runden_davor: int) -> str:
    """Geber der nächsten gezählten Runde: streng reihum (rule-set-v1.md §3.3)."""
    return spieler[gezaehlte_runden_davor % len(spieler)]


def rollen(spieler: list[str], geber: str, spielmacher_index: int) -> tuple[str, list[str]]:
    """Spielmacher und die beiden Gegenspieler einer Runde.

    Der Spielmacher ist der ``spielmacher_index``-te **aktive** Spieler. Bei 3 Spielern ist
    der Geber selbst aktiv und damit — je nach Index — Spielmacher oder Gegenspieler; genau
    dieser Fall ist neu und soll durch die Szenarien erreicht werden.
    """
    aktive = aktive_spieler(spieler, geber)
    spielmacher = aktive[spielmacher_index]
    gegenspieler = [name for name in aktive if name != spielmacher]
    assert len(gegenspieler) == 2, (spieler, geber, aktive)
    return spielmacher, gegenspieler


def normale_runde(spielmacher: str, geber: str, gegenspieler: list[str]) -> dict:
    """Request-Body einer gewonnenen regulären Runde (Summe 250, alle Werte Zehner)."""
    gs1, gs2 = gegenspieler
    return {
        "typ": "normal",
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
    }


def spiel_anlegen(context, spieler: list[str], rundenanzahl: int) -> int:
    """Legt ein Spiel über die API an und gibt dessen id zurück."""
    antwort = post(context, "/api/spiele/", {"spieler": spieler, "rundenanzahl": rundenanzahl})
    assert antwort.status_code == 201, antwort.content
    return antwort.json()["id"]


def historie(context, spiel_id: int) -> list[dict]:
    return context.client.get(f"/api/spiele/{spiel_id}/runden/").json()["runden"]


def punktestaende(context, spiel_id: int) -> dict:
    return context.client.get(f"/api/spiele/{spiel_id}/punktestaende/").json()["punktestaende"]


def sterne(context, spiel_id: int) -> dict:
    return context.client.get(f"/api/spiele/{spiel_id}/punktestaende/").json()["sterne"]
