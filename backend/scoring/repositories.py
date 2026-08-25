"""
Persistenz-Repository für den Binokel Score Tracker – V1.

Dieses Modul kapselt alle Datenbankoperationen.  Die Use Cases in
use_cases.py bleiben dadurch reine Domänenfunktionen ohne Framework-
Abhängigkeiten.

Aufrufmuster (im View):
    1. Input validieren
    2. Use Case aufrufen  → Domänenergebnis
    3. Repository aufrufen → Ergebnis in DB speichern / aus DB laden
"""
from __future__ import annotations

from typing import TypedDict

from django.db import transaction

from scoring.domain import Rundenausgang, Spiel
from scoring.models import (
    GegenspielerRundeModel,
    RundeModel,
    SpielModel,
    SpielerModel,
)


# ── Datenübertragungstypen ─────────────────────────────────────────────────────

class GegenspielerDaten(TypedDict):
    """Eingabedaten eines Gegenspielers beim Speichern einer Runde."""
    name: str
    meldepunkte: int
    stichwerte: int
    hat_eigenen_stich: bool


# ── Slice 1: Spiel anlegen ─────────────────────────────────────────────────────

@transaction.atomic
def spiel_persistieren(spiel: Spiel) -> SpielModel:
    """
    Speichert ein Spiel-Domain-Objekt als SpielModel + SpielerModel-Einträge.

    Args:
        spiel: Das von spiel_anlegen() zurückgegebene Domain-Objekt.

    Returns:
        Das neu angelegte SpielModel (inkl. zugewiesener PK).
    """
    spiel_model = SpielModel.objects.create(rundenanzahl=spiel.rundenanzahl)
    SpielerModel.objects.bulk_create([
        SpielerModel(spiel=spiel_model, name=name, position=position)
        for position, name in enumerate(spiel.spieler_reihenfolge)
    ])
    return spiel_model


def spiel_laden(spiel_id: int) -> Spiel:
    """
    Lädt ein SpielModel aus der DB und konvertiert es in ein Spiel-Domain-Objekt.

    Raises:
        SpielModel.DoesNotExist: Wenn kein Spiel mit dieser ID existiert.
    """
    spiel_model = SpielModel.objects.prefetch_related("spieler").get(pk=spiel_id)
    spieler_namen = list(
        spiel_model.spieler.order_by("position").values_list("name", flat=True)
    )
    return Spiel(spieler_reihenfolge=spieler_namen, rundenanzahl=spiel_model.rundenanzahl)


# ── Slices 2–5: Runde persistieren ────────────────────────────────────────────

@transaction.atomic
def runde_persistieren(
    *,
    spiel_id: int,
    rundennummer: int,
    spielmacher_name: str,
    geber_name: str,
    reizwert: int,
    rundenausgang: Rundenausgang,
    spielmacher_punkte: int,
    verlustwert: int,
    mitpunkte_pro_gegenspieler: int,
    spielmacher_stern: bool,
    gegenspieler_stern: bool,
    gegenspieler: list[GegenspielerDaten],
    spielmacher_meldepunkte: int = 0,
    spielmacher_stichwerte: int = 0,
) -> RundeModel:
    """
    Speichert das vollständige Ergebnis einer ausgewerteten Runde.

    Legt einen RundeModel-Eintrag und je einen GegenspielerRundeModel-Eintrag
    pro Gegenspieler an.  Alle Schreiboperationen erfolgen in einer Transaktion.

    Args:
        spiel_id:                  PK des zugehörigen SpielModel.
        rundennummer:              1-basierte Rundennummer.
        spielmacher_name:          Name des Spielmachers (muss in SpielerModel existieren).
        geber_name:                Name des Gebers (muss in SpielerModel existieren).
        reizwert:                  Gereizte Punktzahl.
        rundenausgang:             Rundenausgang-Enum-Wert.
        spielmacher_punkte:        Erzielte Punkte des Spielmachers (0 bei Verlust).
        verlustwert:               Negativer Verlust (0 bei Gewinn).
        mitpunkte_pro_gegenspieler: Bonus für jeden Gegenspieler (0 bei Verlust des SM).
        spielmacher_stern:         Ob der Spielmacher einen Tausender-Stern trägt.
        gegenspieler_stern:        Ob die Gegenspieler einen Tausender-Stern tragen.
        gegenspieler:              Meldepunkte, Stichwerte und Stich-Zwang je Gegenspieler.
        spielmacher_meldepunkte:   Stich-zwang-gewertete Meldung (M) des Spielmachers.
        spielmacher_stichwerte:    Stichwerte (S) des Spielmachers. Es gilt die Invariante
                                   spielmacher_punkte == spielmacher_meldepunkte
                                   + spielmacher_stichwerte (0|0 bei Verlust/Tausender).

    Returns:
        Das neu angelegte RundeModel.

    Raises:
        SpielModel.DoesNotExist:   Wenn das Spiel nicht gefunden wird.
        SpielerModel.DoesNotExist: Wenn ein Spielername nicht im Spiel existiert.
    """
    spiel_model = SpielModel.objects.get(pk=spiel_id)
    spieler_map: dict[str, SpielerModel] = {
        s.name: s for s in spiel_model.spieler.all()
    }

    if spielmacher_name not in spieler_map:
        raise ValueError(
            f"Spielmacher '{spielmacher_name}' ist nicht im Spiel #{spiel_id} registriert."
        )
    if geber_name not in spieler_map:
        raise ValueError(
            f"Geber '{geber_name}' ist nicht im Spiel #{spiel_id} registriert."
        )
    for gs in gegenspieler:
        if gs["name"] not in spieler_map:
            raise ValueError(
                f"Gegenspieler '{gs['name']}' ist nicht im Spiel #{spiel_id} registriert."
            )

    runde = RundeModel.objects.create(
        spiel=spiel_model,
        rundennummer=rundennummer,
        reizwert=reizwert,
        spielmacher_meldepunkte=spielmacher_meldepunkte,
        spielmacher_stichwerte=spielmacher_stichwerte,
        rundenausgang=rundenausgang.value,
        spielmacher=spieler_map[spielmacher_name],
        geber=spieler_map[geber_name],
        spielmacher_punkte=spielmacher_punkte,
        verlustwert=verlustwert,
        mitpunkte_pro_gegenspieler=mitpunkte_pro_gegenspieler,
        spielmacher_stern=spielmacher_stern,
        gegenspieler_stern=gegenspieler_stern,
    )

    GegenspielerRundeModel.objects.bulk_create([
        GegenspielerRundeModel(
            runde=runde,
            spieler=spieler_map[gs["name"]],
            meldepunkte=gs["meldepunkte"],
            stichwerte=gs["stichwerte"],
            hat_eigenen_stich=gs["hat_eigenen_stich"],
        )
        for gs in gegenspieler
    ])

    return runde


