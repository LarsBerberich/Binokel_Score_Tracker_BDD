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
    UngueltigeMeldepunkte,
    UngueltigerZehnerwert,
)
from scoring.repositories import (
    letzte_rundennummer,
    punktestaende_laden,
    runde_aktualisieren,
    runde_persistieren,
    rundenhistorie_laden,
    spiel_laden,
    spiel_persistieren,
    sterne_laden,
)
from scoring.use_cases import (
    doppeltes_abgehen_auswerten,
    einfaches_abgehen_auswerten,
    meldepunkte_mit_stich_zwang,
    meldepunkte_validieren,
    normales_spiel_auswerten,
    sieger_ermitteln,
    spiel_anlegen,
    stichwerte_validieren,
    zehnerwert_validieren,
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
        return str(exc)
    if isinstance(exc, UngueltigerZehnerwert):
        return str(exc)
    if isinstance(exc, UngueltigeMeldepunkte):
        return str(exc)
    return "Ungültige Eingabedaten."


def _meldepunkte_pruefen(body: dict) -> None:
    """Validiert alle im Body enthaltenen Meldepunkte (Spielmacher + Gegenspieler).

    Plausibilitätsgrenze (normativ: docs/rule-set-v1.md §7.1).
    """
    if "meldepunkte" in body:
        meldepunkte_validieren(body["meldepunkte"])
    for gegenspieler in body.get("gegenspieler", []):
        if isinstance(gegenspieler, dict) and "meldepunkte" in gegenspieler:
            meldepunkte_validieren(gegenspieler["meldepunkte"])


def _zehner_und_kontrollsumme_pruefen(body: dict, *, mit_spielmacher_stichwert: bool) -> None:
    """Erzwingt die Zehner-Eingabe (§9.1/§9.4) für alle in den STAND einfließenden Werte.

    Gilt für die Rundentypen 'normal' und 'doppeltes_abgehen': Reizwert und alle
    Meldepunkte müssen Vielfache von 10 sein; die Stichwerte zusätzlich ≤ 250
    (Kontrollsumme) und ebenfalls Vielfache von 10.

    Args:
        mit_spielmacher_stichwert: True bei 'normal' (Spielmacher hat einen
            eigenen Stichwert), False bei 'doppeltes_abgehen' (Stichwert verfällt).

    Raises:
        UngueltigerZehnerwert: Reizwert/Meldepunkte kein Zehner.
        UngueltigeStichwerte:  Stichwert kein Zehner oder Summe > 250.
    """
    if "reizwert" in body:
        zehnerwert_validieren(body["reizwert"], "Reizwert")
    if "meldepunkte" in body:
        zehnerwert_validieren(body["meldepunkte"], "Meldepunkte")
    for gs in body.get("gegenspieler", []):
        if isinstance(gs, dict) and "meldepunkte" in gs:
            zehnerwert_validieren(gs["meldepunkte"], "Meldepunkte")

    stichwerte = [
        gs["stichwerte"]
        for gs in body.get("gegenspieler", [])
        if isinstance(gs, dict) and "stichwerte" in gs
    ]
    if mit_spielmacher_stichwert and "stichwerte" in body:
        stichwerte.append(body["stichwerte"])
    if stichwerte:
        stichwerte_validieren(stichwerte)


def _pflichtfeld(body: dict, *felder: str) -> str | None:
    """Gibt den Namen des ersten fehlenden Pflichtfelds zurück, oder None."""
    for feld in felder:
        if feld not in body:
            return feld
    return None


class _RundeEingabeFehler(Exception):
    """Fachlicher Eingabefehler mit HTTP-Status – POST und PUT teilen ihn (HOCH-2)."""

    def __init__(self, nachricht: str, status: int = 400) -> None:
        super().__init__(nachricht)
        self.nachricht = nachricht
        self.status = status


def _runde_wertung_berechnen(body: dict) -> dict:
    """Dispatch + Validierung einer Runde nach Typ – gemeinsam für POST und PUT (HOCH-2).

    Führt Meldepunkte-Plausibilität (§7.1), Zehner-/Kontrollsummen-Prüfung
    (§9.1/§9.4), den Typ-Dispatch inkl. Stern- und Gegenspieler-Zeilen-Logik
    (HOCH-3) sowie die Spielmacher-M|S-Invariante (HOCH-1:
    ``spielmacher_punkte == spielmacher_meldepunkte + spielmacher_stichwerte``)
    an EINER Stelle aus. Dadurch durchläuft die Korrektur (PUT) exakt dieselbe
    Wertung wie das Anlegen (POST) – keine Duplikation.

    Returns:
        dict mit allen Wertungsfeldern (rundenausgang, spielmacher_punkte,
        verlustwert, mitpunkte_pro_gegenspieler, spielmacher_stern,
        gegenspieler_stern, spielmacher_meldepunkte, spielmacher_stichwerte,
        gegenspieler) – direkt als ``**kwargs`` für runde_persistieren /
        runde_aktualisieren nutzbar.

    Raises:
        _RundeEingabeFehler: Bei fehlenden Pflichtfeldern, unbekanntem Typ oder
            verletzter Validierung (modulo-10, 250-Kontrollsumme, 1800-Maximum).
    """
    typ: str = body["typ"]
    spielmacher_stern: bool = body.get("spielmacher_stern", False)
    gegenspieler_stern: bool = body.get("gegenspieler_stern", False)

    # Spielmacher-M/S für die getrennte Anschreibetabelle (§5); Invariante
    # spielmacher_punkte == spielmacher_meldepunkte + spielmacher_stichwerte.
    # Bei Verlust/Tausender bleiben beide 0 (siehe Defaults hier).
    spielmacher_meldepunkte = 0
    spielmacher_stichwerte = 0

    # Plausibilitätsgrenze der Meldepunkte prüfen (normativ: rule-set-v1.md §7.1).
    try:
        _meldepunkte_pruefen(body)
    except UngueltigeMeldepunkte as exc:
        raise _RundeEingabeFehler(_validierungsfehler_nachricht(exc)) from exc

    # ── Dispatch nach Rundentyp ────────────────────────────────────────────────

    if typ == "normal":
        fehlendes = _pflichtfeld(body, "reizwert", "meldepunkte", "stichwerte",
                                 "hat_eigenen_stich", "gegenspieler")
        if fehlendes:
            raise _RundeEingabeFehler(f"Pflichtfeld fehlt für typ 'normal': '{fehlendes}'.")

        # Zehner-Eingabe + 250-Kontrollsumme erzwingen (normativ: §9.1/§9.4).
        try:
            _zehner_und_kontrollsumme_pruefen(body, mit_spielmacher_stichwert=True)
        except (UngueltigeStichwerte, UngueltigerZehnerwert) as exc:
            raise _RundeEingabeFehler(_validierungsfehler_nachricht(exc)) from exc

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
            # Getrennte M|S nur bei gewonnenem Spiel; Invariante M+S == Punkte (§5).
            spielmacher_meldepunkte = sm_melde
            spielmacher_stichwerte = body["stichwerte"]
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
            raise _RundeEingabeFehler(
                f"Pflichtfeld fehlt für typ 'einfaches_abgehen': '{fehlendes}'."
            )

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
            raise _RundeEingabeFehler(
                f"Pflichtfeld fehlt für typ 'doppeltes_abgehen': '{fehlendes}'."
            )

        # Zehner-Eingabe + 250-Kontrollsumme erzwingen; Spielmacher-Stichwert verfällt (§9.1/§9.4).
        try:
            _zehner_und_kontrollsumme_pruefen(body, mit_spielmacher_stichwert=False)
        except (UngueltigeStichwerte, UngueltigerZehnerwert) as exc:
            raise _RundeEingabeFehler(_validierungsfehler_nachricht(exc)) from exc

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
        raise _RundeEingabeFehler(
            f"Unbekannter Rundentyp: '{typ}'. "
            "Erlaubt: normal, einfaches_abgehen, doppeltes_abgehen, "
            "tausender_gewonnen, tausender_verloren."
        )

    return {
        "rundenausgang": ausgang,
        "spielmacher_punkte": spielmacher_punkte,
        "verlustwert": verlustwert,
        "mitpunkte_pro_gegenspieler": mitpunkte,
        "spielmacher_stern": spielmacher_stern,
        "gegenspieler_stern": gegenspieler_stern,
        "spielmacher_meldepunkte": spielmacher_meldepunkte,
        "spielmacher_stichwerte": spielmacher_stichwerte,
        "gegenspieler": gegenspieler_daten,
    }


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

def _rundenhistorie_antwort(spiel_id: int) -> JsonResponse:
    """Rundenhistorie (Anschreibetabelle) laden; 0 Runden → leere Historie (200)."""
    try:
        historie = rundenhistorie_laden(spiel_id)
    except ObjectDoesNotExist:
        return _fehler(f"Spiel {spiel_id} nicht gefunden.", status=404)

    return JsonResponse({"spiel_id": spiel_id, **historie})


@csrf_exempt
def runden_view(request, spiel_id: int) -> JsonResponse:
    """POST /api/spiele/{id}/runden/ — Runde auswerten und speichern.
    GET  /api/spiele/{id}/runden/ — Rundenhistorie (Anschreibetabelle) laden.

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
    if request.method == "GET":
        return _rundenhistorie_antwort(spiel_id)

    if request.method != "POST":
        return _fehler("Nur GET oder POST erlaubt.", status=405)

    try:
        body = _json_body(request)
    except ValueError:
        return _fehler("Ungültiger JSON-Body.")

    fehlendes = _pflichtfeld(body, "typ", "rundennummer", "spielmacher", "geber")
    if fehlendes:
        return _fehler(f"Pflichtfeld fehlt: '{fehlendes}'.")

    try:
        wertung = _runde_wertung_berechnen(body)
    except _RundeEingabeFehler as exc:
        return _fehler(exc.nachricht, status=exc.status)

    try:
        runde = runde_persistieren(
            spiel_id=spiel_id,
            rundennummer=body["rundennummer"],
            spielmacher_name=body["spielmacher"],
            geber_name=body["geber"],
            reizwert=body.get("reizwert", 0),
            **wertung,
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


@csrf_exempt
def runde_detail_view(request, spiel_id: int, rundennummer: int) -> JsonResponse:
    """PUT /api/spiele/{id}/runden/{nr}/ — Korrektur der LETZTEN Runde (TASK-014, ADR-015).

    Nur die höchste gespeicherte Rundennummer ist editierbar:
    - Nicht-letzte Runde        → 409 Conflict
    - Runde/Spiel nicht vorhanden → 404 Not Found
    - Validierungsfehler        → 400 (gemeinsames _fehler-Schema)

    Body-Felder wie bei POST, jedoch OHNE ``geber``: der Geber wird deterministisch
    aus der Rundennummer abgeleitet (HOCH-5, Geberrotation §3), nicht vom Client
    übernommen. Der Dispatch ist mit POST geteilt (HOCH-2), sodass Typ-Übergänge
    tausender↔normal die Gegenspieler-Zeilen und Sterne korrekt umschalten (HOCH-3)
    und die Spielmacher-M|S-Invariante (HOCH-1) erhalten bleibt.
    """
    if request.method != "PUT":
        return _fehler("Nur PUT erlaubt.", status=405)

    try:
        body = _json_body(request)
    except ValueError:
        return _fehler("Ungültiger JSON-Body.")

    fehlendes = _pflichtfeld(body, "typ", "spielmacher")
    if fehlendes:
        return _fehler(f"Pflichtfeld fehlt: '{fehlendes}'.")

    try:
        spiel = spiel_laden(spiel_id)
    except ObjectDoesNotExist:
        return _fehler(f"Spiel {spiel_id} nicht gefunden.", status=404)

    # Korrektur-Regel: nur die letzte Runde ist editierbar (ADR-015).
    letzte = letzte_rundennummer(spiel_id)
    if letzte is None:
        return _fehler(f"Spiel {spiel_id} hat noch keine Runden.", status=404)
    if rundennummer < 1 or rundennummer > letzte:
        return _fehler(
            f"Runde {rundennummer} in Spiel {spiel_id} existiert nicht.", status=404
        )
    if rundennummer != letzte:
        return _fehler(
            f"Nur die letzte Runde ({letzte}) ist korrigierbar, nicht Runde {rundennummer}.",
            status=409,
        )

    # Geber deterministisch aus der Rundennummer ableiten (HOCH-5, nicht vom Client).
    geber_name = spiel.geber_in_runde(rundennummer)
    spielmacher_name: str = body["spielmacher"]
    if spielmacher_name not in spiel.spieler_reihenfolge:
        return _fehler(
            f"Spielmacher '{spielmacher_name}' ist nicht im Spiel #{spiel_id} registriert."
        )
    if spielmacher_name == geber_name:
        return _fehler(
            f"Der Spielmacher darf nicht der Geber sein (Geber in Runde {rundennummer}: "
            f"'{geber_name}')."
        )

    try:
        wertung = _runde_wertung_berechnen(body)
    except _RundeEingabeFehler as exc:
        return _fehler(exc.nachricht, status=exc.status)

    try:
        runde = runde_aktualisieren(
            spiel_id=spiel_id,
            rundennummer=rundennummer,
            spielmacher_name=spielmacher_name,
            geber_name=geber_name,
            reizwert=body.get("reizwert", 0),
            **wertung,
        )
    except ObjectDoesNotExist:
        return _fehler(f"Runde {rundennummer} in Spiel {spiel_id} nicht gefunden.", status=404)
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
        status=200,
    )



# ── Slice 6: Punktestände und Sieger ──────────────────────────────────────────

@require_GET
def punktestaende_view(request, spiel_id: int) -> JsonResponse:
    """GET /api/spiele/{id}/punktestaende/ — Aktuelle Punktestände + Sterne aller Spieler."""
    try:
        punkte = punktestaende_laden(spiel_id)
        sterne = sterne_laden(spiel_id)
    except ObjectDoesNotExist:
        return _fehler(f"Spiel {spiel_id} nicht gefunden.", status=404)

    return JsonResponse(
        {"spiel_id": spiel_id, "punktestaende": punkte, "sterne": sterne}
    )


@require_GET
def sieger_view(request, spiel_id: int) -> JsonResponse:
    """GET /api/spiele/{id}/sieger/ — Sieger nach Spielende ermitteln.

    Optionaler Query-Parameter: exakte_stichwerte=Anna:12,Bernd:7
    Format: kommaseparierte Name:Wert-Paare für Tiebreaking mit 1er-Werten.
    """
    try:
        punkte = punktestaende_laden(spiel_id)
        sterne = sterne_laden(spiel_id)
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
            "sterne": sterne,
            "sieger": gewinner,
        }
    )

