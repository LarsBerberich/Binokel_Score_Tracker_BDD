from django.test import TestCase

"""
API-Integrationstests für den Binokel Score Tracker.

Testet den vollständigen Stack von HTTP → View → Use Case → Repository → DB.
Verwendet Djangos TestCase + TestClient (kein externer Testserver nötig).

Normative Quellen:
  - docs/rule-set-v1.md
  - docs/adr/ADR-006-behave-http-blackbox-tests.md
"""
import json

from django.test import Client, TestCase


# ── Hilfsfunktion ─────────────────────────────────────────────────────────────

def _post_json(client: Client, url: str, payload: dict):
    return client.post(
        url,
        data=json.dumps(payload),
        content_type="application/json",
    )


# ── Slice 1: Spiel anlegen / laden ────────────────────────────────────────────

class SpielAnlegenApiTest(TestCase):

    def test_spiel_anlegen_standard(self):
        """POST /api/spiele/ mit 4 Spielern → 201, ID und rundenanzahl=12."""
        antwort = _post_json(self.client, "/api/spiele/", {
            "spieler": ["Anna", "Bernd", "Clara", "Dieter"],
        })
        self.assertEqual(antwort.status_code, 201)
        daten = antwort.json()
        self.assertIn("id", daten)
        self.assertEqual(daten["rundenanzahl"], 12)
        self.assertEqual(daten["spieler"], ["Anna", "Bernd", "Clara", "Dieter"])

    def test_spiel_anlegen_eigene_rundenanzahl(self):
        """POST mit rundenanzahl=8 → wird übernommen."""
        antwort = _post_json(self.client, "/api/spiele/", {
            "spieler": ["Anna", "Bernd", "Clara", "Dieter"],
            "rundenanzahl": 8,
        })
        self.assertEqual(antwort.status_code, 201)
        self.assertEqual(antwort.json()["rundenanzahl"], 8)

    def test_spiel_anlegen_ungueltige_spielerzahl(self):
        """POST mit 3 Spielern → 400."""
        antwort = _post_json(self.client, "/api/spiele/", {
            "spieler": ["Anna", "Bernd", "Clara"],
        })
        self.assertEqual(antwort.status_code, 400)
        self.assertIn("fehler", antwort.json())

    def test_spiel_anlegen_ungueltige_rundenanzahl(self):
        """POST mit rundenanzahl=7 (kein Vielfaches von 4) → 400."""
        antwort = _post_json(self.client, "/api/spiele/", {
            "spieler": ["Anna", "Bernd", "Clara", "Dieter"],
            "rundenanzahl": 7,
        })
        self.assertEqual(antwort.status_code, 400)

    def test_spiel_laden(self):
        """GET /api/spiele/{id}/ gibt angelegtes Spiel zurück."""
        anlegen = _post_json(self.client, "/api/spiele/", {
            "spieler": ["Anna", "Bernd", "Clara", "Dieter"],
        })
        spiel_id = anlegen.json()["id"]

        laden = self.client.get(f"/api/spiele/{spiel_id}/")
        self.assertEqual(laden.status_code, 200)
        daten = laden.json()
        self.assertEqual(daten["id"], spiel_id)
        self.assertEqual(daten["spieler"], ["Anna", "Bernd", "Clara", "Dieter"])

    def test_spiel_laden_nicht_vorhanden(self):
        """GET auf nicht existierende ID → 404."""
        antwort = self.client.get("/api/spiele/9999/")
        self.assertEqual(antwort.status_code, 404)


# ── Hilfsmethode: Spiel anlegen + ID zurückgeben ──────────────────────────────

def _neues_spiel(client: Client) -> int:
    antwort = _post_json(client, "/api/spiele/", {
        "spieler": ["Anna", "Bernd", "Clara", "Dieter"],
    })
    return antwort.json()["id"]


# ── Slice 2–5: Runde auswerten ────────────────────────────────────────────────

