import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import Anschreibetabelle from './Anschreibetabelle.vue'
import type {
  Rundenhistorie,
  RundenhistorieRunde,
  RundenhistorieZelle,
  SpielerRolle,
} from '../api'

/** Baut eine Rundenzelle mit sinnvollen Defaults (M | S | Mit). */
function zelle(rolle: SpielerRolle, teil: Partial<RundenhistorieZelle> = {}): RundenhistorieZelle {
  return {
    rolle,
    ist_geber: rolle === 'geber',
    meldepunkte: 0,
    stichwerte: 0,
    mitpunkte: 0,
    hat_eigenen_stich: false,
    stern: false,
    ...teil,
  }
}

/**
 * Beispiel nach docs/Anschreibetabelle_4_Spieler.md §5 (Spieler A–D):
 * R1 gewonnen (D Schneider), R2 einfaches Abgehen (C verliert), R3 Tausender (D ★).
 */
const runde1: RundenhistorieRunde = {
  rundennummer: 1,
  sequenz: 1,
  zaehlrunde: 1,
  geber: 'A',
  spielmacher: 'B',
  reizwert: 180,
  rundenausgang: 'gewonnenes Spiel',
  ist_tausender: false,
  verlustwert: 0,
  spieler: {
    A: zelle('geber'),
    B: zelle('spielmacher', { meldepunkte: 100, stichwerte: 120, hat_eigenen_stich: true }),
    C: zelle('gegenspieler', { meldepunkte: 40, stichwerte: 130, hat_eigenen_stich: true }),
    D: zelle('gegenspieler', { meldepunkte: 0, stichwerte: 0, hat_eigenen_stich: false }),
  },
  stand: { A: 0, B: 220, C: 170, D: 0 },
}

const runde2: RundenhistorieRunde = {
  rundennummer: 2,
  sequenz: 2,
  zaehlrunde: 2,
  geber: 'B',
  spielmacher: 'C',
  reizwert: 250,
  rundenausgang: 'einfaches Abgehen',
  ist_tausender: false,
  verlustwert: -250,
  spieler: {
    A: zelle('gegenspieler', { meldepunkte: 40, stichwerte: 0, mitpunkte: 30, hat_eigenen_stich: false }),
    B: zelle('geber'),
    C: zelle('spielmacher'),
    D: zelle('gegenspieler', { meldepunkte: 20, stichwerte: 0, mitpunkte: 30, hat_eigenen_stich: false }),
  },
  stand: { A: 70, B: 220, C: -80, D: 50 },
}

const runde3: RundenhistorieRunde = {
  rundennummer: 3,
  sequenz: 3,
  zaehlrunde: null,
  geber: 'C',
  spielmacher: 'D',
  reizwert: 0,
  rundenausgang: 'Tausender gewonnen',
  ist_tausender: true,
  verlustwert: 0,
  spieler: {
    A: zelle('gegenspieler', { meldepunkte: 0, stichwerte: 0, hat_eigenen_stich: false }),
    B: zelle('gegenspieler', { meldepunkte: 0, stichwerte: 0, hat_eigenen_stich: false }),
    C: zelle('geber'),
    D: zelle('spielmacher', { stern: true }),
  },
  stand: { A: 70, B: 220, C: -80, D: 50 },
}

const historie: Rundenhistorie = {
  spiel_id: 7,
  spieler: ['A', 'B', 'C', 'D'],
  runden: [runde1, runde2, runde3],
}

function mounten(h: Rundenhistorie) {
  return mount(Anschreibetabelle, { props: { historie: h } })
}