# ── Slice 6: Punktestände laden ────────────────────────────────────────────────

def punktestaende_laden(spiel_id: int) -> dict[str, int]:
    """
    Berechnet den aktuellen numerischen Punktestand aller Spieler.

    Aggregiert alle gespeicherten Runden eines Spiels.

    Wertungsregeln (normativ: docs/rule-set-v1.md):
    - Gewonnenes Spiel:       Spielmacher +spielmacher_punkte,
                              jeder Gegenspieler +mitpunkte_pro_gegenspieler.
    - Einfaches/Doppeltes Abgehen: Spielmacher +verlustwert (negativ),
                              Gegenspieler erhalten nichts.
    - Tausender:              Kein Einfluss auf numerischen Punktestand.
    - Geber:                  Setzt aus, erhält keine Punkte für diese Runde.

    Returns:
        Mapping Spielername → Gesamtpunktestand.

    Raises:
        SpielModel.DoesNotExist: Wenn das Spiel nicht gefunden wird.
    """
    spiel_model = SpielModel.objects.prefetch_related("spieler").get(pk=spiel_id)
    punkte: dict[str, int] = {s.name: 0 for s in spiel_model.spieler.all()}

    runden = (
        spiel_model.runden
        .select_related("spielmacher")
        .prefetch_related("gegenspieler__spieler")
    )

    for runde in runden:
        ausgang = Rundenausgang(runde.rundenausgang)

        if ausgang in (Rundenausgang.TAUSENDER_GEWONNEN, Rundenausgang.TAUSENDER_VERLOREN):
            continue  # Tausender: kein numerischer Einfluss

        if ausgang == Rundenausgang.GEWONNENES_SPIEL:
            punkte[runde.spielmacher.name] += runde.spielmacher_punkte
        else:
            # Einfaches oder doppeltes Abgehen: nur Spielmacher trägt Verlust
            punkte[runde.spielmacher.name] += runde.verlustwert  # verlustwert ist negativ

        # Gegenspieler: gewertete Meldepunkte + Stichwerte + Mitpunkte (normativ: §12.2, §13.3, §14.3)
        # Hinweis: meldepunkte in GegenspielerRundeModel sind bereits stich-zwang-gewertet gespeichert.
        for gs in runde.gegenspieler.all():
            punkte[gs.spieler.name] += (
                gs.meldepunkte + gs.stichwerte + runde.mitpunkte_pro_gegenspieler
            )

    return punkte


def sterne_laden(spiel_id: int) -> dict[str, int]:
    """
    Aggregiert die Tausender-Sterne je Spieler über alle Runden eines Spiels.

    Sterne stammen ausschließlich aus Tausender-Runden (normativ: docs/rule-set-v1.md §15):
    - spielmacher_stern gesetzt  → +1 für den Spielmacher (Tausender gewonnen).
    - gegenspieler_stern gesetzt → +1 für jeden aktiven Gegenspieler (Tausender verloren).

    Wichtig: Bei Tausender-Runden werden KEINE GegenspielerRundeModel-Zeilen angelegt.
    Die aktiven Gegenspieler werden daher aus „alle Spieler − Geber − Spielmacher"
    hergeleitet (der Geber setzt aus und erhält keinen Stern, §15.3).

    Returns:
        Mapping Spielername → Anzahl Sterne.

    Raises:
        SpielModel.DoesNotExist: Wenn das Spiel nicht gefunden wird.
    """
    spiel_model = SpielModel.objects.prefetch_related("spieler").get(pk=spiel_id)
    sterne: dict[str, int] = {s.name: 0 for s in spiel_model.spieler.all()}
    alle_namen = set(sterne)

    runden = spiel_model.runden.select_related("spielmacher", "geber")

    for runde in runden:
        if runde.spielmacher_stern:
            sterne[runde.spielmacher.name] += 1
        if runde.gegenspieler_stern:
            gegenspieler = alle_namen - {runde.geber.name, runde.spielmacher.name}
            for name in gegenspieler:
                sterne[name] += 1

    return sterne
