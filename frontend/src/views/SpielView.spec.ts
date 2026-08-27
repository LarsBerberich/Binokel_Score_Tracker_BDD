import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount, RouterLinkStub } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import SpielView from './SpielView.vue'
import { useSpielStore } from '../stores/spiel'

vi.mock('../api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api')>()
  return {
    ...actual,
    spielLaden: vi.fn(),
    punktestaendeLaden: vi.fn(),
    rundenHistorieLaden: vi.fn(),
    letzteRundeAktualisieren: vi.fn(),
  }
})
import {
  ApiError,
  letzteRundeAktualisieren,
  punktestaendeLaden,
  rundenHistorieLaden,
  spielLaden,
  type Rundenhistorie,
} from '../api'

const spielLadenMock = vi.mocked(spielLaden)
const punktestaendeLadenMock = vi.mocked(punktestaendeLaden)
const rundenHistorieLadenMock = vi.mocked(rundenHistorieLaden)
const letzteRundeAktualisierenMock = vi.mocked(letzteRundeAktualisieren)
const beispielSpiel = { id: 3, rundenanzahl: 12, spieler: ['Anna', 'Bernd', 'Carla', 'Dirk'] }

const leereHistorie = { spiel_id: 3, spieler: ['Anna', 'Bernd', 'Carla', 'Dirk'], runden: [] }

/** Minimale valide Historie-Runde (FND-006: sequenz + zaehlrunde). */
function macheRunde(
  sequenz: number,
  zaehlrunde: number | null,
  istTausender = false,
): Rundenhistorie['runden'][number] {
  return {
    rundennummer: sequenz,
    sequenz,
    zaehlrunde,
    geber: 'Anna',
    spielmacher: 'Bernd',
    reizwert: 150,
    rundenausgang: istTausender ? 'Tausender gewonnen' : 'gewonnenes Spiel',
    ist_tausender: istTausender,
    verlustwert: 0,
    spieler: {
      Anna: { rolle: 'geber', meldepunkte: 0, stichwerte: 0, mitpunkte: 0, hat_eigenen_stich: false, stern: false },
      Bernd: { rolle: 'spielmacher', meldepunkte: 100, stichwerte: 100, mitpunkte: 0, hat_eigenen_stich: true, stern: istTausender },
      Carla: { rolle: 'gegenspieler', meldepunkte: 40, stichwerte: 90, mitpunkte: 0, hat_eigenen_stich: true, stern: false },
      Dirk: { rolle: 'gegenspieler', meldepunkte: 0, stichwerte: 60, mitpunkte: 0, hat_eigenen_stich: true, stern: false },
    },
    stand: { Anna: 0, Bernd: 200, Carla: 130, Dirk: 60 },
  }
}

/** Historie mit einer normalen Runde (Anna Geber, Bernd Spielmacher). */
const historieMitRunde: Rundenhistorie = {
  spiel_id: 3,
  spieler: ['Anna', 'Bernd', 'Carla', 'Dirk'],
  runden: [
    {
      rundennummer: 1,
      sequenz: 1,
      zaehlrunde: 1,
      geber: 'Anna',
      spielmacher: 'Bernd',
      reizwert: 150,
      rundenausgang: 'gewonnenes Spiel',
      ist_tausender: false,
      verlustwert: 0,
      spieler: {
        Anna: { rolle: 'geber' as const, meldepunkte: 0, stichwerte: 0, mitpunkte: 0, hat_eigenen_stich: false, stern: false },
        Bernd: { rolle: 'spielmacher' as const, meldepunkte: 100, stichwerte: 100, mitpunkte: 0, hat_eigenen_stich: true, stern: false },
        Carla: { rolle: 'gegenspieler' as const, meldepunkte: 40, stichwerte: 90, mitpunkte: 0, hat_eigenen_stich: true, stern: false },
        Dirk: { rolle: 'gegenspieler' as const, meldepunkte: 0, stichwerte: 60, mitpunkte: 0, hat_eigenen_stich: true, stern: false },
      },
      stand: { Anna: 0, Bernd: 200, Carla: 130, Dirk: 60 },
    },
  ],
}

