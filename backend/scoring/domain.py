"""
Domänenmodell für den Binokel Score Tracker – V1-Regelwerk.

Dieses Modul enthält ausschließlich fachliche Typen und Wertklassen.
Keine Framework-Abhängigkeiten.  Normative Quelle: docs/rule-set-v1.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# ── Konstanten ─────────────────────────────────────────────────────────────────

STANDARD_RUNDENANZAHL: int = 12  # durch 3 und 4 teilbar, also für beide Varianten gültig

# Unterstützte Spielerzahlen (ADR-017, normativ: docs/rule-set-v1.md §2). Die Spielerzahl
# bestimmt die Variante: bei 4 Spielern setzt der Geber aus, bei 3 Spielern spielt er mit.
GUELTIGE_SPIELERZAHLEN: tuple[int, ...] = (3, 4)
SPIELERZAHL_MIT_AUSSETZENDEM_GEBER: int = 4

STICHWERT_KONTROLLSUMME: int = 250

# Einsatz der Abrechnung (normativ: docs/rule-set-v1.md §20): 5 Cent je 10 Punkte Differenz zum
# Höchststand. Beträge werden durchgängig in ganzen Cent geführt. Da der STAND in Zehnern geführt
# wird (§9.1), ist die Differenz ein Vielfaches von 10 und der Betrag exakt darstellbar.
ABRECHNUNG_CENT: int = 5
ABRECHNUNG_PUNKTE: int = 10

# Alle Werte, die in den kumulierten STAND einfließen (Stichwerte, Meldepunkte,
# Reizwert), werden in vollen Zehnern geführt. 1er-genaue Werte gibt es nur in der
# letzten Runde für den Gleichstand-Tiebreak (normativ: docs/rule-set-v1.md §9.1/§9.4).
ZEHNER_SCHRITT: int = 10

# Höchstmögliche Meldung eines einzelnen Spielers (württembergisches Doppelblatt):
# doppelte Familie einer Farbe (1500) + doppelter Binokel (300); die beiden Blatt-Ober
# der Familie bilden zugleich den doppelten Binokel. Normativ: docs/rule-set-v1.md §7.1.
MELDEPUNKTE_MAXIMUM: int = 1800


# ── Fehlerklassen ──────────────────────────────────────────────────────────────

class SpielFehler(ValueError):
    """Basisklasse für alle fachlichen Fehler im Binokel Score Tracker."""


class UngueltigeSpielerzahl(SpielFehler):
    """Wird ausgelöst, wenn die Spielerzahl weder 3 noch 4 beträgt."""


class UngueltigeRundenanzahl(SpielFehler):
    """Wird ausgelöst, wenn die Rundenzahl kein Vielfaches der Spielerzahl ist."""


class UnbekannterSpieler(SpielFehler):
    """Wird ausgelöst, wenn ein Name nicht zur Spielerreihenfolge des Spiels gehört."""


class UngueltigerSpielmacher(SpielFehler):
    """Wird ausgelöst, wenn der Spielmacher in der Runde nicht aktiv mitspielt.

    Das betrifft ausschließlich den aussetzenden Geber (nur bei 4 Spielern;
    normativ: docs/rule-set-v1.md §3.4).
    """


class UngueltigeStichwerte(SpielFehler):
    """Wird ausgelöst, wenn die Summe aller drei Stichwerte 250 überschreitet
    oder ein Stichwert kein Vielfaches von 10 ist (normativ: §9.1/§9.4)."""


class UngueltigerZehnerwert(SpielFehler):
    """Wird ausgelöst, wenn ein Wert, der in den STAND einfließt (Reizwert oder
    Meldepunkte), kein Vielfaches von 10 ist (normativ: docs/rule-set-v1.md §9.1/§9.4)."""


class UngueltigeMeldepunkte(SpielFehler):
    """Wird ausgelöst, wenn die Meldepunkte eines Spielers unplausibel sind
    (negativ oder größer als das theoretische Maximum von 1800)."""


# ── Enumerationen ──────────────────────────────────────────────────────────────

class Rundenausgang(Enum):
    """Mögliche Ausgänge einer Binokel-Runde."""

    GEWONNENES_SPIEL = "gewonnenes Spiel"
    DOPPELTES_ABGEHEN = "doppeltes Abgehen"
    EINFACHES_ABGEHEN = "einfaches Abgehen"
    TAUSENDER_GEWONNEN = "Tausender gewonnen"
    TAUSENDER_VERLOREN = "Tausender verloren"


# ── Domänenmodell ──────────────────────────────────────────────────────────────

@dataclass
class Spiel:
    """
    Repräsentiert ein laufendes oder abgeschlossenes Binokel-Spiel mit 3 oder 4 Spielern.

    Die Spielerzahl bestimmt die Variante (ADR-017): Bei 4 Spielern setzt der Geber aus,
    bei 3 Spielern spielt er mit. In beiden Varianten sind pro Runde genau drei Spieler
    aktiv. Die Frage „wer ist aktiv?“ wird ausschließlich hier beantwortet.

    Attribute:
        spieler_reihenfolge: Namen der Spieler in Sitzreihenfolge gegen den
                             Uhrzeigersinn.  Der erste Eintrag ist der erste Geber.
        rundenanzahl:        Geplante Gesamtzahl der Runden (Vielfaches der Spielerzahl).
    """

    spieler_reihenfolge: list[str]
    rundenanzahl: int

    @property
    def geber_setzt_aus(self) -> bool:
        """True bei 4 Spielern (der Geber setzt aus), False bei 3 (der Geber spielt mit)."""
        return len(self.spieler_reihenfolge) == SPIELERZAHL_MIT_AUSSETZENDEM_GEBER

    def aktive_spieler(self, geber: str) -> list[str]:
        """
        Die in der Runde aktiv mitspielenden Spieler – in Sitzreihenfolge.

        Bei 4 Spielern alle außer dem aussetzenden Geber, bei 3 Spielern alle.
        Es sind in beiden Varianten genau drei.

        Raises:
            UnbekannterSpieler: Wenn der Geber nicht zum Spiel gehört.
        """
        self._muss_mitspieler_sein(geber)
        if not self.geber_setzt_aus:
            return list(self.spieler_reihenfolge)
        return [name for name in self.spieler_reihenfolge if name != geber]

    def gegenspieler(self, geber: str, spielmacher: str) -> list[str]:
        """
        Die beiden Gegenspieler: die aktiven Spieler ohne den Spielmacher.

        Raises:
            UnbekannterSpieler:      Wenn Geber oder Spielmacher nicht zum Spiel gehören.
            UngueltigerSpielmacher:  Wenn der Spielmacher nicht aktiv ist, also der
                                     aussetzende Geber (nur bei 4 Spielern).
        """
        aktive = self.aktive_spieler(geber)
        self._muss_mitspieler_sein(spielmacher)
        if spielmacher not in aktive:
            raise UngueltigerSpielmacher(
                f"Der Spielmacher darf nicht der Geber sein (Geber '{geber}' setzt aus)."
            )
        return [name for name in aktive if name != spielmacher]

    def _muss_mitspieler_sein(self, name: str) -> None:
        if name not in self.spieler_reihenfolge:
            raise UnbekannterSpieler(f"'{name}' gehört nicht zu diesem Spiel.")

    def geber_in_runde(self, runde: int) -> str:
        """
        Gibt den Namen des Gebers in der angegebenen Runde zurück.

        Args:
            runde: 1-basierte Rundennummer.

        Returns:
            Name des Gebers gemäß Rotation entlang der Spielerreihenfolge.

        Algorithmus – Modulo-Rotation:
            Runden sind 1-basiert, Listen-Indizes 0-basiert.
            Das „- 1" verschiebt die Basis:  Runde 1 → Index 0 (Anna).

            Der Modulo-Operator „%" gibt den Rest einer Division zurück und
            sorgt dafür, dass der Index nach dem letzten Spieler wieder bei
            0 beginnt – das ist eine Rotation über die tatsächliche Spielerzahl.

            Beispiel mit 4 Spielern ["Anna", "Bernd", "Carla", "Dirk"]:

                Runde 1:  (1 - 1) % 4 =  0 % 4 = 0  → Anna
                Runde 4:  (4 - 1) % 4 =  3 % 4 = 3  → Dirk
                Runde 5:  (5 - 1) % 4 =  4 % 4 = 0  → Anna  ← Neustart

            Beispiel mit 3 Spielern ["Anna", "Bernd", "Carla"]:

                Runde 3:  (3 - 1) % 3 =  2 % 3 = 2  → Carla
                Runde 4:  (4 - 1) % 3 =  3 % 3 = 0  → Anna  ← Neustart
        """
        index = (runde - 1) % len(self.spieler_reihenfolge)
        return self.spieler_reihenfolge[index]
