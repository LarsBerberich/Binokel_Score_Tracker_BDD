/**
 * TypeScript-Typen für den Binokel Score Tracker – abgeleitet aus dem
 * API-Vertrag `frontend/openapi/binokel-api.v1.yaml` (Single Source of Truth).
 *
 * PFLICHT: Änderungen am OpenAPI-Vertrag hier nachziehen.
 */

// ── Gemeinsame Typen ──────────────────────────────────────────────────────────

export type Rundentyp =
  | 'normal'
  | 'einfaches_abgehen'
  | 'doppeltes_abgehen'
  | 'tausender_gewonnen'
  | 'tausender_verloren'

export interface Fehler {
  fehler: string
}

// ── Slice 1: Spiel ────────────────────────────────────────────────────────────

export interface SpielAnlegenRequest {
  /** Genau 4 Spielernamen in Reihenfolge. */
  spieler: string[]
  /** Muss ein Vielfaches von 4 sein. Optional; Default legt das Backend fest. */
  rundenanzahl?: number | null
}

export interface Spiel {
  id: number
  rundenanzahl: number
  spieler: string[]
}

// ── Slices 2–5: Runde ─────────────────────────────────────────────────────────

/** Gegenspieler mit vollem Stich-Zwang (typ normal / doppeltes_abgehen). */
export interface Gegenspieler {
  name: string
  meldepunkte: number
  stichwerte: number
  hat_eigenen_stich: boolean
}

/** Gegenspieler ohne Stich-Zwang (typ einfaches_abgehen). */
export interface GegenspielerEinfach {
  name: string
  meldepunkte: number
  hat_eigenen_stich?: boolean
}

interface RundeBasis {
  rundennummer: number
  spielmacher: string
  geber: string
  spielmacher_stern?: boolean
  gegenspieler_stern?: boolean
}

export interface RundeNormal extends RundeBasis {
  typ: 'normal'
  reizwert: number
  meldepunkte: number
  stichwerte: number
  hat_eigenen_stich: boolean
  gegenspieler: Gegenspieler[]
}

export interface RundeEinfachesAbgehen extends RundeBasis {
  typ: 'einfaches_abgehen'
  reizwert: number
  gegenspieler: GegenspielerEinfach[]
}

export interface RundeDoppeltesAbgehen extends RundeBasis {
  typ: 'doppeltes_abgehen'
  reizwert: number
  gegenspieler: Gegenspieler[]
}

export interface RundeTausender extends RundeBasis {
  typ: 'tausender_gewonnen' | 'tausender_verloren'
}

/** Diskriminierte Union über das Feld `typ`. */
export type RundeRequest =
  | RundeNormal
  | RundeEinfachesAbgehen
  | RundeDoppeltesAbgehen
  | RundeTausender

export interface RundeErgebnis {
  id: number
  rundennummer: number
  /** Interner Ausgangs-Code, z. B. gewonnenes_spiel, doppeltes_abgehen. */
  rundenausgang: string
  spielmacher_punkte: number
  /** Negativer Verlustwert bei Abgehen; sonst 0. */
  verlustwert: number
  mitpunkte_pro_gegenspieler: number
}

// ── TASK-014: Rundenhistorie / Anschreibetabelle ──────────────────────────────

/** Rolle eines Spielers in einer Runde (der Geber setzt aus). */
export type SpielerRolle = 'geber' | 'spielmacher' | 'gegenspieler'

/** Aufschlüsselung eines Spielers in einer Runde (M | S | Mit + Stern-Kennzeichen). */
export interface RundenhistorieZelle {
  rolle: SpielerRolle
  meldepunkte: number
  stichwerte: number
  mitpunkte: number
  hat_eigenen_stich: boolean
  stern: boolean
}

/** Eine Runde der Anschreibetabelle inkl. kumuliertem STAND je Spieler. */
export interface RundenhistorieRunde {
  rundennummer: number
  geber: string
  spielmacher: string
  reizwert: number
  /** Interner Ausgangs-Code (z. B. gewonnenes_spiel). */
  rundenausgang: string
  ist_tausender: boolean
  /** Negativer Verlustwert bei Abgehen; sonst 0. */
  verlustwert: number
  spieler: Record<string, RundenhistorieZelle>
  stand: Record<string, number>
}

/** Vollständige Anschreibetabelle eines Spiels (zweizeilig je Runde). */
export interface Rundenhistorie {
  spiel_id: number
  /** Feste Sitzreihenfolge (Spaltenreihenfolge der Tabelle). */
  spieler: string[]
  runden: RundenhistorieRunde[]
}

// ── Slice 6: Auswertung ───────────────────────────────────────────────────────

/** Mapping Spielername → Gesamtpunktestand. */
export type PunktestandMap = Record<string, number>

/** Mapping Spielername → Anzahl Tausender-Sterne. */
export type SterneMap = Record<string, number>

export interface Punktestaende {
  spiel_id: number
  punktestaende: PunktestandMap
  sterne: SterneMap
}

export interface SiegerErgebnis {
  spiel_id: number
  punktestaende: PunktestandMap
  sterne: SterneMap
  /** Sieger-Namen; leer, wenn kein eindeutiger Sieger feststeht. */
  sieger: string[]
}

// ── System ────────────────────────────────────────────────────────────────────

export interface Health {
  status: 'ok'
}
