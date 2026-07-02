"""
Anwendungsfälle (Use Cases) für den Binokel Score Tracker.

Jede Funktion entspricht einem fachlichen Anwendungsfall aus der Gherkin-Spezifikation.
Normative Quelle: docs/rule-set-v1.md.
"""
from __future__ import annotations

from scoring.domain import (
    Spiel,
    Rundenausgang,
    STANDARD_RUNDENANZAHL,
    GUELTIGE_SPIELERZAHL,
    STICHWERT_KONTROLLSUMME,
    UngueltigeSpielerzahl,
    UngueltigeRundenanzahl,
    UngueltigeStichwerte,
)


# ── Slice 1: Spiel anlegen ─────────────────────────────────────────────────────

def spiel_anlegen(
    spieler: list[str],
    rundenanzahl: int | None = None,
) -> Spiel:
    """
    Legt ein neues V1-Binokel-Spiel an.

    Validierungsregeln (normativ: docs/rule-set-v1.md §2, §3, §4):
    - Es müssen genau 4 Spieler angegeben werden.
    - Die Rundenzahl muss ein Vielfaches von 4 sein.
    - Wird keine Rundenzahl angegeben, gilt der Standardwert 12.

    Raises:
        UngueltigeSpielerzahl:  Wenn nicht genau 4 Spieler angegeben wurden.
        UngueltigeRundenanzahl: Wenn die Rundenzahl kein Vielfaches von 4 ist.
    """
    if len(spieler) != GUELTIGE_SPIELERZAHL:
        raise UngueltigeSpielerzahl(
            f"Ein V1-Spiel erfordert genau {GUELTIGE_SPIELERZAHL} Spieler, "
            f"aber {len(spieler)} wurden angegeben."
        )

    if rundenanzahl is None:
        rundenanzahl = STANDARD_RUNDENANZAHL

    if rundenanzahl % 4 != 0:
        raise UngueltigeRundenanzahl(
            f"Die Rundenzahl muss ein Vielfaches von 4 sein, "
            f"aber {rundenanzahl} wurde angegeben."
        )

    return Spiel(spieler_reihenfolge=spieler, rundenanzahl=rundenanzahl)


# ── Slice 2: Normales Spiel auswerten ─────────────────────────────────────────

def normales_spiel_auswerten(
    reizwert: int,
    meldepunkte: int,
    stichwerte: int,
) -> tuple[Rundenausgang, int]:
    """
    Berechnet Ausgang und Gesamtpunkte für eine regulär gespielte Runde.

    Normativ: docs/rule-set-v1.md §5, §7.

    Returns:
        (Rundenausgang, spielmacher_gesamtpunkte)
        Gesamtpunkte = Meldepunkte + Stichwerte (inkl. gedrückte Karten).
    """
    gesamtpunkte = meldepunkte + stichwerte
    if gesamtpunkte >= reizwert:
        return Rundenausgang.GEWONNENES_SPIEL, gesamtpunkte
    return Rundenausgang.DOPPELTES_ABGEHEN, gesamtpunkte


def meldepunkte_mit_stich_zwang(meldepunkte: int, hat_eigenen_stich: bool) -> int:
    """
    Wendet den Stich-Zwang an: Meldepunkte verfallen ohne eigenen Stich.

    Normativ: docs/rule-set-v1.md §10.
    """
    return meldepunkte if hat_eigenen_stich else 0


def dritten_stichwert_ermitteln(wert1: int, wert2: int) -> int:
    """
    Berechnet den fehlenden dritten Stichwert aus der 250er-Kontrollsumme.

    Normativ: docs/rule-set-v1.md §5.2.
    """
    return STICHWERT_KONTROLLSUMME - wert1 - wert2


def stichwerte_validieren(werte: list[int]) -> None:
    """
    Prüft, ob alle drei Stichwerte zusammen die Kontrollsumme 250 nicht überschreiten.

    Raises:
        UngueltigeStichwerte: Wenn die Summe größer als 250 ist.
    """
    gesamt = sum(werte)
    if gesamt > STICHWERT_KONTROLLSUMME:
        raise UngueltigeStichwerte(
            f"Die Summe der Stichwerte ({gesamt}) überschreitet "
            f"die Kontrollsumme {STICHWERT_KONTROLLSUMME}."
        )


