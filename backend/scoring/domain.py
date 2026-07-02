"""
Domänenmodell für den Binokel Score Tracker – V1-Regelwerk.

Dieses Modul enthält ausschließlich fachliche Typen und Wertklassen.
Keine Framework-Abhängigkeiten.  Normative Quelle: docs/rule-set-v1.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# ── Konstanten ─────────────────────────────────────────────────────────────────

STANDARD_RUNDENANZAHL: int = 12
GUELTIGE_SPIELERZAHL: int = 4
STICHWERT_KONTROLLSUMME: int = 250


# ── Fehlerklassen ──────────────────────────────────────────────────────────────

class SpielFehler(ValueError):
    """Basisklasse für alle fachlichen Fehler im Binokel Score Tracker."""


class UngueltigeSpielerzahl(SpielFehler):
    """Wird ausgelöst, wenn die angegebene Spielerzahl nicht 4 beträgt."""


class UngueltigeRundenanzahl(SpielFehler):
    """Wird ausgelöst, wenn die Rundenzahl kein Vielfaches von 4 ist."""


class UngueltigeStichwerte(SpielFehler):
    """Wird ausgelöst, wenn die Summe aller drei Stichwerte 250 überschreitet."""


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
    Repräsentiert ein laufendes oder abgeschlossenes Binokel-Spiel.

    Attribute:
        spieler_reihenfolge: Namen der Spieler in Sitzreihenfolge gegen den
                             Uhrzeigersinn.  Der erste Eintrag ist der erste Geber.
        rundenanzahl:        Geplante Gesamtzahl der Runden (Vielfaches von 4).
    """

    spieler_reihenfolge: list[str]
    rundenanzahl: int

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
            0 beginnt – das ist eine Rotation.

            Beispiel mit spieler_reihenfolge = ["Anna", "Bernd", "Carla", "Dirk"]:

                Runde 1:  (1 - 1) % 4 =  0 % 4 = 0  → Anna
                Runde 2:  (2 - 1) % 4 =  1 % 4 = 1  → Bernd
                Runde 3:  (3 - 1) % 4 =  2 % 4 = 2  → Carla
                Runde 4:  (4 - 1) % 4 =  3 % 4 = 3  → Dirk
                Runde 5:  (5 - 1) % 4 =  4 % 4 = 0  → Anna  ← Neustart
                Runde 13: (13- 1) % 4 = 12 % 4 = 0  → Anna  ← 3. Durchgang
        """
        index = (runde - 1) % len(self.spieler_reihenfolge)
        return self.spieler_reihenfolge[index]
