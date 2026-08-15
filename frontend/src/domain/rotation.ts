/**
 * Reine Domänenlogik für Geberrotation und Rollen pro Runde (V1, 4 Spieler).
 *
 * Normative Quelle: docs/rule-set-v1.md §3 (Spielerreihenfolge, Geberrotation)
 * und §2 (pro Runde ein aussetzender Geber, 3 aktive Spieler).
 *
 * Die API kennt keine laufende Rundennummer/Rotation – das Frontend leitet sie
 * deterministisch aus der festen Spielerreihenfolge ab.
 */

/**
 * Geber der angegebenen Runde (1-basiert). Die Erfassung beginnt beim ersten
 * Geber (§3.1), daher ist `spieler[0]` Geber in Runde 1; danach streng reihum.
 */
export function geberFuerRunde(spieler: string[], rundennummer: number): string {
  return spieler[(rundennummer - 1) % spieler.length]
}

/** Die drei aktiven Spieler einer Runde: alle außer dem aussetzenden Geber. */
export function aktiveSpieler(spieler: string[], geber: string): string[] {
  return spieler.filter((name) => name !== geber)
}

/** Gegenspieler = aktive Spieler ohne den Spielmacher (im Normalfall zwei). */
export function gegenspielerNamen(aktive: string[], spielmacher: string): string[] {
  return aktive.filter((name) => name !== spielmacher)
}