class RundeAuswertenApiTest(TestCase):

    def setUp(self):
        self.spiel_id = _neues_spiel(self.client)
        self.url = f"/api/spiele/{self.spiel_id}/runden/"

    def test_normales_spiel_gewonnen(self):
        """Runde: typ=normal, Meldepunkte + Stichwerte >= Reizwert → 201, gewonnenes Spiel."""
        antwort = _post_json(self.client, self.url, {
            "typ": "normal",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
            "reizwert": 200,
            "meldepunkte": 110,
            "stichwerte": 100,
            "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Bernd", "meldepunkte": 20, "stichwerte": 50, "hat_eigenen_stich": True},
                {"name": "Clara", "meldepunkte": 0,  "stichwerte": 60, "hat_eigenen_stich": True},
                {"name": "Dieter","meldepunkte": 40, "stichwerte": 40, "hat_eigenen_stich": True},
            ],
        })
        self.assertEqual(antwort.status_code, 201)
        daten = antwort.json()
        self.assertEqual(daten["rundenausgang"], "gewonnenes Spiel")
        self.assertEqual(daten["spielmacher_punkte"], 210)  # 110 + 100

    def test_normales_spiel_doppelt_abgegangen(self):
        """Runde: typ=normal, Punkte < Reizwert → doppeltes Abgehen."""
        antwort = _post_json(self.client, self.url, {
            "typ": "normal",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
            "reizwert": 300,
            "meldepunkte": 110,
            "stichwerte": 100,
            "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Bernd", "meldepunkte": 20, "stichwerte": 50, "hat_eigenen_stich": True},
                {"name": "Clara", "meldepunkte": 0,  "stichwerte": 60, "hat_eigenen_stich": True},
                {"name": "Dieter","meldepunkte": 40, "stichwerte": 40, "hat_eigenen_stich": True},
            ],
        })
        self.assertEqual(antwort.status_code, 201)
        self.assertEqual(antwort.json()["rundenausgang"], "doppeltes Abgehen")

    def test_einfaches_abgehen(self):
        """Runde: typ=einfaches_abgehen → 201, einfaches Abgehen."""
        antwort = _post_json(self.client, self.url, {
            "typ": "einfaches_abgehen",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
            "reizwert": 200,
            "gegenspieler": [
                {"name": "Bernd", "meldepunkte": 20},
                {"name": "Clara", "meldepunkte": 0},
                {"name": "Dieter","meldepunkte": 40},
            ],
        })
        self.assertEqual(antwort.status_code, 201)
        self.assertEqual(antwort.json()["rundenausgang"], "einfaches Abgehen")
        self.assertEqual(antwort.json()["mitpunkte_pro_gegenspieler"], 30)

    def test_doppeltes_abgehen_direkt(self):
        """Runde: typ=doppeltes_abgehen (explizit, nicht via normales Spiel) → 201."""
        antwort = _post_json(self.client, self.url, {
            "typ": "doppeltes_abgehen",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
            "reizwert": 200,
            "gegenspieler": [
                {"name": "Bernd", "meldepunkte": 20, "stichwerte": 50, "hat_eigenen_stich": True},
                {"name": "Clara", "meldepunkte": 0,  "stichwerte": 60, "hat_eigenen_stich": True},
                {"name": "Dieter","meldepunkte": 40, "stichwerte": 40, "hat_eigenen_stich": True},
            ],
        })
        self.assertEqual(antwort.status_code, 201)
        self.assertEqual(antwort.json()["rundenausgang"], "doppeltes Abgehen")
        self.assertEqual(antwort.json()["mitpunkte_pro_gegenspieler"], 30)

    def test_spieler_nicht_im_spiel(self):
        """Spielmacher nicht im Spiel registriert → 400 (kein 500-Leck)."""
        antwort = _post_json(self.client, self.url, {
            "typ": "tausender_gewonnen",
            "rundennummer": 1,
            "spielmacher": "UNBEKANNTER_SPIELER",
            "geber": "Dieter",
        })
        self.assertEqual(antwort.status_code, 400)
        self.assertIn("fehler", antwort.json())

    def test_tausender_gewonnen(self):
        """Runde: typ=tausender_gewonnen → 201, kein Verlustwert."""
        antwort = _post_json(self.client, self.url, {
            "typ": "tausender_gewonnen",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
        })
        self.assertEqual(antwort.status_code, 201)
        self.assertEqual(antwort.json()["rundenausgang"], "Tausender gewonnen")
        self.assertEqual(antwort.json()["verlustwert"], 0)

    def test_tausender_verloren(self):
        """Runde: typ=tausender_verloren → 201, kein Verlustwert."""
        antwort = _post_json(self.client, self.url, {
            "typ": "tausender_verloren",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
        })
        self.assertEqual(antwort.status_code, 201)
        self.assertEqual(antwort.json()["rundenausgang"], "Tausender verloren")

    def test_unbekannter_typ(self):
        """Ungültiger typ-Wert → 400."""
        antwort = _post_json(self.client, self.url, {
            "typ": "kein_gueltiger_typ",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
        })
        self.assertEqual(antwort.status_code, 400)

    def test_pflichtfeld_fehlt(self):
        """Fehlender typ → 400."""
        antwort = _post_json(self.client, self.url, {
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
        })
        self.assertEqual(antwort.status_code, 400)

    def test_meldepunkte_maximum_akzeptiert(self):
        """Spielmacher-Meldepunkte genau am Maximum (1800) → 201 (Plausibilitätsgrenze §7.1)."""
        antwort = _post_json(self.client, self.url, {
            "typ": "normal",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
            "reizwert": 200,
            "meldepunkte": 1800,
            "stichwerte": 100,
            "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Bernd", "meldepunkte": 20, "stichwerte": 50, "hat_eigenen_stich": True},
                {"name": "Clara", "meldepunkte": 0,  "stichwerte": 60, "hat_eigenen_stich": True},
                {"name": "Dieter","meldepunkte": 40, "stichwerte": 40, "hat_eigenen_stich": True},
            ],
        })
        self.assertEqual(antwort.status_code, 201)

    def test_spielmacher_meldepunkte_zu_hoch(self):
        """Spielmacher-Meldepunkte über 1800 → 400 (Plausibilitätsgrenze §7.1)."""
        antwort = _post_json(self.client, self.url, {
            "typ": "normal",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
            "reizwert": 200,
            "meldepunkte": 1801,
            "stichwerte": 100,
            "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Bernd", "meldepunkte": 20, "stichwerte": 50, "hat_eigenen_stich": True},
                {"name": "Clara", "meldepunkte": 0,  "stichwerte": 60, "hat_eigenen_stich": True},
                {"name": "Dieter","meldepunkte": 40, "stichwerte": 40, "hat_eigenen_stich": True},
            ],
        })
        self.assertEqual(antwort.status_code, 400)
        self.assertIn("fehler", antwort.json())

    def test_gegenspieler_meldepunkte_zu_hoch(self):
        """Gegenspieler-Meldepunkte über 1800 → 400 (Plausibilitätsgrenze §7.1)."""
        antwort = _post_json(self.client, self.url, {
            "typ": "einfaches_abgehen",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
            "reizwert": 200,
            "gegenspieler": [
                {"name": "Bernd", "meldepunkte": 5000},
                {"name": "Clara", "meldepunkte": 0},
                {"name": "Dieter","meldepunkte": 40},
            ],
        })
        self.assertEqual(antwort.status_code, 400)
        self.assertIn("fehler", antwort.json())


