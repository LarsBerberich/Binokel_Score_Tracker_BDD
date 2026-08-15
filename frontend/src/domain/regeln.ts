/**
 * Numerische Regelkonstanten der Binokel-Domäne (V1).
 *
 * Normative Quelle: docs/rule-set-v1.md.
 */

/**
 * Summe der Stichwerte aller drei aktiven Spieler einer regulär gespielten Runde
 * (inkl. gedrückter Karten des Spielmachers). Normativ: rule-set-v1.md §5.2.
 */
export const STICHWERT_KONTROLLSUMME = 250

/**
 * Kleinster zulässiger Reizwert (Hausregel, entspricht gängiger Turnierpraxis).
 * Reizwerte sind immer volle 10er-Werte. Normativ: rule-set-v1.md §7.
 */
export const REIZWERT_MINIMUM = 150

/**
 * Höchstmögliche Meldung eines einzelnen Spielers: doppelte Familie einer Farbe
 * (1500) + doppelter Binokel (300) = 1800. Dient als Plausibilitätsgrenze gegen
 * Eingabefehler. Normativ: rule-set-v1.md §7.1.
 */
export const MELDEPUNKTE_MAXIMUM = 1800

/** Schrittweite für 10er-genaue Eingabefelder (Reizwert, Meldepunkte, Stichwerte). */
export const ZEHNER_SCHRITT = 10
