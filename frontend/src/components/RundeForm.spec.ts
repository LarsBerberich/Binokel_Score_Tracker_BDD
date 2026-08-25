import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import RundeForm from './RundeForm.vue'

const aktive = ['Bernd', 'Carla', 'Dirk']

function mountForm() {
  return mount(RundeForm, {
    props: { rundennummer: 1, geber: 'Anna', aktive },
  })
}

describe('RundeForm', () => {
  it('leitet die Gegenspieler aus aktiven Spielern minus Spielmacher ab', async () => {
    const wrapper = mountForm()
    // Default-Spielmacher = erster aktiver Spieler (Bernd)
    expect(wrapper.find('[data-testid="gegenspieler"]').text()).toBe('Carla, Dirk')

    await wrapper.find('[data-testid="spielmacher"]').setValue('Carla')
    expect(wrapper.find('[data-testid="gegenspieler"]').text()).toBe('Bernd, Dirk')
  })

  it('emittiert einfaches Abgehen mit Meldepunkten je Gegenspieler und ohne Stich-Zwang', async () => {
    const wrapper = mountForm()
    await wrapper.find('[data-testid="typ"]').setValue('einfaches_abgehen')
    await wrapper.find('[data-testid="reizwert"]').setValue(150)
    await wrapper.find('[data-testid="gs-meldepunkte-Carla"]').setValue(40)
    await wrapper.find('[data-testid="gs-meldepunkte-Dirk"]').setValue(20)

    // Kein Stichwerte-Feld, keine 250er-Kontrollsumme
    expect(wrapper.find('[data-testid="gs-stichwerte-Carla"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="runde-absenden"]').attributes('disabled')).toBeUndefined()

    await wrapper.find('form').trigger('submit')
    const events = wrapper.emitted('absenden')
    expect(events).toHaveLength(1)
    expect(events?.[0][0]).toEqual({
      typ: 'einfaches_abgehen',
      rundennummer: 1,
      spielmacher: 'Bernd',
      geber: 'Anna',
      reizwert: 150,
      gegenspieler: [
        { name: 'Carla', meldepunkte: 40 },
        { name: 'Dirk', meldepunkte: 20 },
      ],
    })
  })

  it('sperrt das Absenden, wenn Meldepunkte das Maximum (1800) überschreiten', async () => {
    const wrapper = mountForm()
    await wrapper.find('[data-testid="typ"]').setValue('einfaches_abgehen')
    await wrapper.find('[data-testid="reizwert"]').setValue(150)
    await wrapper.find('[data-testid="gs-meldepunkte-Carla"]').setValue(1900)

    expect(wrapper.find('[data-testid="meldepunkte-fehler"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="runde-absenden"]').attributes('disabled')).toBeDefined()

    await wrapper.find('form').trigger('submit')
    expect(wrapper.emitted('absenden')).toBeUndefined()
  })

  it('bietet „Doppeltes Abgehen" nicht als Rundentyp an (wird automatisch abgeleitet)', () => {
    const wrapper = mountForm()
    const werte = wrapper
      .find('[data-testid="typ"]')
      .findAll('option')
      .map((o) => o.element.value)
    expect(werte).toEqual([
      'normal',
      'einfaches_abgehen',
      'tausender_gewonnen',
      'tausender_verloren',
    ])
  })

  it('emittiert einen vollständigen Tausender-Request ohne Zahlenfelder', async () => {
    const wrapper = mountForm()
    await wrapper.find('[data-testid="typ"]').setValue('tausender_gewonnen')

    // Reizwert-Feld entfällt bei Tausender
    expect(wrapper.find('[data-testid="reizwert"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="runde-absenden"]').attributes('disabled')).toBeUndefined()

    await wrapper.find('form').trigger('submit')
    const events = wrapper.emitted('absenden')
    expect(events).toHaveLength(1)
    expect(events?.[0][0]).toEqual({
      typ: 'tausender_gewonnen',
      rundennummer: 1,
      spielmacher: 'Bernd',
      geber: 'Anna',
    })
  })

  it('sperrt die normale Runde, solange die Stichwerte-Summe nicht 250 ergibt', async () => {
    const wrapper = mountForm()
    await wrapper.find('[data-testid="sm-stichwerte"]').setValue(100)

    expect(wrapper.find('[data-testid="stichwerte-summe"]').text()).toContain('100 / 250')
    expect(wrapper.find('[data-testid="runde-absenden"]').attributes('disabled')).toBeDefined()

    await wrapper.find('form').trigger('submit')
    expect(wrapper.emitted('absenden')).toBeUndefined()
  })

  it('berechnet den dritten Stichwert automatisch und emittiert die normale Runde', async () => {
    const wrapper = mountForm()
    await wrapper.find('[data-testid="reizwert"]').setValue(180)
    await wrapper.find('[data-testid="sm-meldepunkte"]').setValue(60)
    await wrapper.find('[data-testid="gs-meldepunkte-Carla"]').setValue(20)
    // Zwei Stichwerte genügen (§8.2) – der dritte (Dirk) wird automatisch = 250 − 130 − 60.
    await wrapper.find('[data-testid="sm-stichwerte"]').setValue(130)
    await wrapper.find('[data-testid="gs-stichwerte-Carla"]').setValue(60)

    const dirkFeld = wrapper.find('[data-testid="gs-stichwerte-Dirk"]')
    expect((dirkFeld.element as HTMLInputElement).value).toBe('60')
    expect(dirkFeld.attributes('readonly')).toBeDefined()
    expect(wrapper.find('[data-testid="stichwerte-summe"]').text()).toContain('250 / 250')
    expect(wrapper.find('[data-testid="runde-absenden"]').attributes('disabled')).toBeUndefined()

    await wrapper.find('form').trigger('submit')
    const events = wrapper.emitted('absenden')
    expect(events).toHaveLength(1)
    expect(events?.[0][0]).toEqual({
      typ: 'normal',
      rundennummer: 1,
      spielmacher: 'Bernd',
      geber: 'Anna',
      reizwert: 180,
      meldepunkte: 60,
      stichwerte: 130,
      hat_eigenen_stich: true,
      gegenspieler: [
        { name: 'Carla', meldepunkte: 20, stichwerte: 60, hat_eigenen_stich: true },
        { name: 'Dirk', meldepunkte: 0, stichwerte: 60, hat_eigenen_stich: true },
      ],
    })
  })

  it('leitet „kein eigener Stich" aus einem Stichwert von 0 ab (012.3)', async () => {
    const wrapper = mountForm()
    await wrapper.find('[data-testid="reizwert"]').setValue(150)
    await wrapper.find('[data-testid="sm-meldepunkte"]').setValue(60)
    await wrapper.find('[data-testid="gs-meldepunkte-Carla"]').setValue(20)
    await wrapper.find('[data-testid="gs-meldepunkte-Dirk"]').setValue(40)
    // sm 130 + Carla 120 → Dirk automatisch 0 → Dirk hat keinen eigenen Stich.
    await wrapper.find('[data-testid="sm-stichwerte"]').setValue(130)
    await wrapper.find('[data-testid="gs-stichwerte-Carla"]').setValue(120)

    expect(
      (wrapper.find('[data-testid="gs-stichwerte-Dirk"]').element as HTMLInputElement).value,
    ).toBe('0')

    await wrapper.find('form').trigger('submit')
    expect(wrapper.emitted('absenden')?.[0][0]).toEqual({
      typ: 'normal',
      rundennummer: 1,
      spielmacher: 'Bernd',
      geber: 'Anna',
      reizwert: 150,
      meldepunkte: 60,
      stichwerte: 130,
      hat_eigenen_stich: true,
      gegenspieler: [
        { name: 'Carla', meldepunkte: 20, stichwerte: 120, hat_eigenen_stich: true },
        { name: 'Dirk', meldepunkte: 40, stichwerte: 0, hat_eigenen_stich: false },
      ],
    })
  })

  it('weist auf doppeltes Abgehen hin, wenn der Spielmacher den Reizwert nicht erreicht (012.7)', async () => {
    const wrapper = mountForm()
    await wrapper.find('[data-testid="reizwert"]').setValue(200)
    await wrapper.find('[data-testid="sm-meldepunkte"]').setValue(20)
    // M+S Spielmacher = 20 + 130 = 150 < 200; Summe 250 gültig (Dirk automatisch 60).
    await wrapper.find('[data-testid="sm-stichwerte"]').setValue(130)
    await wrapper.find('[data-testid="gs-stichwerte-Carla"]').setValue(60)

    expect(wrapper.find('[data-testid="doppeltes-abgehen-hinweis"]').exists()).toBe(true)
  })

  it('sperrt die Runde und zeigt einen Fehler, wenn zwei Stichwerte 250 übersteigen (012.5)', async () => {
    const wrapper = mountForm()
    await wrapper.find('[data-testid="reizwert"]').setValue(180)
    // sm 200 + Carla 100 → Dirk automatisch 250 − 300 = −50 (ungültig).
    await wrapper.find('[data-testid="sm-stichwerte"]').setValue(200)
    await wrapper.find('[data-testid="gs-stichwerte-Carla"]').setValue(100)

    expect(
      (wrapper.find('[data-testid="gs-stichwerte-Dirk"]').element as HTMLInputElement).value,
    ).toBe('-50')
    expect(wrapper.find('[data-testid="stichwerte-fehler"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="runde-absenden"]').attributes('disabled')).toBeDefined()

    await wrapper.find('form').trigger('submit')
    expect(wrapper.emitted('absenden')).toBeUndefined()
  })

  it('setzt das Formular nach einem Rundenwechsel zurück (Bugfix 012.6)', async () => {
    const wrapper = mountForm()
    await wrapper.find('[data-testid="typ"]').setValue('einfaches_abgehen')
    await wrapper.find('[data-testid="reizwert"]').setValue(220)
    await wrapper.find('[data-testid="gs-meldepunkte-Carla"]').setValue(40)

    // Nächste Runde: Parent erhöht die Rundennummer und rotiert Geber/aktive Spieler.
    await wrapper.setProps({ rundennummer: 2, geber: 'Bernd', aktive: ['Anna', 'Carla', 'Dirk'] })

    // Rundentyp zurück auf „Normales Spiel", Reizwert auf Minimum, Detailwerte genullt.
    const typEl = wrapper.find('[data-testid="typ"]').element as HTMLSelectElement
    expect(typEl.value).toBe('normal')
    const reizwertEl = wrapper.find('[data-testid="reizwert"]').element as HTMLInputElement
    expect(reizwertEl.value).toBe('150')
    const meldeEl = wrapper.find('[data-testid="gs-meldepunkte-Carla"]').element as HTMLInputElement
    expect(meldeEl.value).toBe('0')
  })

  it('zeigt eine übergebene Fehlermeldung an', () => {
    const wrapper = mount(RundeForm, {
      props: { rundennummer: 1, geber: 'Anna', aktive, fehler: 'Pflichtfeld fehlt.' },
    })
    expect(wrapper.find('[data-testid="runde-fehler"]').text()).toBe('Pflichtfeld fehlt.')
  })

  // ── TASK-016: Zehner-Eingabe (§9.1/§9.4) ─────────────────────────────────────

  it('erfasst Stichwerte in Zehnerschritten (step=10)', () => {
    const wrapper = mountForm()
    expect(wrapper.find('[data-testid="sm-stichwerte"]').attributes('step')).toBe('10')
    expect(wrapper.find('[data-testid="gs-stichwerte-Carla"]').attributes('step')).toBe('10')
  })

  it('lässt eine normale Runde mit Zehner-Stichwerten (100+90+60=250) zu und liefert den Auto-Wert in Zehnern', async () => {
    const wrapper = mountForm()
    await wrapper.find('[data-testid="sm-stichwerte"]').setValue(100)
    await wrapper.find('[data-testid="gs-stichwerte-Carla"]').setValue(90)

    // Auto-3. Stichwert (Dirk) = 250 − 100 − 90 = 60 (Zehner).
    expect(
      (wrapper.find('[data-testid="gs-stichwerte-Dirk"]').element as HTMLInputElement).value,
    ).toBe('60')
    expect(wrapper.find('[data-testid="stichwerte-summe"]').text()).toContain('250 / 250')
    expect(wrapper.find('[data-testid="stichwerte-modulo-fehler"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="runde-absenden"]').attributes('disabled')).toBeUndefined()

    await wrapper.find('form').trigger('submit')
    expect(wrapper.emitted('absenden')).toHaveLength(1)
  })

  it('sperrt die Runde bei getippten Einerwerten (99+91+60=250) trotz korrekter Summe (Modulo-Guard)', async () => {
    const wrapper = mountForm()
    await wrapper.find('[data-testid="sm-stichwerte"]').setValue(99)
    await wrapper.find('[data-testid="gs-stichwerte-Carla"]').setValue(91)

    // Summe ergibt zwar 250 (Dirk automatisch 60), aber 99 und 91 sind keine Zehner.
    expect(wrapper.find('[data-testid="stichwerte-summe"]').text()).toContain('250 / 250')
    expect(wrapper.find('[data-testid="stichwerte-modulo-fehler"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="runde-absenden"]').attributes('disabled')).toBeDefined()

    await wrapper.find('form').trigger('submit')
    expect(wrapper.emitted('absenden')).toBeUndefined()
  })

  // ── TASK-015: FND-001 — Auto-Stichwert nach Löschen wieder editierbar ────────

  it('hebt das read-only des Auto-Stichwerts auf, wenn ein manueller Wert geleert wird (FND-001)', async () => {
    const wrapper = mountForm()
    // Bernd (Spielmacher) und Carla setzen → Dirk automatisch + read-only.
    await wrapper.find('[data-testid="sm-stichwerte"]').setValue(100)
    await wrapper.find('[data-testid="gs-stichwerte-Carla"]').setValue(90)
    expect(wrapper.find('[data-testid="gs-stichwerte-Dirk"]').attributes('readonly')).toBeDefined()

    // Carla wieder leeren (0) → nur noch ein manueller Wert → Dirk wieder editierbar.
    await wrapper.find('[data-testid="gs-stichwerte-Carla"]').setValue(0)
    expect(wrapper.find('[data-testid="gs-stichwerte-Dirk"]').attributes('readonly')).toBeUndefined()
  })

  // ── TASK-016: Endrunden-Tiebreak (§9.4) ──────────────────────────────────────

  it('bietet in der letzten Runde optionale 1er-Tiebreak-Felder und emittiert die exakten Werte', async () => {
    const wrapper = mount(RundeForm, {
      props: { rundennummer: 4, geber: 'Anna', aktive, rundenanzahl: 4 },
    })
    expect(wrapper.find('[data-testid="tiebreak-block"]').exists()).toBe(true)

    await wrapper.find('[data-testid="sm-stichwerte"]').setValue(100)
    await wrapper.find('[data-testid="gs-stichwerte-Carla"]').setValue(90)
    await wrapper.find('[data-testid="tiebreak-Bernd"]').setValue(78)
    await wrapper.find('[data-testid="tiebreak-Carla"]').setValue(72)

    await wrapper.find('form').trigger('submit')
    const tiebreak = wrapper.emitted('tiebreak-stichwerte')
    expect(tiebreak).toHaveLength(1)
    expect(tiebreak?.[0][0]).toEqual({ Bernd: 78, Carla: 72 })
  })

  it('zeigt in einer normalen (nicht letzten) Runde keine Tiebreak-Felder', () => {
    const wrapper = mount(RundeForm, {
      props: { rundennummer: 1, geber: 'Anna', aktive, rundenanzahl: 4 },
    })
    expect(wrapper.find('[data-testid="tiebreak-block"]').exists()).toBe(false)
  })

  // ── TASK-014 Slice 6: Korrektur der letzten Runde (Vorbelegung) ─────────────

  it('befüllt das Formular im Korrektur-Modus mit den Werten der letzten Runde', () => {
    const wrapper = mount(RundeForm, {
      props: {
        rundennummer: 3,
        geber: 'Anna',
        aktive,
        korrekturModus: true,
        vorbelegung: {
          typ: 'normal' as const,
          reizwert: 180,
          spielmacher: 'Carla',
          meldepunkte: { Bernd: 40, Carla: 100, Dirk: 20 },
          stichwerte: { Bernd: 60, Carla: 130, Dirk: 60 },
        },
      },
    })

    expect((wrapper.find('[data-testid="typ"]').element as HTMLSelectElement).value).toBe('normal')
    expect((wrapper.find('[data-testid="spielmacher"]').element as HTMLSelectElement).value).toBe(
      'Carla',
    )
    expect((wrapper.find('[data-testid="reizwert"]').element as HTMLInputElement).value).toBe('180')
    // Carla ist Spielmacher → Gegenspieler Bernd/Dirk.
    expect((wrapper.find('[data-testid="sm-meldepunkte"]').element as HTMLInputElement).value).toBe(
      '100',
    )
    expect(
      (wrapper.find('[data-testid="gs-meldepunkte-Bernd"]').element as HTMLInputElement).value,
    ).toBe('40')
    expect(
      (wrapper.find('[data-testid="gs-stichwerte-Dirk"]').element as HTMLInputElement).value,
    ).toBe('60')
  })

  it('kennzeichnet den Absenden-Button im Korrektur-Modus und emittiert die korrigierten Werte', async () => {
    const wrapper = mount(RundeForm, {
      props: {
        rundennummer: 2,
        geber: 'Anna',
        aktive,
        korrekturModus: true,
        vorbelegung: {
          typ: 'einfaches_abgehen' as const,
          reizwert: 150,
          spielmacher: 'Bernd',
          meldepunkte: { Bernd: 0, Carla: 40, Dirk: 20 },
          stichwerte: { Bernd: 0, Carla: 0, Dirk: 0 },
        },
      },
    })

    expect(wrapper.find('[data-testid="runde-absenden"]').text()).toContain('Korrektur speichern')

    // Meldepunkte korrigieren und speichern.
    await wrapper.find('[data-testid="gs-meldepunkte-Carla"]').setValue(60)
    await wrapper.find('form').trigger('submit')

    const events = wrapper.emitted('absenden')
    expect(events).toHaveLength(1)
    expect(events?.[0][0]).toEqual({
      typ: 'einfaches_abgehen',
      rundennummer: 2,
      spielmacher: 'Bernd',
      geber: 'Anna',
      reizwert: 150,
      gegenspieler: [
        { name: 'Carla', meldepunkte: 60 },
        { name: 'Dirk', meldepunkte: 20 },
      ],
    })
  })
})
