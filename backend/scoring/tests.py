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


# ── Slice 6: Tausender-Sterne aggregieren ─────────────────────────────────────

class SterneApiTest(TestCase):
    """
    Prüft die Aggregation der Tausender-Sterne (TASK-013).

    Absicherung insb. „Tausender verloren": dabei werden KEINE
    GegenspielerRundeModel-Zeilen angelegt → die aktiven Gegenspieler
    (alle − Geber − Spielmacher) müssen dennoch je einen Stern erhalten,
    der Geber (setzt aus) keinen (normativ: rule-set-v1.md §15.3).
    """

    def setUp(self):
        self.spiel_id = _neues_spiel(self.client)
        url = f"/api/spiele/{self.spiel_id}/runden/"

        # Runde 1: Anna gewinnt einen Tausender → Stern für Anna (Spielmacher).
        _post_json(self.client, url, {
            "typ": "tausender_gewonnen",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
        })

        # Runde 2: Bernd verliert einen Tausender → Sterne für die aktiven
        # Gegenspieler (alle − Geber Anna − Spielmacher Bernd) = Clara, Dieter.
        _post_json(self.client, url, {
            "typ": "tausender_verloren",
            "rundennummer": 2,
            "spielmacher": "Bernd",
            "geber": "Anna",
        })

    def test_punktestaende_enthaelt_sterne(self):
        """GET punktestaende/ liefert additiv das sterne-Mapping."""
        antwort = self.client.get(f"/api/spiele/{self.spiel_id}/punktestaende/")
        self.assertEqual(antwort.status_code, 200)
        daten = antwort.json()
        self.assertIn("sterne", daten)
        self.assertEqual(
            daten["sterne"], {"Anna": 1, "Bernd": 0, "Clara": 1, "Dieter": 1}
        )

    def test_tausender_verloren_verteilt_sterne_ohne_geber(self):
        """Tausender verloren: aktive Gegenspieler bekommen Sterne, der Geber nicht."""
        antwort = self.client.get(f"/api/spiele/{self.spiel_id}/punktestaende/")
        sterne = antwort.json()["sterne"]
        # Runde 2: Geber Anna setzt aus → kein zusätzlicher Stern durch die Niederlage.
        self.assertEqual(sterne["Clara"], 1)
        self.assertEqual(sterne["Dieter"], 1)
        # Anna hat ihren Stern nur aus Runde 1 (Spielmacher-Sieg), nicht aus Runde 2.
        self.assertEqual(sterne["Anna"], 1)

    def test_sieger_enthaelt_sterne(self):
        """GET sieger/ liefert das sterne-Mapping ebenfalls (konsistenter Endstand)."""
        antwort = self.client.get(f"/api/spiele/{self.spiel_id}/sieger/")
        self.assertEqual(antwort.status_code, 200)
        daten = antwort.json()
        self.assertIn("sterne", daten)
        self.assertEqual(
            daten["sterne"], {"Anna": 1, "Bernd": 0, "Clara": 1, "Dieter": 1}
        )

    def test_sterne_null_ohne_tausender(self):
        """Ohne Tausender-Runde sind alle Sternwerte 0."""
        leeres_spiel = _neues_spiel(self.client)
        antwort = self.client.get(f"/api/spiele/{leeres_spiel}/punktestaende/")
        self.assertEqual(
            antwort.json()["sterne"],
            {"Anna": 0, "Bernd": 0, "Clara": 0, "Dieter": 0},
        )


# ── TASK-016: Zehner-Eingabe (§9.1/§9.4) ──────────────────────────────────────

