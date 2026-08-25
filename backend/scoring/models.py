"""
Persistenzmodell für den Binokel Score Tracker – V1.

Django ORM-Modelle.  Jede Klasse entspricht einer Datenbanktabelle.
Normative Quelle: docs/datenmodell-v1.puml

Beziehungsstruktur:
    SpielModel 1──* SpielerModel
    SpielModel 1──* RundeModel
    RundeModel 1──* GegenspielerRundeModel
    RundeModel *──1 SpielerModel  (spielmacher, geber)
    GegenspielerRundeModel *──1 SpielerModel
"""
from django.db import models

from scoring.domain import Rundenausgang


# ── Hilfsdaten ─────────────────────────────────────────────────────────────────

_RUNDENAUSGANG_CHOICES: list[tuple[str, str]] = [
    (e.value, e.value) for e in Rundenausgang
]
_RUNDENAUSGANG_MAX_LEN: int = max(len(e.value) for e in Rundenausgang)


# ── Modelle ────────────────────────────────────────────────────────────────────

class SpielModel(models.Model):
    """Repräsentiert ein Binokel-Spiel (Metadaten + Spielerdefinition)."""

    rundenanzahl = models.IntegerField()
    angelegt_am = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Spiel"
        verbose_name_plural = "Spiele"
        ordering = ["-angelegt_am"]

    def __str__(self) -> str:
        return f"Spiel #{self.pk} ({self.rundenanzahl} Runden)"


class SpielerModel(models.Model):
    """
    Ein Spieler innerhalb eines Spiels.

    position: 0..3, Sitzreihenfolge gegen Uhrzeigersinn.
    Der Spieler mit position=0 ist der erste Geber.
    """

    spiel = models.ForeignKey(
        SpielModel, on_delete=models.CASCADE, related_name="spieler"
    )
    name = models.CharField(max_length=100)
    position = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = "Spieler"
        verbose_name_plural = "Spieler"
        ordering = ["spiel", "position"]
        constraints = [
            models.UniqueConstraint(
                fields=["spiel", "position"],
                name="unique_spieler_position_pro_spiel",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} (Pos. {self.position}, Spiel #{self.spiel_id})"


class RundeModel(models.Model):
    """
    Eine einzelne Binokel-Runde mit vollständigem Wertungsergebnis.

    rundenausgang speichert Rundenausgang.value als String (max. 25 Zeichen).
    verlustwert ist bei gewonnenem Spiel 0, bei Abgehen negativ.
    spielmacher_punkte und mitpunkte_pro_gegenspieler sind bei Tausender 0.

    spielmacher_meldepunkte (M) und spielmacher_stichwerte (S) schlüsseln die
    Spielmacher-Punkte für die zweizeilige Anschreibetabelle getrennt auf
    (docs/Anschreibetabelle_4_Spieler.md §5). Invariante an jedem Schreibpfad:
    spielmacher_punkte == spielmacher_meldepunkte + spielmacher_stichwerte.
    Bei Verlust (Abgehen) und Tausender sind alle drei Werte 0.
    """

    spiel = models.ForeignKey(
        SpielModel, on_delete=models.CASCADE, related_name="runden"
    )
    rundennummer = models.PositiveSmallIntegerField()
    reizwert = models.IntegerField()
    rundenausgang = models.CharField(
        max_length=_RUNDENAUSGANG_MAX_LEN + 2,
        choices=_RUNDENAUSGANG_CHOICES,
    )
    spielmacher = models.ForeignKey(
        SpielerModel, on_delete=models.CASCADE, related_name="spielmacher_runden"
    )
    geber = models.ForeignKey(
        SpielerModel, on_delete=models.CASCADE, related_name="geber_runden"
    )
    spielmacher_punkte = models.IntegerField(default=0)
    spielmacher_meldepunkte = models.IntegerField(default=0)
    spielmacher_stichwerte = models.IntegerField(default=0)
    verlustwert = models.IntegerField(default=0)
    mitpunkte_pro_gegenspieler = models.IntegerField(default=0)
    spielmacher_stern = models.BooleanField(default=False)
    gegenspieler_stern = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Runde"
        verbose_name_plural = "Runden"
        ordering = ["spiel", "rundennummer"]
        constraints = [
            models.UniqueConstraint(
                fields=["spiel", "rundennummer"],
                name="unique_rundennummer_pro_spiel",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"Runde {self.rundennummer} von Spiel #{self.spiel_id}"
            f" ({self.rundenausgang})"
        )


class GegenspielerRundeModel(models.Model):
    """
    Wertungsdaten eines einzelnen Gegenspielers für eine Runde.

    hat_eigenen_stich bestimmt, ob die Meldepunkte gewertet werden
    (Stich-Zwang, Ausnahme: einfaches Abgehen).
    """

    runde = models.ForeignKey(
        RundeModel, on_delete=models.CASCADE, related_name="gegenspieler"
    )
    spieler = models.ForeignKey(
        SpielerModel, on_delete=models.CASCADE, related_name="gegenspieler_runden"
    )
    meldepunkte = models.IntegerField(default=0)
    stichwerte = models.IntegerField(default=0)
    hat_eigenen_stich = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Gegenspieler-Runde"
        verbose_name_plural = "Gegenspieler-Runden"
        ordering = ["runde", "spieler__position"]
        constraints = [
            models.UniqueConstraint(
                fields=["runde", "spieler"],
                name="unique_spieler_pro_runde",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.spieler} als Gegenspieler in Runde {self.runde_id}"

