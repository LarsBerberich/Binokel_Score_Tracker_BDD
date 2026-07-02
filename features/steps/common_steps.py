"""
Gemeinsame Step-Definitionen — werden von mehreren Feature-Dateien genutzt.
"""
from behave import given, when, then, step

from scoring.domain import Rundenausgang, UngueltigeStichwerte
from scoring.use_cases import (
    normales_spiel_auswerten,
    meldepunkte_mit_stich_zwang,
    dritten_stichwert_ermitteln,
    stichwerte_validieren,
    einfaches_abgehen_auswerten,
    doppeltes_abgehen_auswerten,
)


# ---------------------------------------------------------------------------
# When
# ---------------------------------------------------------------------------

@when("die Runde ausgewertet wird")
def step_runde_auswerten(context):
    """
    Zentraler Dispatch — berechnet Ergebnisse anhand des gesetzten Kontexts.

    Jeder Slice setzt im Angenommen-Block bestimmte context-Attribute,
    die hier ausgewertet werden. Die Branches schließen sich in der Praxis
    gegenseitig aus (jedes Szenario belegt nur einen Pfad).
    """
    context.fehler = None
    _reizwert = getattr(context, 'reizwert', None)
    _vorgabe = getattr(context, 'rundenausgang_vorgabe', None)

    # ── Branch 1: Normales Spiel — Spielmacher Punkte ─────────────────────
    _sm_melde = getattr(context, 'spielmacher_meldepunkte', None)
    _sm_stich = getattr(context, 'spielmacher_stichwerte', None)
    if _sm_melde is not None and _sm_stich is not None:
        ausgang, punkte = normales_spiel_auswerten(_reizwert or 0, _sm_melde, _sm_stich)
        context.rundenausgang = ausgang
        context.spielmacher_gesamtpunkte = punkte
        context.mitpunkte_pro_gegenspieler = 0  # bei gewonnenem Spiel keine Mitpunkte

    # ── Branch 2: Stich-Zwang aktiver Spieler (Gegenspieler, normales Spiel) ──
    _ak_melde = getattr(context, 'aktiver_spieler_meldepunkte', None)
    _ak_stiche = getattr(context, 'aktiver_spieler_stiche', None)
    if _ak_melde is not None and _ak_stiche is not None:
        context.aktiver_spieler_meldepunkte_gewertet = meldepunkte_mit_stich_zwang(
            _ak_melde, _ak_stiche > 0
        )

    # ── Branch 3: 250er Kontrollsumme ─────────────────────────────────────
    _bekannte = getattr(context, 'bekannte_stichwerte', [])
    if len(_bekannte) == 2:
        context.dritter_stichwert = dritten_stichwert_ermitteln(*_bekannte)
        context.stichwert_summe = sum(_bekannte) + context.dritter_stichwert
    elif len(_bekannte) == 3:
        try:
            stichwerte_validieren(_bekannte)
        except UngueltigeStichwerte as fehler:
            context.fehler = fehler

    # ── Branch 4: Einfaches Abgehen (aus Vorgabe) ─────────────────────────
    if _vorgabe == Rundenausgang.EINFACHES_ABGEHEN:
        context.rundenausgang = Rundenausgang.EINFACHES_ABGEHEN
        if _reizwert is not None:
            verlustwert, darst = einfaches_abgehen_auswerten(_reizwert)
            context.verlustwert_int = verlustwert
            context.verlustwert_str = str(verlustwert)
            context.verlustwert_darstellung = darst
            context.spielmacher_meldepunkte_gewertet = 0
            context.spielmacher_stichwerte_gewertet = 0
        # Gegenspieler behalten Meldepunkte ohne Stich-Zwang (Regelwerk §11)
        _gs_melde = getattr(context, 'gegenspieler_meldepunkte', None)
        if _gs_melde is not None:
            context.gegenspieler_meldepunkte_gewertet = _gs_melde
        context.mitpunkte_pro_gegenspieler = 30

    # ── Branch 5: Doppeltes Abgehen (aus Vorgabe) ─────────────────────────
    if _vorgabe == Rundenausgang.DOPPELTES_ABGEHEN:
        context.rundenausgang = Rundenausgang.DOPPELTES_ABGEHEN
        if _reizwert is not None:
            verlustwert, darst = doppeltes_abgehen_auswerten(_reizwert)
            context.verlustwert_int = verlustwert
            context.verlustwert_str = str(verlustwert)
            context.verlustwert_darstellung = darst
            context.spielmacher_meldepunkte_gewertet = 0
            context.spielmacher_stichwerte_gewertet = 0
        # Gegenspieler Stichwerte werden gewertet
        _gs_stich_wert = getattr(context, 'gegenspieler_stichwerte', None)
        if _gs_stich_wert is not None:
            context.gegenspieler_stichwerte_gewertet = _gs_stich_wert
        # Gegenspieler unterliegen normalem Stich-Zwang (Regelwerk §12)
        _gs_melde = getattr(context, 'gegenspieler_meldepunkte', None)
        _gs_stiche = getattr(context, 'gegenspieler_stiche', None)
        if _gs_melde is not None and _gs_stiche is not None:
            context.gegenspieler_meldepunkte_gewertet = meldepunkte_mit_stich_zwang(
                _gs_melde, _gs_stiche > 0
            )
        context.mitpunkte_pro_gegenspieler = 30

    # ── Branch 6: Tausender ───────────────────────────────────────────────
    if getattr(context, 'ist_tausender', False):
        context.tausender_meldepunkte_gewertet = None
        context.tausender_stichwerte_gewertet = None
        context.tausender_mitpunkte_gewertet = None
        if hasattr(context, 'numerischer_punktestand'):
            context.numerischer_punktestand_nachher = dict(context.numerischer_punktestand)

    if _vorgabe in (Rundenausgang.TAUSENDER_GEWONNEN, Rundenausgang.TAUSENDER_VERLOREN):
        context.rundenausgang = _vorgabe
        context.spielmacher_stern = (_vorgabe == Rundenausgang.TAUSENDER_GEWONNEN)
        context.gegenspieler_stern = (_vorgabe == Rundenausgang.TAUSENDER_VERLOREN)