class ZehnerEingabeApiTest(TestCase):
    """
    Sichert die Backend-Erzwingung der Zehner-Eingabe (STAND immer auf Zehner)
    und die 250-Kontrollsumme im HTTP-Pfad ab (normativ: rule-set-v1.md §9.1/§9.4).
    """

    def setUp(self):
        self.spiel_id = _neues_spiel(self.client)
        self.url = f"/api/spiele/{self.spiel_id}/runden/"

    def test_stand_ohne_einerstelle(self):
        """Runde mit Zehner-Stichwerten → alle Punktestände sind Vielfache von 10 (FND-002)."""
        antwort = _post_json(self.client, self.url, {
            "typ": "normal",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
            "reizwert": 200,
            "meldepunkte": 100,
            "stichwerte": 100,
            "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Bernd", "meldepunkte": 20, "stichwerte": 90, "hat_eigenen_stich": True},
                {"name": "Clara", "meldepunkte": 0,  "stichwerte": 60, "hat_eigenen_stich": True},
            ],
        })
        self.assertEqual(antwort.status_code, 201)

        punkte = self.client.get(
            f"/api/spiele/{self.spiel_id}/punktestaende/"
        ).json()["punktestaende"]
        for name, wert in punkte.items():
            self.assertEqual(wert % 10, 0, f"Stand von {name} ({wert}) hat eine Einerstelle")

    def test_stichwerte_kein_zehner_abgelehnt(self):
        """POST mit einem Stichwert, der kein Vielfaches von 10 ist → 400 (Modulo-Guard)."""
        antwort = _post_json(self.client, self.url, {
            "typ": "normal",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
            "reizwert": 200,
            "meldepunkte": 100,
            "stichwerte": 95,  # kein Zehner
            "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Bernd", "meldepunkte": 20, "stichwerte": 60, "hat_eigenen_stich": True},
                {"name": "Clara", "meldepunkte": 0,  "stichwerte": 40, "hat_eigenen_stich": True},
            ],
        })
        self.assertEqual(antwort.status_code, 400)
        self.assertIn("fehler", antwort.json())

    def test_reizwert_kein_zehner_abgelehnt(self):
        """POST mit einem Reizwert, der kein Vielfaches von 10 ist → 400."""
        antwort = _post_json(self.client, self.url, {
            "typ": "normal",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
            "reizwert": 155,  # kein Zehner
            "meldepunkte": 100,
            "stichwerte": 100,
            "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Bernd", "meldepunkte": 20, "stichwerte": 90, "hat_eigenen_stich": True},
                {"name": "Clara", "meldepunkte": 0,  "stichwerte": 60, "hat_eigenen_stich": True},
            ],
        })
        self.assertEqual(antwort.status_code, 400)
        self.assertIn("fehler", antwort.json())

    def test_stichwerte_summe_ueber_250_abgelehnt(self):
        """POST mit Zehner-Stichwerten, deren Summe 250 übersteigt → 400 (Kontrollsumme)."""
        antwort = _post_json(self.client, self.url, {
            "typ": "normal",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
            "reizwert": 200,
            "meldepunkte": 100,
            "stichwerte": 120,
            "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Bernd", "meldepunkte": 20, "stichwerte": 90, "hat_eigenen_stich": True},
                {"name": "Clara", "meldepunkte": 0,  "stichwerte": 60, "hat_eigenen_stich": True},
            ],
        })
        self.assertEqual(antwort.status_code, 400)
        self.assertIn("fehler", antwort.json())


# ── TASK-014 Slice 1: Spielmacher-M|S getrennt + Invariante (HOCH-1) ───────────

