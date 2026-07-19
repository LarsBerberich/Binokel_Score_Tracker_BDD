"""
HTTP-Schicht für den Binokel Score Tracker – V1.

Funktion-basierte Views mit Django JsonResponse (kein DRF, siehe ADR-005).

Aufrufmuster pro View:
    1. HTTP-Methode und JSON-Body validieren
    2. Use Case aufrufen  → Domänenlogik
    3. Repository aufrufen → DB-Persistenz / DB-Lesen
    4. JsonResponse zurückgeben

Normative Quelle: docs/rule-set-v1.md, BACKLOG.md TASK-004.
"""
from __future__ import annotations

import json

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from scoring.domain import (
    Rundenausgang,
    UngueltigeRundenanzahl,
    UngueltigeStichwerte,
    UngueltigeSpielerzahl,
)
from scoring.repositories import (
    punktestaende_laden,
    runde_persistieren,
    spiel_laden,
    spiel_persistieren,
)
from scoring.use_cases import (
    doppeltes_abgehen_auswerten,
    einfaches_abgehen_auswerten,
    meldepunkte_mit_stich_zwang,
    normales_spiel_auswerten,
    sieger_ermitteln,
    spiel_anlegen,
)


# ── Hilfsfunktionen ────────────────────────────────────────────────────────────

def _json_body(request) -> dict:
    """Parst den JSON-Request-Body. Wirft ValueError bei ungültigem JSON."""
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("Ungültiger JSON-Body.") from exc


def _fehler(nachricht: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"fehler": nachricht}, status=status)


def _validierungsfehler_nachricht(exc: Exception) -> str:
    if isinstance(exc, UngueltigeSpielerzahl):
        return "Ungültige Spielerzahl: Es müssen genau 4 Spieler angegeben werden."
    if isinstance(exc, UngueltigeRundenanzahl):
        return "Ungültige Rundenzahl: Die Rundenzahl muss ein Vielfaches von 4 sein."
    if isinstance(exc, UngueltigeStichwerte):
        return "Ungültige Stichwerte."
    return "Ungültige Eingabedaten."


def _pflichtfeld(body: dict, *felder: str) -> str | None:
    """Gibt den Namen des ersten fehlenden Pflichtfelds zurück, oder None."""
    for feld in felder:
        if feld not in body:
            return feld
    return None


# ── Slice 1: Spiel anlegen / laden ────────────────────────────────────────────

@csrf_exempt
def spiele_view(request) -> JsonResponse:
    """POST /api/spiele/ — Neues Spiel anlegen."""
    if request.method != "POST":
        return _fehler("Nur POST erlaubt.", status=405)

    try:
        body = _json_body(request)
    except ValueError:
        return _fehler("Ungültiger JSON-Body.")

    fehlendes = _pflichtfeld(body, "spieler")
    if fehlendes:
        return _fehler(f"Pflichtfeld fehlt: '{fehlendes}'.")

    try:
        spiel = spiel_anlegen(
            spieler=body["spieler"],
            rundenanzahl=body.get("rundenanzahl"),
        )
    except (UngueltigeSpielerzahl, UngueltigeRundenanzahl) as exc:
        return _fehler(_validierungsfehler_nachricht(exc))

    spiel_model = spiel_persistieren(spiel)

    return JsonResponse(
        {
            "id": spiel_model.pk,
            "rundenanzahl": spiel_model.rundenanzahl,
            "spieler": spiel.spieler_reihenfolge,
        },
        status=201,
    )


@require_GET
def spiel_detail_view(request, spiel_id: int) -> JsonResponse:
    """GET /api/spiele/{id}/ — Spiel laden."""
    try:
        spiel = spiel_laden(spiel_id)
    except ObjectDoesNotExist:
        return _fehler(f"Spiel {spiel_id} nicht gefunden.", status=404)

    return JsonResponse(
        {
            "id": spiel_id,
            "rundenanzahl": spiel.rundenanzahl,
            "spieler": spiel.spieler_reihenfolge,
        }
    )


# ── Slices 2–5: Runde auswerten und persistieren ──────────────────────────────

