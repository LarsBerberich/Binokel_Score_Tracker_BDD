"""
Anwendungsfälle (Use Cases) für den Binokel Score Tracker.

Jede Funktion entspricht einem fachlichen Anwendungsfall aus der Gherkin-Spezifikation.
Normative Quelle: docs/rule-set-v1.md.
"""
from __future__ import annotations

from scoring.domain import (
    GegenspielerWertung,
    Rundenwertung,
    Spiel,
    Rundenausgang,
    STANDARD_RUNDENANZAHL,
    ABRECHNUNG_CENT,
    ABRECHNUNG_PUNKTE,
    GUELTIGE_SPIELERZAHLEN,
    STICHWERT_KONTROLLSUMME,
    MELDEPUNKTE_MAXIMUM,
    ZEHNER_SCHRITT,
    UngueltigeSpielerzahl,
    UngueltigeRundenanzahl,
    UngueltigeStichwerte,
    UngueltigeMeldepunkte,
    UngueltigeRundeneingabe,
    UngueltigerZehnerwert,
)


# ── Slice 1: Spiel anlegen ─────────────────────────────────────────────────────

def spiel_anlegen(
    spieler: list[str],
    rundenanzahl: int | None = None,
) -> Spiel:
    """
    Legt ein neues V1-Binokel-Spiel an.

    Validierungsregeln (normativ: docs/rule-set-v1.md §2, §3, §4; ADR-017):
    - Es müssen 3 oder 4 Spieler angegeben werden; die Anzahl bestimmt die Variante
      (4 Spieler: der Geber setzt aus, 3 Spieler: der Geber spielt mit).
    - Die Rundenzahl muss ein Vielfaches der Spielerzahl sein, damit jeder Spieler
      gleich oft Geber ist.
    - Wird keine Rundenzahl angegeben, gilt der Standardwert 12 (durch 3 und 4 teilbar).

    Raises:
        UngueltigeSpielerzahl:  Wenn nicht genau 3 oder 4 Spieler angegeben wurden.
        UngueltigeRundenanzahl: Wenn die Rundenzahl kein Vielfaches der Spielerzahl ist.
    """
    if len(spieler) not in GUELTIGE_SPIELERZAHLEN:
        gueltig = " oder ".join(str(n) for n in GUELTIGE_SPIELERZAHLEN)
        raise UngueltigeSpielerzahl(
            f"Ein Spiel erfordert {gueltig} Spieler, "
            f"aber {len(spieler)} wurden angegeben."
        )

    if rundenanzahl is None:
        rundenanzahl = STANDARD_RUNDENANZAHL

    if rundenanzahl % len(spieler) != 0:
        raise UngueltigeRundenanzahl(
            f"Die Rundenzahl muss bei {len(spieler)} Spielern ein Vielfaches von "
            f"{len(spieler)} sein, aber {rundenanzahl} wurde angegeben."
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
    Prüft die Stichwerte, die in den STAND einfließen.

    Zwei Regeln (normativ: docs/rule-set-v1.md §9.1/§9.4):
    - Die Summe aller Stichwerte darf die Kontrollsumme 250 nicht überschreiten.
    - Jeder einzelne Stichwert muss ein Vielfaches von 10 sein (Zehner-Eingabe);
      1er-genaue Werte gibt es nur für den Endrunden-Tiebreak (§9.4) und fließen
      nicht in den STAND ein.

    Raises:
        UngueltigeStichwerte: Wenn die Summe > 250 ist oder ein Wert kein Zehner ist.
    """
    gesamt = sum(werte)
    if gesamt > STICHWERT_KONTROLLSUMME:
        raise UngueltigeStichwerte(
            f"Die Summe der Stichwerte ({gesamt}) überschreitet "
            f"die Kontrollsumme {STICHWERT_KONTROLLSUMME}."
        )
    for wert in werte:
        if wert % ZEHNER_SCHRITT != 0:
            raise UngueltigeStichwerte(
                f"Der Stichwert {wert} ist kein Vielfaches von {ZEHNER_SCHRITT}. "
                "In den STAND einfließende Stichwerte werden in vollen Zehnern erfasst."
            )


def zehnerwert_validieren(wert: int, bezeichnung: str = "Wert") -> None:
    """
    Prüft, ob ein in den STAND einfließender Wert (Reizwert oder Meldepunkte) ein
    Vielfaches von 10 ist (normativ: docs/rule-set-v1.md §9.1/§9.4).

    Raises:
        UngueltigerZehnerwert: Wenn der Wert kein Vielfaches von 10 ist.
    """
    if wert % ZEHNER_SCHRITT != 0:
        raise UngueltigerZehnerwert(
            f"{bezeichnung} ({wert}) muss ein Vielfaches von {ZEHNER_SCHRITT} sein."
        )


def meldepunkte_validieren(meldepunkte: int) -> None:
    """
    Plausibilitätsprüfung für die Meldepunkte eines einzelnen Spielers.

    Die höchstmögliche Meldung im Binokel beträgt 1800 Punkte (doppelte Familie
    einer Farbe = 1500 + doppelter Binokel = 300). Ein höherer oder negativer Wert
    ist ein Eingabefehler.

    Normativ: docs/rule-set-v1.md §7.1.

    Raises:
        UngueltigeMeldepunkte: Wenn die Meldepunkte negativ sind oder 1800 überschreiten.
    """
    if meldepunkte < 0 or meldepunkte > MELDEPUNKTE_MAXIMUM:
        raise UngueltigeMeldepunkte(
            f"Die Meldepunkte eines Spielers ({meldepunkte}) müssen zwischen 0 "
            f"und {MELDEPUNKTE_MAXIMUM} liegen."
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


# ── Abrechnung (rule-set §20) ─────────────────────────────────────────────────

def abrechnung_ermitteln(punktestaende: dict[str, int]) -> dict[str, int]:
    """
    Berechnet, wie viel jeder Spieler zahlen müsste, wenn das Spiel jetzt zu Ende wäre.

    Normativ: docs/rule-set-v1.md §20. Basis ist der höchste Punktestand; jeder Spieler zahlt
    ``ABRECHNUNG_CENT`` (5) Cent je ``ABRECHNUNG_PUNKTE`` (10) Punkte Differenz zum Höchststand.
    Der Spitzenreiter zahlt nichts, bei Gleichstand an der Spitze zahlen alle Spitzenreiter
    nichts. Sterne fließen nicht ein.

    Der STAND wird in Zehnern geführt (§9.1), die Differenz ist also ein Vielfaches von 10 und der
    Betrag exakt in ganzen Cent darstellbar. Nur für Altbestand mit Einerstellen (vor der
    Zehner-Regel) wird kaufmännisch auf ganze Cent gerundet (halbe Cent aufrunden).

    Args:
        punktestaende: Mapping Spielername → numerischer Punktestand (kann negativ sein).

    Returns:
        Mapping Spielername → Betrag in **ganzen Cent** (immer ≥ 0). Leeres Mapping bei
        leerer Eingabe.
    """
    if not punktestaende:
        return {}
    hoechststand = max(punktestaende.values())
    return {
        name: ((hoechststand - stand) * ABRECHNUNG_CENT + ABRECHNUNG_PUNKTE // 2)
        // ABRECHNUNG_PUNKTE
        for name, stand in punktestaende.items()
    }


# ── Slices 2–5: Runde aus der Eingabe auswerten ───────────────────────────────

def _pflichtfeld(eingabe: dict, *felder: str) -> str | None:
    """Gibt den Namen des ersten fehlenden Pflichtfelds zurück, oder None."""
    for feld in felder:
        if feld not in eingabe:
            return feld
    return None


def _meldepunkte_pruefen(eingabe: dict) -> None:
    """Validiert alle in der Eingabe enthaltenen Meldepunkte (Spielmacher + Gegenspieler).

    Plausibilitätsgrenze (normativ: docs/rule-set-v1.md §7.1).
    """
    if "meldepunkte" in eingabe:
        meldepunkte_validieren(eingabe["meldepunkte"])
    for gegenspieler in eingabe.get("gegenspieler", []):
        if isinstance(gegenspieler, dict) and "meldepunkte" in gegenspieler:
            meldepunkte_validieren(gegenspieler["meldepunkte"])


def _zehner_und_kontrollsumme_pruefen(eingabe: dict, *, mit_spielmacher_stichwert: bool) -> None:
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
    if "reizwert" in eingabe:
        zehnerwert_validieren(eingabe["reizwert"], "Reizwert")
    if "meldepunkte" in eingabe:
        zehnerwert_validieren(eingabe["meldepunkte"], "Meldepunkte")
    for gs in eingabe.get("gegenspieler", []):
        if isinstance(gs, dict) and "meldepunkte" in gs:
            zehnerwert_validieren(gs["meldepunkte"], "Meldepunkte")

    stichwerte = [
        gs["stichwerte"]
        for gs in eingabe.get("gegenspieler", [])
        if isinstance(gs, dict) and "stichwerte" in gs
    ]
    if mit_spielmacher_stichwert and "stichwerte" in eingabe:
        stichwerte.append(eingabe["stichwerte"])
    if stichwerte:
        stichwerte_validieren(stichwerte)


def rollen_pruefen(spiel: Spiel, geber: str, spielmacher: str) -> None:
    """Der Spielmacher muss aktiv mitspielen (rule-set-v1.md §3.4, ADR-017).

    Bei 4 Spielern setzt der Geber aus und kann nicht Spielmacher sein; bei 3 Spielern
    spielt er mit. Die Regel beantwortet das Domänenobjekt.

    Raises:
        UnbekannterSpieler:     Geber oder Spielmacher gehören nicht zum Spiel.
        UngueltigerSpielmacher: Der Spielmacher setzt aus.
    """
    spiel.gegenspieler(geber, spielmacher)


def runde_auswerten(eingabe: dict) -> Rundenwertung:
    """Validiert und wertet eine Runde nach Typ – gemeinsam für Anlegen (POST) und Korrektur (PUT).

    Führt Meldepunkte-Plausibilität (§7.1), Zehner-/Kontrollsummen-Prüfung (§9.1/§9.4),
    den Typ-Dispatch inkl. Stern- und Gegenspieler-Zeilen-Logik (HOCH-3) sowie die
    Spielmacher-M|S-Invariante (HOCH-1: ``spielmacher_punkte == spielmacher_meldepunkte +
    spielmacher_stichwerte``) an EINER Stelle aus. Dadurch durchläuft die Korrektur exakt
    dieselbe Wertung wie das Anlegen.

    Args:
        eingabe: Rundendaten mit mindestens dem Feld ``typ`` (normal, einfaches_abgehen,
            doppeltes_abgehen, tausender_gewonnen, tausender_verloren) und den Feldern des Typs.

    Raises:
        UngueltigeRundeneingabe: Pflichtfeld fehlt oder Rundentyp unbekannt.
        UngueltigeMeldepunkte:   Meldepunkte negativ oder über 1800.
        UngueltigerZehnerwert:   Reizwert/Meldepunkte kein Zehner.
        UngueltigeStichwerte:    Stichwert kein Zehner oder Summe > 250.
    """
    typ: str = eingabe["typ"]
    spielmacher_stern: bool = eingabe.get("spielmacher_stern", False)
    gegenspieler_stern: bool = eingabe.get("gegenspieler_stern", False)

    # Spielmacher-M/S für die getrennte Anschreibetabelle (§5). Invariante:
    # bei gewonnenem Spiel gilt spielmacher_punkte == spielmacher_meldepunkte
    # + spielmacher_stichwerte. Bei einfachem Abgehen und Tausender bleiben beide 0.
    # Bei doppeltem Abgehen tragen sie die roh erfassten (fachlich verfallenen) Werte
    # als Korrektur-/Nachvollziehbarkeits-Beleg (FND-004; siehe Zweig unten).
    spielmacher_meldepunkte = 0
    spielmacher_stichwerte = 0

    # Plausibilitätsgrenze der Meldepunkte prüfen (normativ: rule-set-v1.md §7.1).
    _meldepunkte_pruefen(eingabe)

    # ── Dispatch nach Rundentyp ────────────────────────────────────────────────

    if typ == "normal":
        fehlendes = _pflichtfeld(eingabe, "reizwert", "meldepunkte", "stichwerte",
                                 "hat_eigenen_stich", "gegenspieler")
        if fehlendes:
            raise UngueltigeRundeneingabe(
                f"Pflichtfeld fehlt für typ 'normal': '{fehlendes}'."
            )

        # Zehner-Eingabe + 250-Kontrollsumme erzwingen (normativ: §9.1/§9.4).
        _zehner_und_kontrollsumme_pruefen(eingabe, mit_spielmacher_stichwert=True)

        sm_melde = meldepunkte_mit_stich_zwang(
            eingabe["meldepunkte"], eingabe["hat_eigenen_stich"]
        )
        ausgang, gesamtpunkte = normales_spiel_auswerten(
            eingabe["reizwert"], sm_melde, eingabe["stichwerte"]
        )

        if ausgang == Rundenausgang.GEWONNENES_SPIEL:
            spielmacher_punkte = gesamtpunkte
            verlustwert = 0
            mitpunkte = 0
            # Getrennte M|S nur bei gewonnenem Spiel; Invariante M+S == Punkte (§5).
            spielmacher_meldepunkte = sm_melde
            spielmacher_stichwerte = eingabe["stichwerte"]
        else:  # doppeltes Abgehen
            spielmacher_punkte = 0
            verlustwert, _ = doppeltes_abgehen_auswerten(eingabe["reizwert"])
            mitpunkte = 30
            # FND-004: Roh erfasste (fachlich verfallene) M|S des Spielmachers als
            # Korrektur-/Nachvollziehbarkeits-Beleg persistieren. Sie fließen NICHT in
            # den STAND ein (dort zählt allein verlustwert) und werden in der Anschreibetabelle
            # durch die Verlustdarstellung (-x)|0|0 ersetzt. Deshalb gilt die Summen-
            # Invariante hier bewusst NICHT (spielmacher_punkte == 0).
            spielmacher_meldepunkte = sm_melde
            spielmacher_stichwerte = eingabe["stichwerte"]

        gegenspieler = tuple(
            GegenspielerWertung(
                name=gs["name"],
                meldepunkte=meldepunkte_mit_stich_zwang(
                    gs["meldepunkte"], gs["hat_eigenen_stich"]
                ),
                stichwerte=gs["stichwerte"],
                hat_eigenen_stich=gs["hat_eigenen_stich"],
            )
            for gs in eingabe["gegenspieler"]
        )

    elif typ == "einfaches_abgehen":
        fehlendes = _pflichtfeld(eingabe, "reizwert", "gegenspieler")
        if fehlendes:
            raise UngueltigeRundeneingabe(
                f"Pflichtfeld fehlt für typ 'einfaches_abgehen': '{fehlendes}'."
            )

        ausgang = Rundenausgang.EINFACHES_ABGEHEN
        spielmacher_punkte = 0
        verlustwert, _ = einfaches_abgehen_auswerten(eingabe["reizwert"])
        mitpunkte = 30

        # Kein Stich-Zwang für Gegenspieler (normativ: rule-set-v1.md §13.4)
        gegenspieler = tuple(
            GegenspielerWertung(
                name=gs["name"],
                meldepunkte=gs["meldepunkte"],
                stichwerte=0,
                hat_eigenen_stich=gs.get("hat_eigenen_stich", False),
            )
            for gs in eingabe["gegenspieler"]
        )

    elif typ == "doppeltes_abgehen":
        fehlendes = _pflichtfeld(eingabe, "reizwert", "gegenspieler")
        if fehlendes:
            raise UngueltigeRundeneingabe(
                f"Pflichtfeld fehlt für typ 'doppeltes_abgehen': '{fehlendes}'."
            )

        # Zehner-Eingabe + 250-Kontrollsumme erzwingen; Spielmacher-Stichwert verfällt (§9.1/§9.4).
        _zehner_und_kontrollsumme_pruefen(eingabe, mit_spielmacher_stichwert=False)

        ausgang = Rundenausgang.DOPPELTES_ABGEHEN
        spielmacher_punkte = 0
        verlustwert, _ = doppeltes_abgehen_auswerten(eingabe["reizwert"])
        mitpunkte = 30

        # Normaler Stich-Zwang gilt (normativ: rule-set-v1.md §14.4)
        gegenspieler = tuple(
            GegenspielerWertung(
                name=gs["name"],
                meldepunkte=meldepunkte_mit_stich_zwang(
                    gs["meldepunkte"], gs["hat_eigenen_stich"]
                ),
                stichwerte=gs["stichwerte"],
                hat_eigenen_stich=gs["hat_eigenen_stich"],
            )
            for gs in eingabe["gegenspieler"]
        )

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
        gegenspieler = ()

    else:
        raise UngueltigeRundeneingabe(
            f"Unbekannter Rundentyp: '{typ}'. "
            "Erlaubt: normal, einfaches_abgehen, doppeltes_abgehen, "
            "tausender_gewonnen, tausender_verloren."
        )

    return Rundenwertung(
        rundenausgang=ausgang,
        spielmacher_punkte=spielmacher_punkte,
        verlustwert=verlustwert,
        mitpunkte_pro_gegenspieler=mitpunkte,
        spielmacher_stern=spielmacher_stern,
        gegenspieler_stern=gegenspieler_stern,
        spielmacher_meldepunkte=spielmacher_meldepunkte,
        spielmacher_stichwerte=spielmacher_stichwerte,
        gegenspieler=gegenspieler,
    )