class SpielmacherMSInvarianteApiTest(TestCase):
    """
    Sichert die getrennte Aufschlüsselung der Spielmacher-Punkte in M (Meldung)
    und S (Stichwerte) sowie die Schreibpfad-Invariante ab (HOCH-1 / FND-004):

    - Gewonnenes Spiel: spielmacher_punkte == spielmacher_meldepunkte + spielmacher_stichwerte.
    - Doppeltes Abgehen: spielmacher_punkte == 0; M|S tragen die roh erfassten
      (fachlich verfallenen) Werte als Korrektur-Beleg (FND-004).
    - Einfaches Abgehen und Tausender: alle drei Werte 0.
    Normativ: docs/Anschreibetabelle_4_Spieler.md §5.
    """

    def setUp(self):
        self.spiel_id = _neues_spiel(self.client)
        self.url = f"/api/spiele/{self.spiel_id}/runden/"

    def _runde(self, rundennummer: int):
        from scoring.models import RundeModel
        return RundeModel.objects.get(spiel_id=self.spiel_id, rundennummer=rundennummer)

    def _assert_invariante(self, runde):
        self.assertEqual(
            runde.spielmacher_punkte,
            runde.spielmacher_meldepunkte + runde.spielmacher_stichwerte,
            "Invariante verletzt: spielmacher_punkte != M + S",
        )

    def test_normal_gewonnen_ms_getrennt(self):
        """Gewonnenes Spiel: M und S getrennt gespeichert, Summe == spielmacher_punkte."""
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
                {"name": "Bernd", "meldepunkte": 20, "stichwerte": 90, "hat_eigenen_stich": True},
                {"name": "Clara", "meldepunkte": 0,  "stichwerte": 60, "hat_eigenen_stich": True},
            ],
        })
        self.assertEqual(antwort.status_code, 201)
        runde = self._runde(1)
        self.assertEqual(runde.spielmacher_meldepunkte, 110)
        self.assertEqual(runde.spielmacher_stichwerte, 100)
        self.assertEqual(runde.spielmacher_punkte, 210)
        self._assert_invariante(runde)

    def test_normal_ohne_stich_meldung_verfaellt(self):
        """Spielmacher ohne eigenen Stich: M verfällt (Stich-Zwang), Invariante bleibt."""
        antwort = _post_json(self.client, self.url, {
            "typ": "normal",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
            "reizwert": 150,
            "meldepunkte": 100,
            "stichwerte": 250,
            "hat_eigenen_stich": False,
            "gegenspieler": [
                {"name": "Bernd", "meldepunkte": 20, "stichwerte": 0, "hat_eigenen_stich": False},
                {"name": "Clara", "meldepunkte": 0,  "stichwerte": 0, "hat_eigenen_stich": False},
            ],
        })
        self.assertEqual(antwort.status_code, 201)
        runde = self._runde(1)
        # Meldung verfällt ohne Stich → M = 0, S = 250 → Punkte 250.
        self.assertEqual(runde.spielmacher_meldepunkte, 0)
        self.assertEqual(runde.spielmacher_stichwerte, 250)
        self._assert_invariante(runde)

    def test_doppeltes_abgehen_ms_roh_persistiert(self):
        """Doppeltes Abgehen (normal, M+S < Reizwert): Punkte 0, aber M|S tragen die
        roh erfassten (fachlich verfallenen) Werte als Korrektur-Beleg (FND-004)."""
        antwort = _post_json(self.client, self.url, {
            "typ": "normal",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
            "reizwert": 300,
            "meldepunkte": 100,
            "stichwerte": 100,
            "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Bernd", "meldepunkte": 20, "stichwerte": 90, "hat_eigenen_stich": True},
                {"name": "Clara", "meldepunkte": 0,  "stichwerte": 60, "hat_eigenen_stich": True},
            ],
        })
        self.assertEqual(antwort.status_code, 201)
        runde = self._runde(1)
        # Roh erfasste Werte bleiben erhalten (M stich-zwang-gewertet, S roh) – für die Korrektur.
        self.assertEqual(runde.spielmacher_meldepunkte, 100)
        self.assertEqual(runde.spielmacher_stichwerte, 100)
        # Gewertet wird allein der Verlust; die Spielmacher-Punkte sind 0.
        self.assertEqual(runde.spielmacher_punkte, 0)
        self.assertEqual(runde.verlustwert, -600)

    def test_einfaches_abgehen_ms_null(self):
        """Einfaches Abgehen: M|S = 0|0."""
        _post_json(self.client, self.url, {
            "typ": "einfaches_abgehen",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
            "reizwert": 200,
            "gegenspieler": [
                {"name": "Bernd", "meldepunkte": 20},
                {"name": "Clara", "meldepunkte": 0},
            ],
        })
        runde = self._runde(1)
        self.assertEqual(runde.spielmacher_meldepunkte, 0)
        self.assertEqual(runde.spielmacher_stichwerte, 0)
        self._assert_invariante(runde)

    def test_tausender_ms_null(self):
        """Tausender gewonnen: M|S = 0|0, Punkte 0."""
        _post_json(self.client, self.url, {
            "typ": "tausender_gewonnen",
            "rundennummer": 1,
            "spielmacher": "Anna",
            "geber": "Dieter",
        })
        runde = self._runde(1)
        self.assertEqual(runde.spielmacher_meldepunkte, 0)
        self.assertEqual(runde.spielmacher_stichwerte, 0)
        self.assertEqual(runde.spielmacher_punkte, 0)
        self._assert_invariante(runde)


# ── TASK-014 Slice 3: Rundenhistorie / Anschreibetabelle ──────────────────────

