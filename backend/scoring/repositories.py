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


# ── FND-006: gezählte Runden, Sequenz und Geber-Ableitung ──────────────────────

_TAUSENDER_AUSGAENGE: tuple[str, str] = (
    Rundenausgang.TAUSENDER_GEWONNEN.value,
    Rundenausgang.TAUSENDER_VERLOREN.value,
)


def _spieler_positionsliste(spiel_model: SpielModel) -> list[str]:
    """Spielernamen in fester Sitzreihenfolge (position 0..3)."""
    return list(
        spiel_model.spieler.order_by("position").values_list("name", flat=True)
    )


def _gezaehlte_runden(spiel_model: SpielModel, *, vor_sequenz: int | None = None) -> int:
    """Anzahl der ZÄHLENDEN (nicht-Tausender) Runden eines Spiels.

    Ein Tausender läuft außer Konkurrenz und zählt nicht als gespielte Runde
    (FND-006, normativ: docs/rule-set-v1.md §15). Optional werden nur Runden mit
    Sequenz (``rundennummer``) < ``vor_sequenz`` gezählt – Grundlage für die
    Geber-Ableitung einer bestimmten Runde.
    """
    runden = spiel_model.runden.exclude(rundenausgang__in=_TAUSENDER_AUSGAENGE)
    if vor_sequenz is not None:
        runden = runden.filter(rundennummer__lt=vor_sequenz)
    return runden.count()


def geber_fuer_sequenz(spiel_id: int, sequenz: int) -> str:
    """Geber der Runde mit gegebener Sequenz (``rundennummer``) – für die Korrektur (PUT).

    = spieler[(Anzahl gezählter Runden mit Sequenz < sequenz) % 4]. Hängt nur von
    den Runden DAVOR ab, ist damit unabhängig vom (ggf. korrigierten) Typ der Runde
    selbst. Ohne Tausender identisch zu ``Spiel.geber_in_runde(sequenz)`` – mit
    Tausender bleibt der Geber über die außer-Konkurrenz-Runden hinweg stehen
    (FND-006, §15).

    Raises:
        SpielModel.DoesNotExist: Wenn das Spiel nicht gefunden wird.
    """
    spiel_model = SpielModel.objects.prefetch_related("spieler").get(pk=spiel_id)
    reihenfolge = _spieler_positionsliste(spiel_model)
    index = _gezaehlte_runden(spiel_model, vor_sequenz=sequenz) % len(reihenfolge)
    return reihenfolge[index]


# ── Slices 2–5: Runde persistieren ────────────────────────────────────────────

def _namen_pruefen(
    spiel_id: int,
    spieler_map: dict[str, SpielerModel],
    spielmacher_name: str,
    geber_name: str,
    gegenspieler: list[GegenspielerDaten],
) -> None:
    """Stellt sicher, dass alle Namen im Spiel registriert sind (sonst ValueError)."""
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


def _gegenspieler_zeilen_setzen(
    runde: RundeModel,
    spieler_map: dict[str, SpielerModel],
    gegenspieler: list[GegenspielerDaten],
) -> None:
    """Ersetzt die GegenspielerRundeModel-Zeilen einer Runde vollständig.

    Beim Anlegen sind noch keine Zeilen vorhanden; bei der Korrektur (PUT) werden
    die alten gelöscht und neu erzeugt. Für Tausender ist ``gegenspieler`` leer,
    sodass die Runde ganz ohne Gegenspieler-Zeilen bleibt (HOCH-3).
    """
    runde.gegenspieler.all().delete()
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