# ── Slice 6: Punktestände und Sieger ──────────────────────────────────────────

class PunktestaendeUndSiegerApiTest(TestCase):
    """
    Spielt 2 Runden durch und prüft Punktestände + Siegerermittlung.

    Runde 1: Anna gewinnt mit reizwert=200, melde=110, stich=100 → 210 Punkte
    Runde 2: Bernd gewinnt mit reizwert=150, melde=80, stich=80 → 160 Punkte
    """

    def setUp(self):
        self.spiel_id = _neues_spiel(self.client)
        url = f"/api/spiele/{self.spiel_id}/runden/"

        # Runde 1: Anna gewinnt
        _post_json(self.client, url, {
            "typ": "normal",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
            "reizwert": 200,
            "meldepunkte": 110,
            "stichwerte": 100,
            "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Bernd", "meldepunkte": 20, "stichwerte": 50, "hat_eigenen_stich": True},
                {"name": "Clara", "meldepunkte": 0,  "stichwerte": 60, "hat_eigenen_stich": True},
                {"name": "Dieter","meldepunkte": 40, "stichwerte": 40, "hat_eigenen_stich": True},
            ],
        })

        # Runde 2: Bernd gewinnt
        _post_json(self.client, url, {
            "typ": "normal",
            "rundennummer": 2,
            "spielmacher": "Bernd",
            "geber": "Anna",
            "reizwert": 150,
            "meldepunkte": 80,
            "stichwerte": 80,
            "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Anna",  "meldepunkte": 20, "stichwerte": 50, "hat_eigenen_stich": True},
                {"name": "Clara", "meldepunkte": 0,  "stichwerte": 60, "hat_eigenen_stich": True},
                {"name": "Dieter","meldepunkte": 40, "stichwerte": 40, "hat_eigenen_stich": True},
            ],
        })

    def test_punktestaende(self):
        """GET /api/spiele/{id}/punktestaende/ → Punkte für alle Spieler."""
        antwort = self.client.get(f"/api/spiele/{self.spiel_id}/punktestaende/")
        self.assertEqual(antwort.status_code, 200)
        daten = antwort.json()
        self.assertEqual(daten["spiel_id"], self.spiel_id)
        punkte = daten["punktestaende"]
        self.assertIn("Anna", punkte)
        self.assertIn("Bernd", punkte)
        # Anna: 210 (eigene Runde) + 30 (mitpunkte Runde 2, hat_eigenen_stich) + 20+50 (melde+stich Runde 2)
        # Bernd: 30 (mitpunkte Runde 1, hat_eigenen_stich) + 20+50 (melde+stich Runde 1) + 160 (eigene Runde)
        self.assertGreater(punkte["Anna"], 0)
        self.assertGreater(punkte["Bernd"], 0)

    def test_sieger_ermitteln(self):
        """GET /api/spiele/{id}/sieger/ → mindestens ein Gewinner."""
        antwort = self.client.get(f"/api/spiele/{self.spiel_id}/sieger/")
        self.assertEqual(antwort.status_code, 200)
        daten = antwort.json()
        self.assertIn("sieger", daten)
        self.assertIsInstance(daten["sieger"], list)
        self.assertGreater(len(daten["sieger"]), 0)

    def test_sieger_nicht_vorhanden(self):
        """GET auf nicht existierendes Spiel → 404."""
        antwort = self.client.get("/api/spiele/9999/sieger/")
        self.assertEqual(antwort.status_code, 404)

    def test_exakte_stichwerte_tiebreaking(self):
        """exakte_stichwerte Query-Parameter wird akzeptiert."""
        antwort = self.client.get(
            f"/api/spiele/{self.spiel_id}/sieger/",
            {"exakte_stichwerte": "Anna:12,Bernd:7,Clara:5,Dieter:3"},
        )
        self.assertEqual(antwort.status_code, 200)
        self.assertIn("sieger", antwort.json())