describe('Anschreibetabelle', () => {
  it('zeigt einen Hinweis, solange keine Runde erfasst ist', () => {
    const wrapper = mounten({ spiel_id: 7, spieler: ['A', 'B', 'C', 'D'], runden: [] })
    expect(wrapper.find('[data-testid="anschreibetabelle-leer"]').exists()).toBe(true)
  })

  it('stellt „M | S | Mit" für den gewinnenden Spielmacher dar', () => {
    const wrapper = mounten(historie)
    const text = wrapper.find('[data-testid="runde-1-B"]').text()
    expect(text).toContain('100')
    expect(text).toContain('120')
  })

  it('markiert den Geber mit „setzt aus"', () => {
    const wrapper = mounten(historie)
    expect(wrapper.find('[data-testid="setzt-aus-1-A"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="runde-1-A"]').text()).toContain('setzt aus')
  })

  it('annotiert den Schneider-Gegenspieler (0 Stiche) im normalen Spiel als 0', () => {
    const wrapper = mounten(historie)
    expect(wrapper.find('[data-testid="schneider-1-D"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="runde-1-D"]').text()).toContain('(0 Stiche)')
  })

  it('rückt den eingeklammerten Verlustwert ins erste Feld des Spielmachers', () => {
    const wrapper = mounten(historie)
    const verlust = wrapper.find('[data-testid="verlust-2-C"]')
    expect(verlust.exists()).toBe(true)
    expect(verlust.text()).toContain('(-250)')
  })

  it('zeigt bei einfachem Abgehen KEINE Schneider-Annotation (kein Stich-Zwang)', () => {
    const wrapper = mounten(historie)
    expect(wrapper.find('[data-testid="schneider-2-A"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="schneider-2-D"]').exists()).toBe(false)
  })

  it('weist den Rundenausgang je Runde aus (§5-Annotation)', () => {
    const wrapper = mounten(historie)
    expect(wrapper.find('[data-testid="ausgang-1"]').text()).toBe('gewonnen')
    expect(wrapper.find('[data-testid="ausgang-2"]').text()).toBe('einfaches Abgehen')
    expect(wrapper.find('[data-testid="ausgang-3"]').text()).toBe('gewonnen')
  })

  it('zeigt bei Tausender den Stern und keine Schneider-Annotation', () => {
    const wrapper = mounten(historie)
    expect(wrapper.find('[data-testid="stern-3-D"]').text()).toContain('★')
    expect(wrapper.find('[data-testid="schneider-3-A"]').exists()).toBe(false)
  })

  it('kennzeichnet die Tausender-Zeile als „außer Konkurrenz" ohne gezählte Nummer (FND-006)', () => {
    const wrapper = mounten(historie)
    // Tausender (Sequenz 3, zaehlrunde=null): außer-Konkurrenz-Markierung statt Rundennummer.
    expect(wrapper.find('[data-testid="ausser-konkurrenz-3"]').exists()).toBe(true)
    // Reguläre Runden (Sequenz 1/2) tragen keine solche Markierung.
    expect(wrapper.find('[data-testid="ausser-konkurrenz-1"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="ausser-konkurrenz-2"]').exists()).toBe(false)
  })

  it('friert den STAND bei Tausender ein (identisch zur Vorrunde)', () => {
    const wrapper = mounten(historie)
    expect(wrapper.find('[data-testid="stand-2-B"]').text()).toBe('220')
    expect(wrapper.find('[data-testid="stand-3-B"]').text()).toBe('220')
  })

  it('gibt den kumulierten STAND je Runde und Spieler aus', () => {
    const wrapper = mounten(historie)
    expect(wrapper.find('[data-testid="stand-1-B"]').text()).toBe('220')
    expect(wrapper.find('[data-testid="stand-2-C"]').text()).toBe('-80')
    expect(wrapper.find('[data-testid="stand-2-D"]').text()).toBe('50')
  })
})

describe('Anschreibetabelle bei 3 Spielern (ADR-017)', () => {
  /** Der Geber A ist Spielmacher: er spielt mit und trägt seine Werte ein. */
  const dreierRunde: RundenhistorieRunde = {
    rundennummer: 1,
    sequenz: 1,
    zaehlrunde: 1,
    geber: 'A',
    spielmacher: 'A',
    reizwert: 150,
    rundenausgang: 'gewonnenes Spiel',
    ist_tausender: false,
    verlustwert: 0,
    spieler: {
      A: zelle('spielmacher', { ist_geber: true, meldepunkte: 150, stichwerte: 100, hat_eigenen_stich: true }),
      B: zelle('gegenspieler', { meldepunkte: 0, stichwerte: 90, hat_eigenen_stich: true }),
      C: zelle('gegenspieler', { meldepunkte: 0, stichwerte: 60, hat_eigenen_stich: true }),
    },
    stand: { A: 250, B: 90, C: 60 },
  }
  const dreierHistorie: Rundenhistorie = { spiel_id: 8, spieler: ['A', 'B', 'C'], runden: [dreierRunde] }

  it('zeigt den mitspielenden Geber mit seinen Werten und ohne „setzt aus"', () => {
    const wrapper = mounten(dreierHistorie)
    expect(wrapper.find('[data-testid="setzt-aus-1-A"]').exists()).toBe(false)
    const text = wrapper.find('[data-testid="runde-1-A"]').text()
    expect(text).toContain('150')
    expect(text).toContain('100')
    expect(text).not.toContain('setzt aus')
  })

  it('führt die Geber-Spalte weiterhin mit dem Namen des Gebers', () => {
    const wrapper = mounten(dreierHistorie)
    expect(wrapper.text()).toContain('Geber')
    expect(wrapper.text()).toContain('A')
  })

  it('zeigt eine Spalte je Spieler – drei statt vier', () => {
    const wrapper = mounten(dreierHistorie)
    for (const name of ['A', 'B', 'C']) {
      expect(wrapper.find(`[data-testid="runde-1-${name}"]`).exists()).toBe(true)
    }
    expect(wrapper.find('[data-testid="runde-1-D"]').exists()).toBe(false)
  })
})