# ── Slice 3: Einfaches Abgehen auswerten ──────────────────────────────────────

def einfaches_abgehen_auswerten(reizwert: int) -> tuple[int, str]:
    """
    Berechnet Verlustwert und Darstellung für einfaches Abgehen.

    Normativ: docs/rule-set-v1.md §11.

    Returns:
        (verlustwert_int, verlustwert_darstellung)
        Beispiel: (-250, '(-250)')
    """
    verlustwert = -reizwert
    darstellung = f"({verlustwert})"
    return verlustwert, darstellung


# ── Slice 4: Doppeltes Abgehen auswerten ──────────────────────────────────────

def doppeltes_abgehen_auswerten(reizwert: int) -> tuple[int, str]:
    """
    Berechnet Verlustwert und Darstellung für doppeltes Abgehen.

    Normativ: docs/rule-set-v1.md §12.

    Returns:
        (verlustwert_int, verlustwert_darstellung)
        Beispiel: (-400, '(-400)') für Reizwert 200.
    """
    verlustwert = -2 * reizwert
    darstellung = f"({verlustwert})"
    return verlustwert, darstellung


# ── Slice 6: Spielende und Siegerermittlung ───────────────────────────────────

def sieger_ermitteln(
    punktestaende: dict[str, int],
    exakte_stichwerte: dict[str, int] | None = None,
) -> list[str]:
    """
    Ermittelt den oder die Sieger nach dem höchsten numerischen Punktestand.

    Normativ: docs/rule-set-v1.md §16.

    Tiebreaking-Regeln:
    - Sterne aus Tausender-Runden beeinflussen den Gesamtsieg nicht.
    - Bei Gleichstand werden exakte 1er-Stichwerte aus der letzten Runde herangezogen.
    - Bleibt danach Gleichstand, gibt es mehrere Sieger.

    Args:
        punktestaende:    Mapping Spielername → numerischer Gesamtpunktestand.
        exakte_stichwerte: Optionale exakte 1er-Stichwerte für Tiebreaking.

    Returns:
        Sortierte Liste der Spielernamen mit dem höchsten Punktestand.
    """
    if not punktestaende:
        return []

    max_punkte = max(punktestaende.values())
    kandidaten = [name for name, p in punktestaende.items() if p == max_punkte]

    if len(kandidaten) > 1 and exakte_stichwerte:
        max_exakt = max(exakte_stichwerte.get(k, 0) for k in kandidaten)
        kandidaten = [k for k in kandidaten if exakte_stichwerte.get(k, 0) == max_exakt]

    return kandidaten

    """
    Legt ein neues V1-Binokel-Spiel an.

    Validierungsregeln (normativ: docs/rule-set-v1.md §2, §3, §4):
    - Es müssen genau 4 Spieler angegeben werden.
    - Die Rundenzahl muss ein Vielfaches von 4 sein.
    - Wird keine Rundenzahl angegeben, gilt der Standardwert 12.

    Args:
        spieler:      Namen der Spieler in Sitzreihenfolge gegen den Uhrzeigersinn.
        rundenanzahl: Gewünschte Rundenanzahl oder None für Standardwert.

    Returns:
        Ein neu angelegtes Spiel-Objekt.

    Raises:
        UngueltigeSpielerzahl:  Wenn nicht genau 4 Spieler angegeben wurden.
        UngueltigeRundenanzahl: Wenn die Rundenzahl kein Vielfaches von 4 ist.
    """
    if len(spieler) != GUELTIGE_SPIELERZAHL:
        raise UngueltigeSpielerzahl(
            f"Ein V1-Spiel erfordert genau {GUELTIGE_SPIELERZAHL} Spieler, "
            f"aber {len(spieler)} wurden angegeben."
        )

    if rundenanzahl is None:
        rundenanzahl = STANDARD_RUNDENANZAHL

    if rundenanzahl % 4 != 0:
        raise UngueltigeRundenanzahl(
            f"Die Rundenzahl muss ein Vielfaches von 4 sein, "
            f"aber {rundenanzahl} wurde angegeben."
        )

    return Spiel(spieler_reihenfolge=spieler, rundenanzahl=rundenanzahl)