@csrf_exempt
def runden_view(request, spiel_id: int) -> JsonResponse:
    """POST /api/spiele/{id}/runden/ — Runde auswerten und speichern.

    Body-Felder (alle Typen):
        typ          : "normal" | "einfaches_abgehen" | "doppeltes_abgehen"
                       | "tausender_gewonnen" | "tausender_verloren"
        rundennummer : int (1-basiert)
        spielmacher  : str
        geber        : str

    Zusatzfelder für typ "normal" und "doppeltes_abgehen":
        reizwert, meldepunkte, stichwerte, hat_eigenen_stich : Spielmacher
        gegenspieler : [{name, meldepunkte, stichwerte, hat_eigenen_stich}]

    Zusatzfelder für typ "einfaches_abgehen":
        reizwert
        gegenspieler : [{name, meldepunkte}]   (kein Stich-Zwang, stichwerte = 0)

    Sterne (optional, Default false):
        spielmacher_stern, gegenspieler_stern
    """
    if request.method != "POST":
        return _fehler("Nur POST erlaubt.", status=405)

    try:
        body = _json_body(request)
    except ValueError:
        return _fehler("Ungültiger JSON-Body.")

    fehlendes = _pflichtfeld(body, "typ", "rundennummer", "spielmacher", "geber")
    if fehlendes:
        return _fehler(f"Pflichtfeld fehlt: '{fehlendes}'.")

    typ: str = body["typ"]
    rundennummer: int = body["rundennummer"]
    spielmacher_name: str = body["spielmacher"]
    geber_name: str = body["geber"]
    spielmacher_stern: bool = body.get("spielmacher_stern", False)
    gegenspieler_stern: bool = body.get("gegenspieler_stern", False)

    # ── Dispatch nach Rundentyp ────────────────────────────────────────────────

    if typ == "normal":
        fehlendes = _pflichtfeld(body, "reizwert", "meldepunkte", "stichwerte",
                                 "hat_eigenen_stich", "gegenspieler")
        if fehlendes:
            return _fehler(f"Pflichtfeld fehlt für typ 'normal': '{fehlendes}'.")

        sm_melde = meldepunkte_mit_stich_zwang(
            body["meldepunkte"], body["hat_eigenen_stich"]
        )
        ausgang, gesamtpunkte = normales_spiel_auswerten(
            body["reizwert"], sm_melde, body["stichwerte"]
        )

        if ausgang == Rundenausgang.GEWONNENES_SPIEL:
            spielmacher_punkte = gesamtpunkte
            verlustwert = 0
            mitpunkte = 0
        else:  # doppeltes Abgehen
            spielmacher_punkte = 0
            verlustwert, _ = doppeltes_abgehen_auswerten(body["reizwert"])
            mitpunkte = 30

        gegenspieler_daten = [
            {
                "name": gs["name"],
                "meldepunkte": meldepunkte_mit_stich_zwang(
                    gs["meldepunkte"], gs["hat_eigenen_stich"]
                ),
                "stichwerte": gs["stichwerte"],
                "hat_eigenen_stich": gs["hat_eigenen_stich"],
            }
            for gs in body["gegenspieler"]
        ]

    elif typ == "einfaches_abgehen":
        fehlendes = _pflichtfeld(body, "reizwert", "gegenspieler")
        if fehlendes:
            return _fehler(f"Pflichtfeld fehlt für typ 'einfaches_abgehen': '{fehlendes}'.")

        ausgang = Rundenausgang.EINFACHES_ABGEHEN
        spielmacher_punkte = 0
        verlustwert, _ = einfaches_abgehen_auswerten(body["reizwert"])
        mitpunkte = 30

        # Kein Stich-Zwang für Gegenspieler (normativ: rule-set-v1.md §13.4)
        gegenspieler_daten = [
            {
                "name": gs["name"],
                "meldepunkte": gs["meldepunkte"],
                "stichwerte": 0,
                "hat_eigenen_stich": gs.get("hat_eigenen_stich", False),
            }
            for gs in body["gegenspieler"]
        ]

    elif typ == "doppeltes_abgehen":
        fehlendes = _pflichtfeld(body, "reizwert", "gegenspieler")
        if fehlendes:
            return _fehler(f"Pflichtfeld fehlt für typ 'doppeltes_abgehen': '{fehlendes}'.")

        ausgang = Rundenausgang.DOPPELTES_ABGEHEN
        spielmacher_punkte = 0
        verlustwert, _ = doppeltes_abgehen_auswerten(body["reizwert"])
        mitpunkte = 30

        # Normaler Stich-Zwang gilt (normativ: rule-set-v1.md §14.4)
        gegenspieler_daten = [
            {
                "name": gs["name"],
                "meldepunkte": meldepunkte_mit_stich_zwang(
                    gs["meldepunkte"], gs["hat_eigenen_stich"]
                ),
                "stichwerte": gs["stichwerte"],
                "hat_eigenen_stich": gs["hat_eigenen_stich"],
            }
            for gs in body["gegenspieler"]
        ]

    elif typ in ("tausender_gewonnen", "tausender_verloren"):
        # Kein numerischer Einfluss auf Punktestand (normativ: rule-set-v1.md §15)
        ausgang = (
            Rundenausgang.TAUSENDER_GEWONNEN
            if typ == "tausender_gewonnen"
            else Rundenausgang.TAUSENDER_VERLOREN
        )
        spielmacher_punkte = 0
        verlustwert = 0
        mitpunkte = 0
        spielmacher_stern = ausgang == Rundenausgang.TAUSENDER_GEWONNEN
        gegenspieler_stern = ausgang == Rundenausgang.TAUSENDER_VERLOREN
        gegenspieler_daten = []

    else:
        return _fehler(
            f"Unbekannter Rundentyp: '{typ}'. "
            "Erlaubt: normal, einfaches_abgehen, doppeltes_abgehen, "
            "tausender_gewonnen, tausender_verloren."
        )

    try:
        runde = runde_persistieren(
            spiel_id=spiel_id,
            rundennummer=rundennummer,
            spielmacher_name=spielmacher_name,
            geber_name=geber_name,
            reizwert=body.get("reizwert", 0),
            rundenausgang=ausgang,
            spielmacher_punkte=spielmacher_punkte,
            verlustwert=verlustwert,
            mitpunkte_pro_gegenspieler=mitpunkte,
            spielmacher_stern=spielmacher_stern,
            gegenspieler_stern=gegenspieler_stern,
            gegenspieler=gegenspieler_daten,
        )
    except ObjectDoesNotExist:
        return _fehler(f"Spiel {spiel_id} nicht gefunden.", status=404)
    except (IntegrityError, ValueError, UngueltigeStichwerte) as exc:
        return _fehler(_validierungsfehler_nachricht(exc), status=400)

    return JsonResponse(
        {
            "id": runde.pk,
            "rundennummer": runde.rundennummer,
            "rundenausgang": runde.rundenausgang,
            "spielmacher_punkte": runde.spielmacher_punkte,
            "verlustwert": runde.verlustwert,
            "mitpunkte_pro_gegenspieler": runde.mitpunkte_pro_gegenspieler,
        },
        status=201,
    )


