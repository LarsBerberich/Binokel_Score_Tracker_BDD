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