class RundenhistorieApiTest(TestCase):
    """
    GET /api/spiele/{id}/runden/ liefert die zweizeilige Anschreibetabelle:
    je Runde die M|S|Mit-Aufschlüsselung pro Spieler plus den kumulierten STAND
    (normativ: docs/Anschreibetabelle_4_Spieler.md §5). Der letzte STAND je Spieler
    muss `punktestaende_laden` entsprechen (HOCH-4).
    """

    def setUp(self):
        self.spiel_id = _neues_spiel(self.client)
        self.url = f"/api/spiele/{self.spiel_id}/runden/"

    def test_leere_historie_ohne_runden(self):
        """0 Runden → 200 mit leerer Rundenliste und 0-STAND (kein 404)."""
        antwort = self.client.get(self.url)
        self.assertEqual(antwort.status_code, 200)
        daten = antwort.json()
        self.assertEqual(daten["runden"], [])
        self.assertEqual(daten["spieler"], ["Anna", "Bernd", "Clara", "Dieter"])

    def test_historie_nicht_vorhandenes_spiel(self):
        """GET auf nicht existierendes Spiel → 404."""
        antwort = self.client.get("/api/spiele/9999/runden/")
        self.assertEqual(antwort.status_code, 404)

    def test_historie_struktur_und_stand(self):
        """Nach einer gewonnenen Runde: M|S getrennt, Mit, STAND korrekt."""
        _post_json(self.client, self.url, {
            "typ": "normal",
            "rundennummer": 1,
            "spielmacher": "Bernd",
            "geber": "Anna",
            "reizwert": 180,
            "meldepunkte": 100,
            "stichwerte": 120,
            "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Clara", "meldepunkte": 40, "stichwerte": 130, "hat_eigenen_stich": True},
                {"name": "Dieter", "meldepunkte": 40, "stichwerte": 0, "hat_eigenen_stich": False},
            ],
        })
        daten = self.client.get(self.url).json()
        self.assertEqual(len(daten["runden"]), 1)
        runde = daten["runden"][0]
        self.assertEqual(runde["geber"], "Anna")
        self.assertEqual(runde["spielmacher"], "Bernd")

        anna = runde["spieler"]["Anna"]
        self.assertEqual(anna["rolle"], "geber")

        bernd = runde["spieler"]["Bernd"]
        self.assertEqual(bernd["rolle"], "spielmacher")
        self.assertEqual(bernd["meldepunkte"], 100)
        self.assertEqual(bernd["stichwerte"], 120)

        # Dieter: kein eigener Stich → M gestrichen (0), annotierbar (SOLLTE-6).
        dieter = runde["spieler"]["Dieter"]
        self.assertEqual(dieter["meldepunkte"], 0)
        self.assertFalse(dieter["hat_eigenen_stich"])

        # STAND-Zeile stimmt mit punktestaende überein (HOCH-4).
        punkte = self.client.get(
            f"/api/spiele/{self.spiel_id}/punktestaende/"
        ).json()["punktestaende"]
        self.assertEqual(runde["stand"], punkte)

    def test_letzte_stand_zeile_gleich_punktestaende(self):
        """Über mehrere Runden: letzte STAND-Zeile == punktestaende (HOCH-4)."""
        _post_json(self.client, self.url, {
            "typ": "normal", "rundennummer": 1, "spielmacher": "Anna", "geber": "Dieter",
            "reizwert": 200, "meldepunkte": 110, "stichwerte": 100, "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Bernd", "meldepunkte": 20, "stichwerte": 90, "hat_eigenen_stich": True},
                {"name": "Clara", "meldepunkte": 0, "stichwerte": 60, "hat_eigenen_stich": True},
            ],
        })
        _post_json(self.client, self.url, {
            "typ": "einfaches_abgehen", "rundennummer": 2, "spielmacher": "Bernd", "geber": "Anna",
            "reizwert": 250,
            "gegenspieler": [
                {"name": "Clara", "meldepunkte": 40},
                {"name": "Dieter", "meldepunkte": 20},
            ],
        })
        daten = self.client.get(self.url).json()
        letzter_stand = daten["runden"][-1]["stand"]
        punkte = self.client.get(
            f"/api/spiele/{self.spiel_id}/punktestaende/"
        ).json()["punktestaende"]
        self.assertEqual(letzter_stand, punkte)

    def test_tausender_stern_und_stand_friert_ein(self):
        """Tausender: Stern gesetzt, STAND unverändert gegenüber Vorrunde."""
        _post_json(self.client, self.url, {
            "typ": "normal", "rundennummer": 1, "spielmacher": "Anna", "geber": "Dieter",
            "reizwert": 200, "meldepunkte": 110, "stichwerte": 100, "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Bernd", "meldepunkte": 20, "stichwerte": 90, "hat_eigenen_stich": True},
                {"name": "Clara", "meldepunkte": 0, "stichwerte": 60, "hat_eigenen_stich": True},
            ],
        })
        _post_json(self.client, self.url, {
            "typ": "tausender_verloren", "rundennummer": 2, "spielmacher": "Bernd", "geber": "Anna",
        })
        daten = self.client.get(self.url).json()
        r1_stand = daten["runden"][0]["stand"]
        r2 = daten["runden"][1]
        self.assertTrue(r2["ist_tausender"])
        self.assertEqual(r2["stand"], r1_stand)  # STAND friert ein
        # Tausender verloren: aktive Gegenspieler (alle − Geber Anna − SM Bernd) = Clara, Dieter.
        self.assertTrue(r2["spieler"]["Clara"]["stern"])
        self.assertTrue(r2["spieler"]["Dieter"]["stern"])
        self.assertFalse(r2["spieler"]["Anna"]["stern"])  # Geber setzt aus


# ── TASK-014 Slice 4: Korrektur der letzten Runde (PUT) ───────────────────────

