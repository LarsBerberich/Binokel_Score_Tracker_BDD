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
from dataclasses import asdict

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from scoring.domain import (
    UnbekannterSpieler,
    UngueltigeRundenanzahl,
    UngueltigeStichwerte,
    UngueltigeSpielerzahl,
    UngueltigeMeldepunkte,
    UngueltigeRundeneingabe,
    UngueltigerSpielmacher,
    UngueltigerZehnerwert,
)
from scoring.repositories import (
    geber_fuer_sequenz,
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
    abrechnung_ermitteln,
    rollen_pruefen,
    runde_auswerten,
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
        return f"Ungültige Spielerzahl: {exc}"
    if isinstance(exc, UngueltigeRundenanzahl):
        return f"Ungültige Rundenzahl: {exc}"
    if isinstance(exc, UngueltigeStichwerte):
        return str(exc)
    if isinstance(exc, UngueltigerZehnerwert):
        return str(exc)
    if isinstance(exc, UngueltigeMeldepunkte):
        return str(exc)
    return "Ungültige Eingabedaten."


def _pflichtfeld(body: dict, *felder: str) -> str | None:
    """Gibt den Namen des ersten fehlenden Pflichtfelds zurück, oder None."""
    for feld in felder:
        if feld not in body:
            return feld
    return None


# Fachliche Eingabefehler einer Runde (Use Case + Domäne) → 400 mit der Meldung des Fehlers.
_RUNDE_EINGABEFEHLER = (
    UngueltigeRundeneingabe,
    UnbekannterSpieler,
    UngueltigerSpielmacher,
    UngueltigeMeldepunkte,
    UngueltigeStichwerte,
    UngueltigerZehnerwert,
)


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
    """Rundenhistorie (Anschreibetabelle) laden; 0 Runden → leere Historie (200).

    Additiv werden mitgeliefert:

    - ``zu_zahlen_cent``: Abrechnung bei sofortigem Spielende (rule-set-v1.md §20), Betrag je
      Spieler in ganzen Cent (5 Cent je 10 Punkte Differenz zum Höchststand);
    - ``sterne``: Summe der Tausender-Sterne je Spieler (§15) – dieselbe Aggregation wie
      ``/punktestaende/``, damit die Anschreibetabelle sie nicht ein zweites Mal berechnet.
    """
    try:
        historie = rundenhistorie_laden(spiel_id)
        punkte = punktestaende_laden(spiel_id)
        sterne = sterne_laden(spiel_id)
    except ObjectDoesNotExist:
        return _fehler(f"Spiel {spiel_id} nicht gefunden.", status=404)

    return JsonResponse(
        {
            "spiel_id": spiel_id,
            **historie,
            "zu_zahlen_cent": abrechnung_ermitteln(punkte),
            "sterne": sterne,
        }
    )


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

    fehlendes = _pflichtfeld(body, "typ", "spielmacher", "geber")
    if fehlendes:
        return _fehler(f"Pflichtfeld fehlt: '{fehlendes}'.")

    try:
        wertung = runde_auswerten(body)
    except _RUNDE_EINGABEFEHLER as exc:
        return _fehler(str(exc))

    try:
        rollen_pruefen(spiel_laden(spiel_id), body["geber"], body["spielmacher"])
    except ObjectDoesNotExist:
        return _fehler(f"Spiel {spiel_id} nicht gefunden.", status=404)
    except _RUNDE_EINGABEFEHLER as exc:
        return _fehler(str(exc))

    # rundennummer (Sequenz) vergibt das Repository selbst (max+1, FND-006); eine im
    # Body mitgeschickte rundennummer wird bewusst ignoriert. Der geber kommt weiterhin
    # aus dem Body (das Frontend leitet ihn aus der gezählten Runde/Historie ab).
    try:
        runde = runde_persistieren(
            spiel_id=spiel_id,
            spielmacher_name=body["spielmacher"],
            geber_name=body["geber"],
            reizwert=body.get("reizwert", 0),
            **asdict(wertung),
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
    übernommen. Der Spielmacher muss aktiv mitspielen – bei 4 Spielern also nicht der
    (aussetzende) Geber, bei 3 Spielern darf es der mitspielende Geber sein (ADR-017).

    Der Dispatch ist mit POST geteilt (HOCH-2), sodass Typ-Übergänge
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

    # Geber deterministisch aus der gezählten Runde ableiten (HOCH-1/HOCH-2, FND-006):
    # NICHT aus der rundennummer (= Sequenz inkl. Tausender), sondern aus der Anzahl
    # zählender Runden vor dieser Sequenz. Ohne Tausender identisch zur alten Rotation.
    geber_name = geber_fuer_sequenz(spiel_id, rundennummer)
    spielmacher_name: str = body["spielmacher"]
    try:
        rollen_pruefen(spiel, geber_name, spielmacher_name)
        wertung = runde_auswerten(body)
    except _RUNDE_EINGABEFEHLER as exc:
        return _fehler(str(exc))

    try:
        runde = runde_aktualisieren(
            spiel_id=spiel_id,
            rundennummer=rundennummer,
            spielmacher_name=spielmacher_name,
            geber_name=geber_name,
            reizwert=body.get("reizwert", 0),
            **asdict(wertung),
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