# ---------------------------------------------------------------------------
# Rundenausgang (Given- und Then-Kontext)
# ---------------------------------------------------------------------------

@given('der Rundenausgang ist "{ausgang}"')
def step_rundenausgang_gegeben(context, ausgang):
    context.reizwert = None
    context.spielmacher_meldepunkte = None
    context.spielmacher_stichwerte = None
    context.bekannte_stichwerte = []
    context.gegenspieler_meldepunkte = None
    context.gegenspieler_stiche = None
    context.gegenspieler_stichwerte = None
    context.fehler = None
    context.rundenausgang_vorgabe = Rundenausgang(ausgang)


@then('ist der Rundenausgang "{ausgang}"')
def step_rundenausgang_pruefen(context, ausgang):
    erwartet = Rundenausgang(ausgang)
    assert context.rundenausgang == erwartet, (
        f"Erwartet Rundenausgang '{ausgang}', "
        f"aber erhalten: '{context.rundenausgang.value}'"
    )


# ---------------------------------------------------------------------------
# Spielmacher — Reizwert, Punkte, Verlustwert
# ---------------------------------------------------------------------------

@step("der Reizwert des Spielmachers ist {reizwert:d}")
def step_reizwert(context, reizwert):
    context.reizwert = reizwert


@step("der Spielmacher hat {meldepunkte:d} Meldepunkte und {stichwerte:d} "
      "Stichwerte einschließlich gedrückter Karten")
def step_spielmacher_punkte(context, meldepunkte, stichwerte):
    context.spielmacher_meldepunkte = meldepunkte
    context.spielmacher_stichwerte = stichwerte


@step("der Spielmacher erreicht mit {punkte:d} Punkten den Reizwert nicht")
def step_reizwert_nicht_erreicht(context, punkte):
    assert context.spielmacher_gesamtpunkte == punkte, (
        f"Erwartet Gesamtpunkte {punkte}, "
        f"aber erhalten: {context.spielmacher_gesamtpunkte}"
    )


@step("die Meldepunkte des Spielmachers werden mit 0 gewertet")
def step_spielmacher_meldepunkte_null(context):
    assert context.spielmacher_meldepunkte_gewertet == 0, (
        f"Erwartet 0 Meldepunkte, "
        f"aber erhalten: {context.spielmacher_meldepunkte_gewertet}"
    )


@step("die Stichwerte des Spielmachers werden mit 0 gewertet")
def step_spielmacher_stichwerte_null(context):
    assert context.spielmacher_stichwerte_gewertet == 0, (
        f"Erwartet 0 Stichwerte, "
        f"aber erhalten: {context.spielmacher_stichwerte_gewertet}"
    )


@then('wird beim Spielmacher der Verlustwert "{verlustwert}" eingetragen')
def step_verlustwert_eintragen(context, verlustwert):
    assert context.verlustwert_str == verlustwert, (
        f"Erwartet Verlustwert '{verlustwert}', "
        f"aber erhalten: '{context.verlustwert_str}'"
    )


@then('wird der Verlustwert als "{darstellung}" in der Tabelle dargestellt')
def step_verlustwert_darstellung(context, darstellung):
    assert context.verlustwert_darstellung == darstellung, (
        f"Erwartet Darstellung '{darstellung}', "
        f"aber erhalten: '{context.verlustwert_darstellung}'"
    )


# ---------------------------------------------------------------------------
# Gegenspieler — Meldepunkte, Stiche
# ---------------------------------------------------------------------------

@step("ein Gegenspieler hat {meldepunkte:d} Meldepunkte")
def step_gegenspieler_meldepunkte(context, meldepunkte):
    context.gegenspieler_meldepunkte = meldepunkte


@step("der Gegenspieler hat {stiche:d} eigene Stiche")
def step_gegenspieler_stiche(context, stiche):
    context.gegenspieler_stiche = stiche