describe('Anschreibetabelle: Zeile „zu zahlen" (rule-set §20)', () => {
  /** Beträge liefert das Backend in ganzen Cent: Höchststand B = 220, je 10 Punkte Differenz 5 Cent. */
  const mitAbrechnung: Rundenhistorie = {
    ...historie,
    zu_zahlen_cent: { A: 75, B: 0, C: 150, D: 85 },
  }
  const normal = (text: string) => text.replace(/\u00a0/g, ' ')

  it('zeigt je zahlendem Spieler den Betrag im Euro-Format', () => {
    const wrapper = mounten(mitAbrechnung)
    expect(normal(wrapper.find('[data-testid="zu-zahlen-A"]').text())).toBe('0,75 €')
    expect(normal(wrapper.find('[data-testid="zu-zahlen-C"]').text())).toBe('1,50 €')
    expect(normal(wrapper.find('[data-testid="zu-zahlen-D"]').text())).toBe('0,85 €')
  })

  it('zeigt beim Spitzenreiter keinen Betrag an – die Zelle bleibt leer', () => {
    const zelle = mounten(mitAbrechnung).find('[data-testid="zu-zahlen-B"]')
    expect(zelle.exists()).toBe(true) // Spalte bleibt erhalten, damit die Tabelle ausgerichtet ist
    expect(zelle.text()).toBe('')
  })

  it('zeigt auch bei Gleichstand an der Spitze für keinen Spitzenreiter einen Betrag', () => {
    const wrapper = mounten({ ...historie, zu_zahlen_cent: { A: 0, B: 0, C: 150, D: 85 } })
    expect(wrapper.find('[data-testid="zu-zahlen-A"]').text()).toBe('')
    expect(wrapper.find('[data-testid="zu-zahlen-B"]').text()).toBe('')
    expect(normal(wrapper.find('[data-testid="zu-zahlen-C"]').text())).toBe('1,50 €')
  })

  it('blendet die ganze Zeile aus, wenn niemand etwas zahlen muss', () => {
    const wrapper = mounten({ ...historie, zu_zahlen_cent: { A: 0, B: 0, C: 0, D: 0 } })
    expect(wrapper.find('[data-testid="zu-zahlen"]').exists()).toBe(false)
  })

  it('steht als letzte Zeile direkt unter der letzten STAND-Zeile', () => {
    const wrapper = mounten(mitAbrechnung)
    const zeilen = wrapper.findAll('tbody tr')
    const letzte = zeilen[zeilen.length - 1]
    expect(letzte.attributes('data-testid')).toBe('zu-zahlen')
    expect(zeilen[zeilen.length - 2].text()).toContain('STAND')
  })

  it('erscheint genau einmal – nicht unter jeder Runde', () => {
    expect(mounten(mitAbrechnung).findAll('[data-testid="zu-zahlen"]')).toHaveLength(1)
  })

  it('benennt die Zeile verständlich', () => {
    const text = mounten(mitAbrechnung).find('[data-testid="zu-zahlen"]').text()
    expect(text).toContain('zu zahlen')
  })

  it('beschriftet die Zeile im laufenden Spiel mit „zu zahlen, wenn das Spiel jetzt endet"', () => {
    const text = mounten(mitAbrechnung).find('[data-testid="zu-zahlen"]').text()
    expect(text).toContain('zu zahlen, wenn das Spiel jetzt endet')
  })

  it('beschriftet die Zeile zum Spielende mit „Wer zahlt was in die Kasse"', () => {
    const wrapper = mount(Anschreibetabelle, { props: { historie: mitAbrechnung, spielende: true } })
    const text = wrapper.find('[data-testid="zu-zahlen"]').text()
    expect(text).toContain('Wer zahlt was in die Kasse')
    expect(text).not.toContain('jetzt endet')
  })

  it('funktioniert bei 3 Spielern mit drei Beträgen', () => {
    const dreierRunde: RundenhistorieRunde = {
      ...runde1,
      spieler: { A: runde1.spieler.A, B: runde1.spieler.B, C: runde1.spieler.C },
      stand: { A: 0, B: 220, C: 170 },
    }
    const wrapper = mounten({
      spiel_id: 8,
      spieler: ['A', 'B', 'C'],
      runden: [dreierRunde],
      zu_zahlen_cent: { A: 0, B: 80, C: 95 },
    })
    expect(normal(wrapper.find('[data-testid="zu-zahlen-B"]').text())).toBe('0,80 €')
    expect(normal(wrapper.find('[data-testid="zu-zahlen-C"]').text())).toBe('0,95 €')
    expect(wrapper.find('[data-testid="zu-zahlen-A"]').text()).toBe('') // Spitzenreiter
    expect(wrapper.find('[data-testid="zu-zahlen-D"]').exists()).toBe(false)
  })

  it('blendet die Zeile aus, wenn das Backend keine Abrechnung liefert', () => {
    expect(mounten(historie).find('[data-testid="zu-zahlen"]').exists()).toBe(false)
  })

  it('zeigt ohne Runden nur den Leerhinweis', () => {
    const wrapper = mounten({
      spiel_id: 7, spieler: ['A', 'B'], runden: [], zu_zahlen_cent: { A: 0, B: 50 },
    })
    expect(wrapper.find('[data-testid="zu-zahlen"]').exists()).toBe(false)
  })
})

