/**
 * Darstellung von Geldbeträgen (Abrechnung, rule-set-v1.md §20).
 *
 * Das Backend liefert Beträge in **ganzen Cent**; erst die Darstellung macht daraus Euro.
 * Dadurch gibt es im gesamten System keine Gleitkomma-Rundung bei der Berechnung.
 */

const EURO = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' })

/** Formatiert ganze Cent als Euro im deutschen Format mit zwei Nachkommastellen, z. B. `8,00 €`. */
export function euroFormatieren(cent: number): string {
  return EURO.format(cent / 100)
}
