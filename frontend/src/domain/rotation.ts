/**
 * Reine Domänenlogik für Geberrotation und Rollen pro Runde (V1, 3 oder 4 Spieler).
 *
 * Normative Quelle: docs/rule-set-v1.md §3 (Spielerreihenfolge, Geberrotation, §3.4 aktive
 * Spieler) und ADR-017 (Drei-Spieler-Variante).
 *
 * Die Variante ergibt sich allein aus der Spielerzahl: Bei 4 Spielern setzt der Geber aus,
 * bei 3 Spielern spielt er mit. In beiden Varianten sind pro Runde genau drei Spieler aktiv.
 *
 * Die API kennt keine laufende Rundennummer/Rotation – das Frontend leitet sie
 * deterministisch aus der festen Spielerreihenfolge ab.
 */

/** Spielerzahl, bei der der Geber aussetzt (rule-set-v1.md §3.4). */
const SPIELERZAHL_MIT_AUSSETZENDEM_GEBER = 4

/**
 * Geber der angegebenen Runde (1-basiert). Die Erfassung beginnt beim ersten
 * Geber (§3.1), daher ist `spieler[0]` Geber in Runde 1; danach streng reihum
 * über die tatsächliche Spielerzahl.
 */
export function geberFuerRunde(spieler: string[], rundennummer: number): string {
  return spieler[(rundennummer - 1) % spieler.length]
}

/** Setzt der Geber aus (4 Spieler) oder spielt er mit (3 Spieler)? */
export function geberSetztAus(spieler: string[]): boolean {
  return spieler.length === SPIELERZAHL_MIT_AUSSETZENDEM_GEBER
}

/**
 * Die drei aktiven Spieler einer Runde: bei 4 Spielern alle außer dem aussetzenden Geber,
 * bei 3 Spielern alle.
 */
export function aktiveSpieler(spieler: string[], geber: string): string[] {
  if (!geberSetztAus(spieler)) return [...spieler]
  return spieler.filter((name) => name !== geber)
}

/** Gegenspieler = aktive Spieler ohne den Spielmacher (in beiden Varianten genau zwei). */
export function gegenspielerNamen(aktive: string[], spielmacher: string): string[] {
  return aktive.filter((name) => name !== spielmacher)
}