class RundeKorrekturApiTest(TestCase):
    """
    PUT /api/spiele/{id}/runden/{nr}/ — Korrektur der letzten Runde (TASK-014, ADR-015).

    Nur die höchste Rundennummer ist editierbar. Der Geber wird deterministisch aus
    der Rundennummer abgeleitet (HOCH-5), der Dispatch ist mit POST geteilt (HOCH-2),
    Typ-Übergänge schalten Gegenspieler-Zeilen und Sterne um (HOCH-3), und die
    Spielmacher-M|S-Invariante bleibt erhalten (HOCH-1).

    Geberrotation (Spieler Anna,Bernd,Clara,Dieter): Runde 1→Anna, 2→Bernd, 3→Clara.
    """

    def setUp(self):
        self.spiel_id = _neues_spiel(self.client)
        self.url = f"/api/spiele/{self.spiel_id}/runden/"

    def _put_json(self, rundennummer: int, payload: dict):
        return self.client.put(
            f"/api/spiele/{self.spiel_id}/runden/{rundennummer}/",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def _runde(self, rundennummer: int):
        from scoring.models import RundeModel
        return RundeModel.objects.get(spiel_id=self.spiel_id, rundennummer=rundennummer)

    def _normale_runde_1(self):
        """POST Runde 1: gewonnenes Spiel, Geber Anna (= deterministisch), SM Bernd."""
        return _post_json(self.client, self.url, {
            "typ": "normal", "rundennummer": 1, "spielmacher": "Bernd", "geber": "Anna",
            "reizwert": 200, "meldepunkte": 110, "stichwerte": 100, "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Clara", "meldepunkte": 20, "stichwerte": 90, "hat_eigenen_stich": True},
                {"name": "Dieter", "meldepunkte": 0, "stichwerte": 60, "hat_eigenen_stich": True},
            ],
        })

    def test_put_letzte_runde_aktualisiert_stand(self):
        """Korrektur der letzten Runde → 200, letzte STAND-Zeile == punktestaende (HOCH-4)."""
        self._normale_runde_1()
        antwort = self._put_json(1, {
            "typ": "normal", "spielmacher": "Bernd",
            "reizwert": 200, "meldepunkte": 150, "stichwerte": 100, "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Clara", "meldepunkte": 20, "stichwerte": 80, "hat_eigenen_stich": True},
                {"name": "Dieter", "meldepunkte": 0, "stichwerte": 70, "hat_eigenen_stich": True},
            ],
        })
        self.assertEqual(antwort.status_code, 200)
        runde = self._runde(1)
        self.assertEqual(runde.spielmacher_punkte, 250)  # 150 + 100

        historie = self.client.get(self.url).json()
        letzter_stand = historie["runden"][-1]["stand"]
        punkte = self.client.get(
            f"/api/spiele/{self.spiel_id}/punktestaende/"
        ).json()["punktestaende"]
        self.assertEqual(letzter_stand, punkte)

    def test_put_invariante_ms(self):
        """PUT normal gewonnen: Invariante spielmacher_punkte == M + S bleibt erhalten."""
        self._normale_runde_1()
        self._put_json(1, {
            "typ": "normal", "spielmacher": "Bernd",
            "reizwert": 200, "meldepunkte": 120, "stichwerte": 90, "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Clara", "meldepunkte": 20, "stichwerte": 100, "hat_eigenen_stich": True},
                {"name": "Dieter", "meldepunkte": 0, "stichwerte": 60, "hat_eigenen_stich": True},
            ],
        })
        runde = self._runde(1)
        self.assertEqual(runde.spielmacher_meldepunkte, 120)
        self.assertEqual(runde.spielmacher_stichwerte, 90)
        self.assertEqual(
            runde.spielmacher_punkte,
            runde.spielmacher_meldepunkte + runde.spielmacher_stichwerte,
        )

    def test_doppeltes_abgehen_roh_ermoeglicht_korrektur(self):
        """FND-004: doppeltes Abgehen speichert die SM-Rohwerte, sodass GET sie liefert
        und die PUT-Korrektur derselben Runde die 250-Kontrollsumme erfüllt (200, kein 400)."""
        _post_json(self.client, self.url, {
            "typ": "normal", "rundennummer": 1, "spielmacher": "Bernd", "geber": "Anna",
            "reizwert": 300, "meldepunkte": 100, "stichwerte": 100, "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Clara", "meldepunkte": 20, "stichwerte": 90, "hat_eigenen_stich": True},
                {"name": "Dieter", "meldepunkte": 0, "stichwerte": 60, "hat_eigenen_stich": True},
            ],
        })
        # GET liefert die roh erfassten Spielmacher-Stichwerte (Basis der Korrektur-Vorbelegung).
        historie = self.client.get(self.url).json()
        sm_zelle = historie["runden"][-1]["spieler"]["Bernd"]
        self.assertEqual(sm_zelle["stichwerte"], 100)
        # PUT mit denselben Werten läuft durch (Kontrollsumme 100+90+60 == 250).
        antwort = self._put_json(1, {
            "typ": "normal", "spielmacher": "Bernd",
            "reizwert": 300, "meldepunkte": 100, "stichwerte": 100, "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Clara", "meldepunkte": 20, "stichwerte": 90, "hat_eigenen_stich": True},
                {"name": "Dieter", "meldepunkte": 0, "stichwerte": 60, "hat_eigenen_stich": True},
            ],
        })
        self.assertEqual(antwort.status_code, 200)

    def test_put_typ_uebergang_normal_zu_tausender(self):
        """normal→tausender: GS-Zeilen gelöscht, Sterne gesetzt, SM M|S = 0|0 (HOCH-3)."""
        self._normale_runde_1()
        antwort = self._put_json(1, {"typ": "tausender_gewonnen", "spielmacher": "Bernd"})
        self.assertEqual(antwort.status_code, 200)
        runde = self._runde(1)
        self.assertEqual(runde.gegenspieler.count(), 0)
        self.assertTrue(runde.spielmacher_stern)
        self.assertFalse(runde.gegenspieler_stern)
        self.assertEqual(runde.spielmacher_meldepunkte, 0)
        self.assertEqual(runde.spielmacher_stichwerte, 0)
        self.assertEqual(runde.spielmacher_punkte, 0)

    def test_put_typ_uebergang_tausender_zu_normal(self):
        """tausender→normal: GS-Zeilen angelegt, Sterne gelöscht, SM M|S gesetzt (HOCH-3)."""
        _post_json(self.client, self.url, {
            "typ": "tausender_verloren", "rundennummer": 1, "spielmacher": "Bernd", "geber": "Anna",
        })
        antwort = self._put_json(1, {
            "typ": "normal", "spielmacher": "Bernd",
            "reizwert": 200, "meldepunkte": 110, "stichwerte": 100, "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Clara", "meldepunkte": 20, "stichwerte": 90, "hat_eigenen_stich": True},
                {"name": "Dieter", "meldepunkte": 0, "stichwerte": 60, "hat_eigenen_stich": True},
            ],
        })
        self.assertEqual(antwort.status_code, 200)
        runde = self._runde(1)
        self.assertEqual(runde.gegenspieler.count(), 2)
        self.assertFalse(runde.spielmacher_stern)
        self.assertFalse(runde.gegenspieler_stern)
        self.assertEqual(runde.spielmacher_meldepunkte, 110)
        self.assertEqual(runde.spielmacher_stichwerte, 100)

    def test_put_geber_deterministisch_ignoriert_client(self):
        """Geber wird aus rundennummer abgeleitet, ein Body-Geber wird ignoriert (HOCH-5)."""
        self._normale_runde_1()
        self._put_json(1, {
            "typ": "normal", "spielmacher": "Bernd", "geber": "Clara",  # falsch → wird ignoriert
            "reizwert": 200, "meldepunkte": 110, "stichwerte": 100, "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Clara", "meldepunkte": 20, "stichwerte": 90, "hat_eigenen_stich": True},
                {"name": "Dieter", "meldepunkte": 0, "stichwerte": 60, "hat_eigenen_stich": True},
            ],
        })
        runde = self._runde(1)
        self.assertEqual(runde.geber.name, "Anna")  # deterministisch für Runde 1

    def test_put_spielmacher_gleich_geber_abgelehnt(self):
        """Spielmacher == abgeleiteter Geber → 400."""
        self._normale_runde_1()
        antwort = self._put_json(1, {"typ": "tausender_gewonnen", "spielmacher": "Anna"})
        self.assertEqual(antwort.status_code, 400)

    def test_put_spielmacher_nicht_im_spiel_abgelehnt(self):
        """Spielmacher ist kein Spieler des Spiels → 400."""
        self._normale_runde_1()
        antwort = self._put_json(1, {"typ": "tausender_gewonnen", "spielmacher": "Xaver"})
        self.assertEqual(antwort.status_code, 400)

    def test_put_validierung_reuse_stichwert_kein_zehner(self):
        """Geteilte Validierung (modulo-10 Stichwert) greift auch im PUT → 400."""
        self._normale_runde_1()
        antwort = self._put_json(1, {
            "typ": "normal", "spielmacher": "Bernd",
            "reizwert": 200, "meldepunkte": 100, "stichwerte": 95, "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Clara", "meldepunkte": 20, "stichwerte": 60, "hat_eigenen_stich": True},
                {"name": "Dieter", "meldepunkte": 0, "stichwerte": 40, "hat_eigenen_stich": True},
            ],
        })
        self.assertEqual(antwort.status_code, 400)

    def test_put_validierung_reuse_reizwert_kein_zehner(self):
        """Geteilte Validierung (modulo-10 Reizwert) greift auch im PUT → 400."""
        self._normale_runde_1()
        antwort = self._put_json(1, {
            "typ": "normal", "spielmacher": "Bernd",
            "reizwert": 155, "meldepunkte": 100, "stichwerte": 100, "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Clara", "meldepunkte": 20, "stichwerte": 90, "hat_eigenen_stich": True},
                {"name": "Dieter", "meldepunkte": 0, "stichwerte": 60, "hat_eigenen_stich": True},
            ],
        })
        self.assertEqual(antwort.status_code, 400)

    def test_put_validierung_reuse_kontrollsumme(self):
        """Geteilte Validierung (250-Kontrollsumme) greift auch im PUT → 400."""
        self._normale_runde_1()
        antwort = self._put_json(1, {
            "typ": "normal", "spielmacher": "Bernd",
            "reizwert": 200, "meldepunkte": 100, "stichwerte": 120, "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": "Clara", "meldepunkte": 20, "stichwerte": 90, "hat_eigenen_stich": True},
                {"name": "Dieter", "meldepunkte": 0, "stichwerte": 60, "hat_eigenen_stich": True},
            ],
        })
        self.assertEqual(antwort.status_code, 400)

    def test_put_nicht_letzte_runde_409(self):
        """Korrektur einer bestehenden, aber nicht letzten Runde → 409 Conflict."""
        self._normale_runde_1()
        _post_json(self.client, self.url, {
            "typ": "einfaches_abgehen", "rundennummer": 2, "spielmacher": "Clara", "geber": "Bernd",
            "reizwert": 250,
            "gegenspieler": [
                {"name": "Anna", "meldepunkte": 40},
                {"name": "Dieter", "meldepunkte": 20},
            ],
        })
        antwort = self._put_json(1, {"typ": "tausender_gewonnen", "spielmacher": "Bernd"})
        self.assertEqual(antwort.status_code, 409)

    def test_put_nicht_existente_runde_404(self):
        """Korrektur einer nicht existierenden Runde (> letzte) → 404 Not Found."""
        self._normale_runde_1()
        antwort = self._put_json(5, {"typ": "tausender_gewonnen", "spielmacher": "Bernd"})
        self.assertEqual(antwort.status_code, 404)

    def test_put_leeres_spiel_404(self):
        """Korrektur ohne jede gespeicherte Runde → 404."""
        antwort = self._put_json(1, {"typ": "tausender_gewonnen", "spielmacher": "Bernd"})
        self.assertEqual(antwort.status_code, 404)

    def test_put_get_auf_detail_405(self):
        """GET auf den Detail-Endpunkt → 405 (nur PUT erlaubt)."""
        self._normale_runde_1()
        antwort = self.client.get(f"/api/spiele/{self.spiel_id}/runden/1/")
        self.assertEqual(antwort.status_code, 405)


