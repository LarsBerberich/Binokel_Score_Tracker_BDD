"""
Step-Definitionen für: runde_normales_spiel.feature
Slice 2 — häufigster Ablauf, zentrale Wertungslogik.
"""
from behave import given, when, then, step

from scoring.domain import UngueltigeStichwerte


# ---------------------------------------------------------------------------
# Hilfsfunktion
# ---------------------------------------------------------------------------

def _init_runden_kontext(context):
    """Setzt alle Runden-Kontextvariablen auf ihre Standardwerte."""
    context.reizwert = None
    context.spielmacher_meldepunkte = None
    context.spielmacher_stichwerte = None
    context.aktiver_spieler_meldepunkte = None
    context.aktiver_spieler_stiche = None
    context.bekannte_stichwerte = []
    context.rundenausgang_vorgabe = None
    context.fehler = None


# ---------------------------------------------------------------------------
# Given
# ---------------------------------------------------------------------------

@given("eine regulär ausgespielte Runde mit Reizwert {reizwert:d}")
def step_runde_mit_reizwert(context, reizwert):
    _init_runden_kontext(context)
    context.reizwert = reizwert


@given("eine regulär ausgespielte Runde")
def step_runde_ohne_reizwert(context):
    _init_runden_kontext(context)


# ---------------------------------------------------------------------------
# Then
# ---------------------------------------------------------------------------

@then("werden seine Meldepunkte mit 0 gewertet")
def step_aktiver_spieler_meldepunkte_null(context):
    assert context.aktiver_spieler_meldepunkte_gewertet == 0, (
        f"Erwartet 0 Meldepunkte, aber erhalten: "
        f"{context.aktiver_spieler_meldepunkte_gewertet}"
    )


@then("wird der fehlende dritte Stichwert mit {wert:d} ermittelt")
def step_dritter_stichwert_ermitteln(context, wert):
    assert context.dritter_stichwert == wert, (
        f"Erwartet dritten Stichwert {wert}, aber erhalten: {context.dritter_stichwert}"
    )


@then("wird die Eingabe abgelehnt")
def step_eingabe_abgelehnt(context):
    assert context.fehler is not None, "Erwartet einen Fehler, aber keiner wurde ausgelöst."


# ---------------------------------------------------------------------------
# And / Step (kontextneutral)
# ---------------------------------------------------------------------------

@step("der Spielmacher hat mindestens einen eigenen Stich")
def step_spielmacher_hat_stich(context):
    context.spielmacher_hat_stich = True  # Vorbedingung; beeinflusst Berechnung nicht


@step("der Spielmacher erreicht mit {punkte:d} Punkten den Reizwert")
def step_reizwert_erreicht(context, punkte):
    assert context.spielmacher_gesamtpunkte == punkte, (
        f"Erwartet Gesamtpunkte {punkte}, aber erhalten: {context.spielmacher_gesamtpunkte}"
    )


@step("es werden keine Mitpunkte vergeben")
def step_keine_mitpunkte_vergeben(context):
    assert context.mitpunkte_pro_gegenspieler == 0, (
        f"Erwartet 0 Mitpunkte, aber erhalten: {context.mitpunkte_pro_gegenspieler}"
    )


@step("ein aktiver Spieler hat {meldepunkte:d} Meldepunkte gemeldet")
def step_aktiver_spieler_meldepunkte(context, meldepunkte):
    context.aktiver_spieler_meldepunkte = meldepunkte


@step("der aktive Spieler hat {stiche:d} eigene Stiche")
def step_aktiver_spieler_stiche(context, stiche):
    context.aktiver_spieler_stiche = stiche


@step("die Stichwerte zweier aktiver Spieler sind {wert1:d} und {wert2:d}")
def step_zwei_stichwerte(context, wert1, wert2):
    context.bekannte_stichwerte = [wert1, wert2]


@step("die Summe der drei Stichwerte beträgt {summe:d}")
def step_stichwert_summe(context, summe):
    assert context.stichwert_summe == summe, (
        f"Erwartet Stichwert-Summe {summe}, aber erhalten: {context.stichwert_summe}"
    )


@step("die Stichwerte aller drei aktiven Spieler sind {wert1:d}, {wert2:d} und {wert3:d}")
def step_alle_drei_stichwerte(context, wert1, wert2, wert3):
    context.bekannte_stichwerte = [wert1, wert2, wert3]


@step("es wird ein Fehler angezeigt, dass die Stichwerte in der Summe 250 ergeben müssen")
def step_fehler_kontrollsumme(context):
    assert isinstance(context.fehler, UngueltigeStichwerte), (
        f"Erwartet UngueltigeStichwerte, aber erhalten: {type(context.fehler)}"
    )
