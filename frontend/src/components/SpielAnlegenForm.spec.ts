import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import SpielAnlegenForm from './SpielAnlegenForm.vue'

type Wrapper = ReturnType<typeof mount>

/** Trägt die Namen in die Felder spieler-0 … ein (nur so viele, wie übergeben werden). */
async function fuelle(wrapper: Wrapper, namen: string[]) {
  for (let i = 0; i < namen.length; i++) {
    await wrapper.find(`[data-testid="spieler-${i}"]`).setValue(namen[i])
  }
}

const VIER = ['Anna', 'Bert', 'Cara', 'Dirk']
const DREI = ['Anna', 'Bert', 'Cara']

describe('SpielAnlegenForm', () => {
  it('rendert vier Spieler-Eingabefelder; das vierte ist optional', () => {
    const wrapper = mount(SpielAnlegenForm)
    for (let i = 0; i < 4; i++) {
      expect(wrapper.find(`[data-testid="spieler-${i}"]`).exists()).toBe(true)
    }
    expect(wrapper.find('[data-testid="spieler-2"]').attributes('required')).toBeDefined()
    expect(wrapper.find('[data-testid="spieler-3"]').attributes('required')).toBeUndefined()
  })

  it('sperrt den Absenden-Button, solange die Eingaben ungültig sind', () => {
    const wrapper = mount(SpielAnlegenForm)
    const button = wrapper.find('[data-testid="absenden"]')
    expect(button.attributes('disabled')).toBeDefined()
  })

  it('gibt einen Validierungshinweis aus, wenn weniger als drei Namen eingetragen sind', async () => {
    const wrapper = mount(SpielAnlegenForm)
    await fuelle(wrapper, ['Anna', 'Bert'])
    await wrapper.find('form').trigger('submit')
    expect(wrapper.find('[data-testid="validierungsfehler"]').text()).toContain(
      'mindestens drei Spielernamen',
    )
    expect(wrapper.emitted('absenden')).toBeUndefined()
  })

  it('weist doppelte Spielernamen ab', async () => {
    const wrapper = mount(SpielAnlegenForm)
    await fuelle(wrapper, ['Anna', 'Anna', 'Anna'])
    await wrapper.find('form').trigger('submit')
    expect(wrapper.find('[data-testid="validierungsfehler"]').text()).toContain('eindeutig')
    expect(wrapper.emitted('absenden')).toBeUndefined()
  })

  describe.each([
    { name: '4 Spieler', namen: VIER, teiler: 4, ungueltig: 10, gueltig: 8 },
    { name: '3 Spieler', namen: DREI, teiler: 3, ungueltig: 10, gueltig: 9 },
  ])('bei $name', ({ namen, teiler, ungueltig, gueltig }) => {
    it(`weist eine Rundenanzahl ab, die kein Vielfaches von ${teiler} ist`, async () => {
      const wrapper = mount(SpielAnlegenForm)
      await fuelle(wrapper, namen)
      await wrapper.find('[data-testid="rundenanzahl"]').setValue(ungueltig)
      await wrapper.find('form').trigger('submit')
      expect(wrapper.find('[data-testid="validierungsfehler"]').text()).toContain(
        `Vielfaches von ${teiler}`,
      )
      expect(wrapper.emitted('absenden')).toBeUndefined()
    })

    it(`bietet die Rundenanzahl in Schritten von ${teiler} an`, async () => {
      const wrapper = mount(SpielAnlegenForm)
      await fuelle(wrapper, namen)
      const feld = wrapper.find('[data-testid="rundenanzahl"]')
      expect(feld.attributes('step')).toBe(String(teiler))
      expect(feld.attributes('min')).toBe(String(teiler))
    })

    it('akzeptiert die Standardrundenanzahl 12, die für beide Varianten gültig ist', async () => {
      const wrapper = mount(SpielAnlegenForm)
      await fuelle(wrapper, namen)
      await wrapper.find('form').trigger('submit')
      expect(wrapper.emitted('absenden')?.[0][0]).toEqual({ spieler: namen, rundenanzahl: 12 })
    })

    it('emittiert absenden mit getrimmten Namen und gültiger Rundenanzahl', async () => {
      const wrapper = mount(SpielAnlegenForm)
      await fuelle(wrapper, ['  Anna ', ...namen.slice(1)])
      await wrapper.find('[data-testid="rundenanzahl"]').setValue(gueltig)
      await wrapper.find('form').trigger('submit')

      const events = wrapper.emitted('absenden')
      expect(events).toHaveLength(1)
      expect(events?.[0][0]).toEqual({ spieler: namen, rundenanzahl: gueltig })
    })
  })

  it('sperrt das Formular und den Button, wenn laedt=true', () => {
    const wrapper = mount(SpielAnlegenForm, { props: { laedt: true } })
    expect(wrapper.find('fieldset').attributes('disabled')).toBeDefined()
    expect(wrapper.find('[data-testid="absenden"]').attributes('disabled')).toBeDefined()
  })

  it('zeigt eine Server-Fehlermeldung an', () => {
    const wrapper = mount(SpielAnlegenForm, { props: { fehler: 'Ungültige Spielerzahl.' } })
    expect(wrapper.find('[data-testid="server-fehler"]').text()).toBe('Ungültige Spielerzahl.')
  })
})