describe('SpielView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    spielLadenMock.mockReset()
    punktestaendeLadenMock.mockReset()
    rundenHistorieLadenMock.mockReset()
    letzteRundeAktualisierenMock.mockReset()
    rundenHistorieLadenMock.mockResolvedValue(leereHistorie)
    punktestaendeLadenMock.mockResolvedValue({
      spiel_id: 3,
      punktestaende: { Anna: 0, Bernd: 0, Carla: 0, Dirk: 0 },
      sterne: { Anna: 0, Bernd: 0, Carla: 0, Dirk: 0 },
    })
  })

  it('nutzt das Spiel aus dem Store und zeigt Runde 1 mit Anna als Geber', () => {
    useSpielStore().setzeSpiel(beispielSpiel)
    const wrapper = mount(SpielView, { props: { spielId: '3' } })

    expect(spielLadenMock).not.toHaveBeenCalled()
    expect(wrapper.find('[data-testid="rundenfortschritt"]').text()).toContain('Runde 1 / 12')
    expect(wrapper.find('[data-testid="geber"]').text()).toBe('Anna')
  })

  it('lädt das Spiel per API, wenn der Store leer ist', async () => {
    spielLadenMock.mockResolvedValue(beispielSpiel)
    const wrapper = mount(SpielView, { props: { spielId: '3' } })
    await flushPromises()

    expect(spielLadenMock).toHaveBeenCalledWith(3)
    expect(wrapper.find('[data-testid="geber"]').text()).toBe('Anna')
  })

  it('zeigt eine Fehlermeldung, wenn das Laden scheitert', async () => {
    spielLadenMock.mockRejectedValue(new ApiError(404, 'Spiel 3 nicht gefunden.'))
    const wrapper = mount(SpielView, { props: { spielId: '3' } })
    await flushPromises()

    expect(wrapper.find('[data-testid="fehler"]').text()).toBe('Spiel 3 nicht gefunden.')
  })

  it('lädt und zeigt die Punktestände absteigend sortiert', async () => {
    useSpielStore().setzeSpiel(beispielSpiel)
    punktestaendeLadenMock.mockResolvedValue({
      spiel_id: 3,
      punktestaende: { Anna: 120, Bernd: 90, Carla: 150, Dirk: 60 },
      sterne: { Anna: 0, Bernd: 0, Carla: 0, Dirk: 0 },
    })
    const wrapper = mount(SpielView, {
      props: { spielId: '3' },
      global: { stubs: { RouterLink: RouterLinkStub } },
    })
    await flushPromises()

    expect(punktestaendeLadenMock).toHaveBeenCalledWith(3)
    const reihenfolge = wrapper
      .findAll('[data-testid^="punktestand-"]')
      .map((el) => el.attributes('data-testid'))
      .filter((id) => id !== 'punktestand-wert')
    expect(reihenfolge).toEqual([
      'punktestand-Carla',
      'punktestand-Anna',
      'punktestand-Bernd',
      'punktestand-Dirk',
    ])
  })

  it('zeigt Tausender-Sterne neben dem Punktestand des Spielers', async () => {
    useSpielStore().setzeSpiel(beispielSpiel)
    punktestaendeLadenMock.mockResolvedValue({
      spiel_id: 3,
      punktestaende: { Anna: 120, Bernd: 90, Carla: 150, Dirk: 60 },
      sterne: { Anna: 2, Bernd: 0, Carla: 1, Dirk: 0 },
    })
    const wrapper = mount(SpielView, {
      props: { spielId: '3' },
      global: { stubs: { RouterLink: RouterLinkStub } },
    })
    await flushPromises()

    expect(wrapper.find('[data-testid="sterne-Anna"]').text()).toBe('★★')
    expect(wrapper.find('[data-testid="sterne-Carla"]').text()).toBe('★')
    // Spieler ohne Sterne bekommen kein Stern-Element.
    expect(wrapper.find('[data-testid="sterne-Bernd"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="sterne-Dirk"]').exists()).toBe(false)
  })

  it('zeigt nach der letzten Runde den Beendet-Bereich mit Link zur Auswertung', async () => {
    const store = useSpielStore()
    store.setzeSpiel({ id: 3, rundenanzahl: 4, spieler: ['Anna', 'Bernd', 'Carla', 'Dirk'] })
    // Vier gezählte (nicht-Tausender) Runden in der Historie → Spiel beendet (FND-006).
    rundenHistorieLadenMock.mockResolvedValue({
      spiel_id: 3,
      spieler: ['Anna', 'Bernd', 'Carla', 'Dirk'],
      runden: [1, 2, 3, 4].map((n) => macheRunde(n, n)),
    })

    const wrapper = mount(SpielView, {
      props: { spielId: '3' },
      global: { stubs: { RouterLink: RouterLinkStub } },
    })
    await flushPromises()

    expect(wrapper.find('[data-testid="beendet"]').exists()).toBe(true)
    const link = wrapper.findComponent(RouterLinkStub)
    expect(link.props().to).toEqual({ name: 'spielende', params: { spielId: '3' } })
  })

  it('zählt Tausender nicht als Runde: Fortschritt und Geber bleiben stehen (FND-006)', async () => {
    useSpielStore().setzeSpiel(beispielSpiel)
    rundenHistorieLadenMock.mockResolvedValue({
      spiel_id: 3,
      spieler: ['Anna', 'Bernd', 'Carla', 'Dirk'],
      runden: [macheRunde(1, 1), macheRunde(2, null, true)],
    })
    const wrapper = mount(SpielView, {
      props: { spielId: '3' },
      global: { stubs: { RouterLink: RouterLinkStub } },
    })
    await flushPromises()

    // Eine gezählte Runde gespielt, der Tausender zählt nicht → nächste zu spielende
    // ist weiterhin die gezählte Runde 2 mit Geber Bernd (spieler[(2-1)%4]).
    expect(wrapper.find('[data-testid="rundenfortschritt"]').text()).toContain('Runde 2 / 12')
    expect(wrapper.find('[data-testid="geber"]').text()).toBe('Bernd')
    expect(wrapper.find('[data-testid="beendet"]').exists()).toBe(false)
  })

  it('zeigt die Anschreibetabelle, sobald Runden in der Historie vorliegen', async () => {
    useSpielStore().setzeSpiel(beispielSpiel)
    rundenHistorieLadenMock.mockResolvedValue({
      spiel_id: 3,
      spieler: ['Anna', 'Bernd', 'Carla', 'Dirk'],
      runden: [
        {
          rundennummer: 1,
          sequenz: 1,
          zaehlrunde: 1,
          geber: 'Anna',
          spielmacher: 'Bernd',
          reizwert: 150,
          rundenausgang: 'gewonnenes Spiel',
          ist_tausender: false,
          verlustwert: 0,
          spieler: {
            Anna: { rolle: 'geber', meldepunkte: 0, stichwerte: 0, mitpunkte: 0, hat_eigenen_stich: false, stern: false },
            Bernd: { rolle: 'spielmacher', meldepunkte: 100, stichwerte: 120, mitpunkte: 0, hat_eigenen_stich: true, stern: false },
            Carla: { rolle: 'gegenspieler', meldepunkte: 40, stichwerte: 130, mitpunkte: 0, hat_eigenen_stich: true, stern: false },
            Dirk: { rolle: 'gegenspieler', meldepunkte: 0, stichwerte: 0, mitpunkte: 0, hat_eigenen_stich: false, stern: false },
          },
          stand: { Anna: 0, Bernd: 220, Carla: 170, Dirk: 0 },
        },
      ],
    })
    const wrapper = mount(SpielView, {
      props: { spielId: '3' },
      global: { stubs: { RouterLink: RouterLinkStub } },
    })
    await flushPromises()

    expect(rundenHistorieLadenMock).toHaveBeenCalledWith(3)
    expect(wrapper.find('[data-testid="anschreibetabelle"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="stand-1-Bernd"]').text()).toBe('220')
  })

  it('korrigiert die letzte Runde per PUT und lädt Punktestände + Historie neu', async () => {
    useSpielStore().setzeSpiel(beispielSpiel)
    rundenHistorieLadenMock.mockResolvedValue(historieMitRunde)
    letzteRundeAktualisierenMock.mockResolvedValue({
      id: 1,
      rundennummer: 1,
      rundenausgang: 'gewonnenes Spiel',
      spielmacher_punkte: 210,
      verlustwert: 0,
      mitpunkte_pro_gegenspieler: 0,
    })
    const wrapper = mount(SpielView, {
      props: { spielId: '3' },
      global: { stubs: { RouterLink: RouterLinkStub } },
    })
    await flushPromises()

    // Korrektur starten → Formular im Korrektur-Modus mit den Werten der letzten Runde.
    expect(wrapper.find('[data-testid="korrektur-starten"]').exists()).toBe(true)
    await wrapper.find('[data-testid="korrektur-starten"]').trigger('click')
    expect(wrapper.find('[data-testid="korrektur"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="runde-absenden"]').text()).toContain('Korrektur speichern')
    // Vorbelegung: Bernd Spielmacher, Meldepunkte 100 aus der letzten Runde.
    expect((wrapper.find('[data-testid="sm-meldepunkte"]').element as HTMLInputElement).value).toBe(
      '100',
    )

    // Korrigierten Meldewert setzen und speichern.
    await wrapper.find('[data-testid="sm-meldepunkte"]').setValue(110)
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(letzteRundeAktualisierenMock).toHaveBeenCalledTimes(1)
    const [spielId, rundennummer, payload] = letzteRundeAktualisierenMock.mock.calls[0]
    expect(spielId).toBe(3)
    expect(rundennummer).toBe(1)
    expect(payload).toMatchObject({ typ: 'normal', spielmacher: 'Bernd', meldepunkte: 110 })

    // Nach Erfolg: Korrektur-Modus verlassen, Punktestände + Historie neu geladen.
    expect(wrapper.find('[data-testid="korrektur"]').exists()).toBe(false)
    expect(punktestaendeLadenMock).toHaveBeenCalledTimes(2)
    expect(rundenHistorieLadenMock).toHaveBeenCalledTimes(2)
  })

  it('belegt bei Korrektur einer doppelt-abgegangenen Runde den SM-Stichwert vor (Kontrollsumme 250, FND-004)', async () => {
    useSpielStore().setzeSpiel(beispielSpiel)
    const historieDoppelt: Rundenhistorie = {
      spiel_id: 3,
      spieler: ['Anna', 'Bernd', 'Carla', 'Dirk'],
      runden: [
        {
          rundennummer: 1,
          sequenz: 1,
          zaehlrunde: 1,
          geber: 'Anna',
          spielmacher: 'Bernd',
          reizwert: 300,
          rundenausgang: 'doppeltes Abgehen',
          ist_tausender: false,
          verlustwert: -600,
          spieler: {
            Anna: { rolle: 'geber', meldepunkte: 0, stichwerte: 0, mitpunkte: 0, hat_eigenen_stich: false, stern: false },
            Bernd: { rolle: 'spielmacher', meldepunkte: 0, stichwerte: 60, mitpunkte: 0, hat_eigenen_stich: true, stern: false },
            Carla: { rolle: 'gegenspieler', meldepunkte: 0, stichwerte: 130, mitpunkte: 30, hat_eigenen_stich: true, stern: false },
            Dirk: { rolle: 'gegenspieler', meldepunkte: 0, stichwerte: 60, mitpunkte: 30, hat_eigenen_stich: true, stern: false },
          },
          stand: { Anna: 0, Bernd: -600, Carla: 160, Dirk: 90 },
        },
      ],
    }
    rundenHistorieLadenMock.mockResolvedValue(historieDoppelt)
    const wrapper = mount(SpielView, {
      props: { spielId: '3' },
      global: { stubs: { RouterLink: RouterLinkStub } },
    })
    await flushPromises()

    await wrapper.find('[data-testid="korrektur-starten"]').trigger('click')
    // FND-004: SM-Stichwert ist mit dem roh erfassten Wert vorbelegt.
    expect((wrapper.find('[data-testid="sm-stichwerte"]').element as HTMLInputElement).value).toBe(
      '60',
    )
    // „Korrektur speichern" ist nicht gesperrt (Summe 60 + 130 + 60 == 250).
    expect(wrapper.find('[data-testid="runde-absenden"]').attributes('disabled')).toBeUndefined()
  })
})
