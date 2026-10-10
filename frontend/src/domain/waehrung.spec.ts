import { describe, expect, it } from 'vitest'
import { euroFormatieren } from './waehrung'

/** Intl trennt Betrag und Währungszeichen durch ein geschütztes Leerzeichen. */
const normal = (text: string) => text.replace(/ /g, ' ')

describe('euroFormatieren', () => {
  it('stellt ganze Cent im deutschen Format mit Euro-Zeichen dar', () => {
    expect(normal(euroFormatieren(800))).toBe('8,00 €')
    expect(normal(euroFormatieren(1250))).toBe('12,50 €')
    expect(normal(euroFormatieren(950))).toBe('9,50 €')
  })

  it('zeigt immer genau zwei Nachkommastellen', () => {
    expect(normal(euroFormatieren(0))).toBe('0,00 €')
    expect(normal(euroFormatieren(5))).toBe('0,05 €')
    expect(normal(euroFormatieren(100))).toBe('1,00 €')
  })

  it('trennt Tausender mit einem Punkt', () => {
    expect(normal(euroFormatieren(123456))).toBe('1.234,56 €')
  })

  it('rechnet ganzzahlig, ohne Gleitkomma-Artefakte', () => {
    expect(normal(euroFormatieren(1010))).toBe('10,10 €')
    expect(normal(euroFormatieren(29))).toBe('0,29 €')
  })
})