# ── FND-006: Tausender außer Konkurrenz ───────────────────────────────────────

class TausenderAusserKonkurrenzApiTest(TestCase):
    """FND-006: Tausender laufen außer Konkurrenz (normativ: docs/rule-set-v1.md §15).

    Jede erfasste Runde – auch ein Tausender – erhält eine eindeutige fortlaufende
    Sequenz (``rundennummer``). Ein Tausender zählt aber NICHT als gespielte Runde:
    die gezählte Spielrunde (``zaehlrunde``) und der Geber bleiben stehen, bis eine
    reguläre Runde folgt. Spieler: Anna(0), Bernd(1), Clara(2), Dieter(3);
    Geber der gezählten Runde n = spieler[(n-1) % 4].
    """

    def setUp(self):
        self.spiel_id = _neues_spiel(self.client)
        self.url = f"/api/spiele/{self.spiel_id}/runden/"

    def _normal(self, spielmacher, geber, gs1, gs2):
        return _post_json(self.client, self.url, {
            "typ": "normal", "spielmacher": spielmacher, "geber": geber,
            "reizwert": 150, "meldepunkte": 150, "stichwerte": 100, "hat_eigenen_stich": True,
            "gegenspieler": [
                {"name": gs1, "meldepunkte": 0, "stichwerte": 90, "hat_eigenen_stich": True},
                {"name": gs2, "meldepunkte": 0, "stichwerte": 60, "hat_eigenen_stich": True},
            ],
        })

    def _tausender(self, spielmacher, geber, verloren=False):
        return _post_json(self.client, self.url, {
            "typ": "tausender_verloren" if verloren else "tausender_gewonnen",
            "spielmacher": spielmacher, "geber": geber,
        })

    def test_historie_zaehlrunde_und_sequenz(self):
        """Tausender erhält eigene Sequenz, aber keine gezählte Rundennummer (zaehlrunde=None)."""
        self._normal("Bernd", "Anna", "Clara", "Dieter")   # Seq 1, gezählte Runde 1
        self._tausender("Clara", "Bernd")                  # Seq 2, außer Konkurrenz
        self._normal("Dieter", "Bernd", "Anna", "Clara")   # Seq 3, gezählte Runde 2

        historie = self.client.get(self.url).json()["runden"]
        self.assertEqual([r["sequenz"] for r in historie], [1, 2, 3])
        self.assertEqual([r["rundennummer"] for r in historie], [1, 2, 3])
        self.assertEqual([r["zaehlrunde"] for r in historie], [1, None, 2])
        self.assertEqual([r["ist_tausender"] for r in historie], [False, True, False])

    def test_geber_bleibt_ueber_tausender_stehen(self):
        """geber_fuer_sequenz: Tausender-Sequenzen verschieben den Geber nicht (POST≡PUT)."""
        from scoring.repositories import geber_fuer_sequenz
        self._normal("Bernd", "Anna", "Clara", "Dieter")   # Seq 1 (zählt)
        self._tausender("Clara", "Bernd")                  # Seq 2 (Tausender)
        self._normal("Dieter", "Bernd", "Anna", "Clara")   # Seq 3 (zählt)

        self.assertEqual(geber_fuer_sequenz(self.spiel_id, 1), "Anna")   # 0 gezählt davor
        self.assertEqual(geber_fuer_sequenz(self.spiel_id, 2), "Bernd")  # 1 gezählt davor
        self.assertEqual(geber_fuer_sequenz(self.spiel_id, 3), "Bernd")  # Tausender zählt nicht
        self.assertEqual(geber_fuer_sequenz(self.spiel_id, 4), "Clara")  # 2 gezählt davor

    def test_mehrere_tausender_hintereinander_persistierbar(self):
        """Mehrere Tausender in Folge → eindeutige Sequenzen, alle 201; Zähler erst bei regulär."""
        self.assertEqual(self._tausender("Bernd", "Anna").status_code, 201)                 # Seq 1
        self.assertEqual(self._tausender("Clara", "Anna", verloren=True).status_code, 201)  # Seq 2
        self.assertEqual(
            self._normal("Bernd", "Anna", "Clara", "Dieter").status_code, 201               # Seq 3
        )
        historie = self.client.get(self.url).json()["runden"]
        self.assertEqual([r["sequenz"] for r in historie], [1, 2, 3])
        self.assertEqual([r["zaehlrunde"] for r in historie], [None, None, 1])

    def test_tausender_friert_stand_ein_und_vergibt_sterne(self):
        """Tausender: kein numerischer Beitrag (STAND friert), aber Sterne (§15)."""
        self._normal("Bernd", "Anna", "Clara", "Dieter")  # Bernd gewinnt 250
        stand_vor = self.client.get(f"/api/spiele/{self.spiel_id}/punktestaende/").json()
        self._tausender("Clara", "Bernd", verloren=True)  # aktive GS Anna+Dieter je Stern
        stand_nach = self.client.get(f"/api/spiele/{self.spiel_id}/punktestaende/").json()

        self.assertEqual(stand_vor["punktestaende"], stand_nach["punktestaende"])
        self.assertEqual(stand_nach["sterne"]["Anna"], 1)
        self.assertEqual(stand_nach["sterne"]["Dieter"], 1)
        self.assertEqual(stand_nach["sterne"]["Clara"], 0)  # Spielmacher
        self.assertEqual(stand_nach["sterne"]["Bernd"], 0)  # Geber (setzt aus)

    def test_put_letzter_tausender_korrigierbar(self):
        """Letzte Runde = Tausender ist korrigierbar (gewonnen→verloren) → 200."""
        from scoring.models import RundeModel
        self._normal("Bernd", "Anna", "Clara", "Dieter")  # Seq 1
        self._tausender("Clara", "Bernd")                 # Seq 2 (letzte)
        antwort = self.client.put(
            f"/api/spiele/{self.spiel_id}/runden/2/",
            data=json.dumps({"typ": "tausender_verloren", "spielmacher": "Clara"}),
            content_type="application/json",
        )
        self.assertEqual(antwort.status_code, 200)
        runde = RundeModel.objects.get(spiel_id=self.spiel_id, rundennummer=2)
        self.assertEqual(runde.rundenausgang, "Tausender verloren")

    def test_put_nicht_letzter_tausender_409(self):
        """Ein Tausender, der nicht die höchste Sequenz ist, ist nicht korrigierbar → 409."""
        self._normal("Bernd", "Anna", "Clara", "Dieter")  # Seq 1
        self._tausender("Clara", "Bernd")                 # Seq 2
        self._normal("Dieter", "Bernd", "Anna", "Clara")  # Seq 3 (letzte)
        antwort = self.client.put(
            f"/api/spiele/{self.spiel_id}/runden/2/",
            data=json.dumps({"typ": "tausender_verloren", "spielmacher": "Clara"}),
            content_type="application/json",
        )
        self.assertEqual(antwort.status_code, 409)