describe('Anschreibetabelle: Sternesumme in der Endabrechnung', () => {
  /** `historie` enthält in Runde 3 einen Tausender (D ★); das Backend liefert die Summe je Spieler. */
  const mitSternen: Rundenhistorie = {
    ...historie,
    sterne: { A: 0, B: 0, C: 1, D: 2 },
    zu_zahlen_cent: { A: 75, B: 0, C: 150, D: 85 },
  }
  const zeile = '[data-testid="sterne-summe"]'
  const endabrechnung = (h: Rundenhistorie) =>
    mount(Anschreibetabelle, { props: { historie: h, spielende: true } })

  it('zeigt die Sternesumme je Spieler', () => {
    const wrapper = endabrechnung(mitSternen)
    expect(wrapper.find('[data-testid="sterne-summe-D"]').text()).toBe('★★')
    expect(wrapper.find('[data-testid="sterne-summe-C"]').text()).toBe('★')
  })

  it('lässt die Zelle leer, wenn ein Spieler keine Sterne hat', () => {
    const wrapper = endabrechnung(mitSternen)
    expect(wrapper.find('[data-testid="sterne-summe-A"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="sterne-summe-A"]').text()).toBe('')
  })

  it('steht zwischen der letzten STAND-Zeile und der Abrechnung', () => {
    const wrapper = endabrechnung(mitSternen)
    const zeilen = wrapper.findAll('tbody tr')
    const ids = zeilen.map((z) => z.attributes('data-testid'))
    const anzahl = zeilen.length
    expect(ids[anzahl - 2]).toBe('sterne-summe')
    expect(ids[anzahl - 1]).toBe('zu-zahlen')
    expect(zeilen[anzahl - 3].text()).toContain('STAND')
  })

  it('benennt die Zeile verständlich', () => {
    expect(endabrechnung(mitSternen).find(zeile).text()).toContain('Sterne')
  })

  it('entfällt, wenn kein Tausender gespielt wurde', () => {
    const ohneTausender: Rundenhistorie = {
      ...mitSternen,
      runden: [runde1, runde2],
      sterne: { A: 0, B: 0, C: 0, D: 0 },
    }
    expect(endabrechnung(ohneTausender).find(zeile).exists()).toBe(false)
  })

  it('entfällt im laufenden Spiel – dort zählt nur die Endabrechnung', () => {
    expect(mounten(mitSternen).find(zeile).exists()).toBe(false)
  })

  it('entfällt, wenn das Backend keine Sternesumme liefert', () => {
    const ohneFeld: Rundenhistorie = { ...historie, zu_zahlen_cent: { A: 75, B: 0, C: 150, D: 85 } }
    expect(endabrechnung(ohneFeld).find(zeile).exists()).toBe(false)
  })

  it('erscheint auch dann, wenn niemand zahlen muss', () => {
    const wrapper = endabrechnung({ ...mitSternen, zu_zahlen_cent: { A: 0, B: 0, C: 0, D: 0 } })
    expect(wrapper.find(zeile).exists()).toBe(true)
    expect(wrapper.find('[data-testid="zu-zahlen"]').exists()).toBe(false)
  })

  it('funktioniert bei 3 Spielern', () => {
    const dreierRunde: RundenhistorieRunde = {
      ...runde3,
      spieler: { A: runde3.spieler.A, B: runde3.spieler.B, C: runde3.spieler.D },
    }
    const wrapper = endabrechnung({
      spiel_id: 8,
      spieler: ['A', 'B', 'C'],
      runden: [dreierRunde],
      sterne: { A: 0, B: 0, C: 1 },
    })
    expect(wrapper.find('[data-testid="sterne-summe-C"]').text()).toBe('★')
    expect(wrapper.find('[data-testid="sterne-summe-D"]').exists()).toBe(false)
  })
})