# ── Slice 6: Punktestände und Sieger ──────────────────────────────────────────

@require_GET
def punktestaende_view(request, spiel_id: int) -> JsonResponse:
    """GET /api/spiele/{id}/punktestaende/ — Aktuelle Punktestände aller Spieler."""
    try:
        punkte = punktestaende_laden(spiel_id)
    except ObjectDoesNotExist:
        return _fehler(f"Spiel {spiel_id} nicht gefunden.", status=404)

    return JsonResponse({"spiel_id": spiel_id, "punktestaende": punkte})


@require_GET
def sieger_view(request, spiel_id: int) -> JsonResponse:
    """GET /api/spiele/{id}/sieger/ — Sieger nach Spielende ermitteln.

    Optionaler Query-Parameter: exakte_stichwerte=Anna:12,Bernd:7
    Format: kommaseparierte Name:Wert-Paare für Tiebreaking mit 1er-Werten.
    """
    try:
        punkte = punktestaende_laden(spiel_id)
    except ObjectDoesNotExist:
        return _fehler(f"Spiel {spiel_id} nicht gefunden.", status=404)

    # Optionale exakte Stichwerte für Tiebreaking (normativ: rule-set-v1.md §9.3)
    exakte: dict[str, int] | None = None
    raw = request.GET.get("exakte_stichwerte")
    if raw:
        try:
            exakte = {
                teil.split(":")[0].strip(): int(teil.split(":")[1])
                for teil in raw.split(",")
            }
        except (ValueError, IndexError):
            return _fehler(
                "Ungültiges Format für exakte_stichwerte. "
                "Erwartet: 'Name1:Wert1,Name2:Wert2'."
            )

    gewinner = sieger_ermitteln(punkte, exakte)

    return JsonResponse(
        {
            "spiel_id": spiel_id,
            "punktestaende": punkte,
            "sieger": gewinner,
        }
    )

