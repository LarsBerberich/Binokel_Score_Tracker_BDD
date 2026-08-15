import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import SpielAnlegenForm from './SpielAnlegenForm.vue'

/** Füllt das Formular mit vier gültigen Namen. */
async function fuelleGueltig(wrapper: ReturnType<typeof mount>) {
  const namen = ['Anna', 'Bert', 'Cara', 'Dirk']
  for (let i = 0; i < 4; i++) {
    await wrapper.find(`[data-testid="spieler-${i}"]`).setValue(namen[i])
  }
}

describe('SpielAnlegenForm', () => {
  it('rendert vier Spieler-Eingabefelder', () => {
    const wrapper = mount(SpielAnlegenForm)
    for (let i = 0; i < 4; i++) {
      expect(wrapper.find(`[data-testid="spieler-${i}"]`).exists()).toBe(true)
    }
  })

  it('sperrt den Absenden-Button, solange die Eingaben ungültig sind', () => {
    const wrapper = mount(SpielAnlegenForm)
    const button = wrapper.find('[data-testid="absenden"]')
    expect(button.attributes('disabled')).toBeDefined()
  })

  it('gibt einen Validierungshinweis bei fehlenden Namen aus', async () => {
    const wrapper = mount(SpielAnlegenForm)
    await wrapper.find('form').trigger('submit')
    expect(wrapper.find('[data-testid="validierungsfehler"]').text()).toContain(
      'alle vier Spielernamen',
    )
    expect(wrapper.emitted('absenden')).toBeUndefined()
  })

  it('weist doppelte Spielernamen ab', async () => {
    const wrapper = mount(SpielAnlegenForm)
    for (let i = 0; i < 4; i++) {
      await wrapper.find(`[data-testid="spieler-${i}"]`).setValue('Anna')
    }
    await wrapper.find('form').trigger('submit')
    expect(wrapper.find('[data-testid="validierungsfehler"]').text()).toContain('eindeutig')
    expect(wrapper.emitted('absenden')).toBeUndefined()
  })

  it('weist eine Rundenanzahl ab, die kein Vielfaches von 4 ist', async () => {
    const wrapper = mount(SpielAnlegenForm)
    await fuelleGueltig(wrapper)
    await wrapper.find('[data-testid="rundenanzahl"]').setValue(10)
    await wrapper.find('form').trigger('submit')
    expect(wrapper.find('[data-testid="validierungsfehler"]').text()).toContain('Vielfaches von 4')
    expect(wrapper.emitted('absenden')).toBeUndefined()
  })

  it('emittiert absenden mit getrimmten Namen und Rundenanzahl bei gültiger Eingabe', async () => {
    const wrapper = mount(SpielAnlegenForm)
    await wrapper.find('[data-testid="spieler-0"]').setValue('  Anna ')
    await wrapper.find('[data-testid="spieler-1"]').setValue('Bert')
    await wrapper.find('[data-testid="spieler-2"]').setValue('Cara')
    await wrapper.find('[data-testid="spieler-3"]').setValue('Dirk')
    await wrapper.find('[data-testid="rundenanzahl"]').setValue(8)
    await wrapper.find('form').trigger('submit')

    const events = wrapper.emitted('absenden')
    expect(events).toHaveLength(1)
    expect(events?.[0][0]).toEqual({
      spieler: ['Anna', 'Bert', 'Cara', 'Dirk'],
      rundenanzahl: 8,
    })
  })

  it('sperrt das Formular und den Button, wenn laedt=true', () => {
    const wrapper = mount(SpielAnlegenForm, { props: { laedt: true } })
    expect(wrapper.find('fieldset').attributes('disabled')).toBeDefined()
    expect(wrapper.find('[data-testid="absenden"]').attributes('disabled')).toBeDefined()
  })

  it('zeigt eine Server-Fehlermeldung an', () => {
    const wrapper = mount(SpielAnlegenForm, { props: { fehler: 'Genau 4 Spieler erforderlich.' } })
    expect(wrapper.find('[data-testid="server-fehler"]').text()).toBe(
      'Genau 4 Spieler erforderlich.',
    )
  })
})