@transaction.atomic
def runde_persistieren(
    *,
    spiel_id: int,
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

    Die ``rundennummer`` (Sequenz/Erfassungsreihenfolge) wird serverseitig als
    ``max+1`` vergeben – jede erfasste Runde inkl. Tausender ist eindeutig
    (FND-006). Der ``geber_name`` wird vom Aufrufer bereits serverseitig aus der
    Historie abgeleitet (``geber_fuer_neue_runde``), nicht vom Client übernommen.

    Legt einen RundeModel-Eintrag und je einen GegenspielerRundeModel-Eintrag
    pro Gegenspieler an.  Alle Schreiboperationen erfolgen in einer Transaktion.

    Args:
        spiel_id:                  PK des zugehörigen SpielModel.
        spielmacher_name:          Name des Spielmachers (muss in SpielerModel existieren).
        geber_name:                Name des Gebers (serverseitig abgeleitet).
        reizwert:                  Gereizte Punktzahl.
        rundenausgang:             Rundenausgang-Enum-Wert.
        spielmacher_punkte:        Erzielte Punkte des Spielmachers (0 bei Verlust).
        verlustwert:               Negativer Verlust (0 bei Gewinn).
        mitpunkte_pro_gegenspieler: Bonus für jeden Gegenspieler (0 bei Verlust des SM).
        spielmacher_stern:         Ob der Spielmacher einen Tausender-Stern trägt.
        gegenspieler_stern:        Ob die Gegenspieler einen Tausender-Stern tragen.
        gegenspieler:              Meldepunkte, Stichwerte und Stich-Zwang je Gegenspieler.
        spielmacher_meldepunkte:   Stich-zwang-gewertete Meldung (M) des Spielmachers.
        spielmacher_stichwerte:    Stichwerte (S) des Spielmachers. Invariante je Ausgang:
                                   gewonnenes Spiel spielmacher_punkte == M + S; doppeltes
                                   Abgehen punkte == 0, M|S = roh erfasste (verfallene) Werte
                                   (FND-004); einfaches Abgehen/Tausender M == S == 0.

    Returns:
        Das neu angelegte RundeModel.

    Raises:
        SpielModel.DoesNotExist:   Wenn das Spiel nicht gefunden wird.
        ValueError:                Wenn ein Spielername nicht im Spiel existiert.
    """
    spiel_model = SpielModel.objects.get(pk=spiel_id)
    spieler_map: dict[str, SpielerModel] = {
        s.name: s for s in spiel_model.spieler.all()
    }
    _namen_pruefen(spiel_id, spieler_map, spielmacher_name, geber_name, gegenspieler)

    # Fortlaufende Sequenz vergeben (Erfassungsreihenfolge/Identität, FND-006).
    letzte = (
        RundeModel.objects.filter(spiel=spiel_model)
        .order_by("-rundennummer")
        .values_list("rundennummer", flat=True)
        .first()
    )
    rundennummer = (letzte or 0) + 1

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
    _gegenspieler_zeilen_setzen(runde, spieler_map, gegenspieler)

    return runde


@transaction.atomic
def runde_aktualisieren(
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
    Überschreibt eine bereits gespeicherte Runde in-place (Korrektur, TASK-014).

    Aktualisiert alle Wertungsfelder und ersetzt die GegenspielerRundeModel-Zeilen
    vollständig. Dadurch schaltet auch ein Typ-Übergang korrekt um (HOCH-3):
    tausender→normal legt GS-Zeilen an und löscht die Sterne, normal→tausender
    löscht die GS-Zeilen und setzt die Sterne. Die Rundennummer bleibt erhalten,
    sodass Geberrotation und Sequenz unverändert bleiben.

    Raises:
        SpielModel.DoesNotExist:  Wenn das Spiel nicht gefunden wird.
        RundeModel.DoesNotExist:  Wenn die Runde (spiel_id, rundennummer) nicht existiert.
        ValueError:               Wenn ein Spielername nicht im Spiel existiert.
    """
    spiel_model = SpielModel.objects.get(pk=spiel_id)
    spieler_map: dict[str, SpielerModel] = {
        s.name: s for s in spiel_model.spieler.all()
    }
    _namen_pruefen(spiel_id, spieler_map, spielmacher_name, geber_name, gegenspieler)

    runde = RundeModel.objects.get(spiel=spiel_model, rundennummer=rundennummer)
    runde.reizwert = reizwert
    runde.rundenausgang = rundenausgang.value
    runde.spielmacher = spieler_map[spielmacher_name]
    runde.geber = spieler_map[geber_name]
    runde.spielmacher_punkte = spielmacher_punkte
    runde.spielmacher_meldepunkte = spielmacher_meldepunkte
    runde.spielmacher_stichwerte = spielmacher_stichwerte
    runde.verlustwert = verlustwert
    runde.mitpunkte_pro_gegenspieler = mitpunkte_pro_gegenspieler
    runde.spielmacher_stern = spielmacher_stern
    runde.gegenspieler_stern = gegenspieler_stern
    runde.save()

    _gegenspieler_zeilen_setzen(runde, spieler_map, gegenspieler)

    return runde


def letzte_rundennummer(spiel_id: int) -> int | None:
    """Höchste gespeicherte Rundennummer eines Spiels, oder None ohne Runden.

    Grundlage für die Korrektur-Regel „nur die letzte Runde ist editierbar"
    (TASK-014 / ADR-015).
    """
    return (
        RundeModel.objects.filter(spiel_id=spiel_id)
        .order_by("-rundennummer")
        .values_list("rundennummer", flat=True)
        .first()
    )


# ── Slice 6: Punktestände laden ────────────────────────────────────────────────

def _runde_beitrag(runde: RundeModel) -> dict[str, int]:
    """
    Beitrag einer einzelnen Runde zum kumulierten STAND je Spieler.

    Gemeinsame Wahrheit für den Gesamt-Punktestand (Summe über alle Runden) und
    die laufende STAND-Zeile der Anschreibetabelle (laufende Summe je Runde), damit
    beide garantiert identisch rechnen (HOCH-4).

    Wertungsregeln (normativ: docs/rule-set-v1.md, docs/Anschreibetabelle_4_Spieler.md §4):
    - Gewonnenes Spiel:       Spielmacher +spielmacher_punkte.
    - Einfaches/Doppeltes Abgehen: Spielmacher +verlustwert (negativ).
    - Tausender:              Kein numerischer Einfluss (leerer Beitrag).
    - Jeder Gegenspieler:     +meldepunkte +stichwerte +mitpunkte_pro_gegenspieler.
      (meldepunkte sind bereits stich-zwang-gewertet gespeichert; §12.2, §13.3, §14.3)

    Returns:
        Mapping Spielername → Beitrag dieser Runde. Nicht enthaltene Spieler tragen 0 bei.
    """
    beitrag: dict[str, int] = {}
    ausgang = Rundenausgang(runde.rundenausgang)

    if ausgang in (Rundenausgang.TAUSENDER_GEWONNEN, Rundenausgang.TAUSENDER_VERLOREN):
        return beitrag  # Tausender: STAND friert ein

    if ausgang == Rundenausgang.GEWONNENES_SPIEL:
        beitrag[runde.spielmacher.name] = runde.spielmacher_punkte
    else:
        # Einfaches oder doppeltes Abgehen: nur Spielmacher trägt den Verlust (negativ).
        beitrag[runde.spielmacher.name] = runde.verlustwert

    for gs in runde.gegenspieler.all():
        beitrag[gs.spieler.name] = (
            beitrag.get(gs.spieler.name, 0)
            + gs.meldepunkte + gs.stichwerte + runde.mitpunkte_pro_gegenspieler
        )

    return beitrag


def punktestaende_laden(spiel_id: int) -> dict[str, int]:
    """
    Berechnet den aktuellen numerischen Punktestand aller Spieler.

    Aggregiert die Pro-Runde-Beiträge (`_runde_beitrag`) über alle gespeicherten
    Runden eines Spiels. Nutzt denselben Beitrag wie die STAND-Zeile der
    Anschreibetabelle (HOCH-4), sodass beide garantiert übereinstimmen.

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
        for name, wert in _runde_beitrag(runde).items():
            punkte[name] += wert

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


# ── TASK-014: Rundenhistorie / Anschreibetabelle ──────────────────────────────

def rundenhistorie_laden(spiel_id: int) -> dict:
    """
    Baut die zweizeilige Anschreibetabelle (docs/Anschreibetabelle_4_Spieler.md §5).

    Je Runde eine Rundenzeile (M | S | Mit pro Spieler, Verlustwert beim
    verlierenden Spielmacher, Stern bei Tausender, „setzt aus" für den Geber) und
    der kumulierte STAND-Zwischenstand je Spieler. Der STAND wird über den
    gemeinsamen `_runde_beitrag` als laufende Summe gebildet (HOCH-4), sodass die
    letzte STAND-Zeile garantiert `punktestaende_laden` entspricht.

    Bei Tausender-Runden existieren KEINE GegenspielerRundeModel-Zeilen; die
    aktiven Gegenspieler werden aus „alle − Geber − Spielmacher" hergeleitet und
    erhalten (bei Tausender verloren) ihren Stern (§15.3). Der STAND friert ein.

    Returns:
        {
          "spieler": [Name, …]        # feste Sitzreihenfolge
          "runden": [
            {
              "rundennummer", "geber", "spielmacher", "reizwert",
              "rundenausgang", "ist_tausender", "verlustwert",
              "spieler": {Name: {rolle, meldepunkte, stichwerte, mitpunkte,
                                 hat_eigenen_stich, stern}},
              "stand": {Name: kumulierter STAND}
            }, …
          ]
        }

    Raises:
        SpielModel.DoesNotExist: Wenn das Spiel nicht gefunden wird.
    """
    spiel_model = SpielModel.objects.prefetch_related("spieler").get(pk=spiel_id)
    alle_namen = list(
        spiel_model.spieler.order_by("position").values_list("name", flat=True)
    )

    runden = (
        spiel_model.runden
        .select_related("spielmacher", "geber")
        .prefetch_related("gegenspieler__spieler")
        .order_by("rundennummer")
    )

    laufender_stand: dict[str, int] = {name: 0 for name in alle_namen}
    historie: list[dict] = []
    # Fortlaufende gezählte Spielrunde (Tausender zählen nicht, FND-006/§15).
    gezaehlt = 0

    for runde in runden:
        ausgang = Rundenausgang(runde.rundenausgang)
        ist_tausender = ausgang in (
            Rundenausgang.TAUSENDER_GEWONNEN,
            Rundenausgang.TAUSENDER_VERLOREN,
        )

        # Gezählte Spielrunde nur für reguläre Runden; Tausender laufen außer Konkurrenz.
        if ist_tausender:
            zaehlrunde: int | None = None
        else:
            gezaehlt += 1
            zaehlrunde = gezaehlt

        # STAND fortschreiben – gemeinsamer Beitrag (HOCH-4).
        for name, wert in _runde_beitrag(runde).items():
            laufender_stand[name] += wert

        aktive_gegenspieler = set(alle_namen) - {runde.geber.name, runde.spielmacher.name}
        gs_map = {gs.spieler.name: gs for gs in runde.gegenspieler.all()}

        spieler_daten: dict[str, dict] = {}
        for name in alle_namen:
            if name == runde.geber.name:
                spieler_daten[name] = {
                    "rolle": "geber",
                    "meldepunkte": 0,
                    "stichwerte": 0,
                    "mitpunkte": 0,
                    "hat_eigenen_stich": False,
                    "stern": False,
                }
            elif name == runde.spielmacher.name:
                spieler_daten[name] = {
                    "rolle": "spielmacher",
                    "meldepunkte": runde.spielmacher_meldepunkte,
                    "stichwerte": runde.spielmacher_stichwerte,
                    "mitpunkte": 0,
                    "hat_eigenen_stich": runde.spielmacher_stichwerte > 0,
                    "stern": runde.spielmacher_stern,
                }
            else:
                gs = gs_map.get(name)
                spieler_daten[name] = {
                    "rolle": "gegenspieler",
                    "meldepunkte": gs.meldepunkte if gs else 0,
                    "stichwerte": gs.stichwerte if gs else 0,
                    "mitpunkte": runde.mitpunkte_pro_gegenspieler if gs else 0,
                    "hat_eigenen_stich": gs.hat_eigenen_stich if gs else False,
                    "stern": runde.gegenspieler_stern and name in aktive_gegenspieler,
                }

        historie.append({
            "rundennummer": runde.rundennummer,
            "sequenz": runde.rundennummer,
            "zaehlrunde": zaehlrunde,
            "geber": runde.geber.name,
            "spielmacher": runde.spielmacher.name,
            "reizwert": runde.reizwert,
            "rundenausgang": runde.rundenausgang,
            "ist_tausender": ist_tausender,
            "verlustwert": runde.verlustwert,
            "spieler": spieler_daten,
            "stand": dict(laufender_stand),
        })

    return {"spieler": alle_namen, "runden": historie}
