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
  }
})
import { ApiError, punktestaendeLaden, rundenHistorieLaden, spielLaden } from '../api'

const spielLadenMock = vi.mocked(spielLaden)
const punktestaendeLadenMock = vi.mocked(punktestaendeLaden)
const rundenHistorieLadenMock = vi.mocked(rundenHistorieLaden)
const beispielSpiel = { id: 3, rundenanzahl: 12, spieler: ['Anna', 'Bernd', 'Carla', 'Dirk'] }

const leereHistorie = { spiel_id: 3, spieler: ['Anna', 'Bernd', 'Carla', 'Dirk'], runden: [] }

describe('SpielView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    spielLadenMock.mockReset()
    punktestaendeLadenMock.mockReset()
    rundenHistorieLadenMock.mockReset()
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

  it('zeigt nach der letzten Runde den Beendet-Bereich mit Link zur Auswertung', () => {
    const store = useSpielStore()
    store.setzeSpiel({ id: 3, rundenanzahl: 4, spieler: ['Anna', 'Bernd', 'Carla', 'Dirk'] })
    // Vier Runden weiterschalten → Rundennummer 5 > 4 → Spiel beendet
    for (let i = 0; i < 4; i++) store.naechsteRunde()

    const wrapper = mount(SpielView, {
      props: { spielId: '3' },
      global: { stubs: { RouterLink: RouterLinkStub } },
    })

    expect(wrapper.find('[data-testid="beendet"]').exists()).toBe(true)
    const link = wrapper.findComponent(RouterLinkStub)
    expect(link.props().to).toEqual({ name: 'spielende', params: { spielId: '3' } })
  })

  it('zeigt die Anschreibetabelle, sobald Runden in der Historie vorliegen', async () => {
    useSpielStore().setzeSpiel(beispielSpiel)
    rundenHistorieLadenMock.mockResolvedValue({
      spiel_id: 3,
      spieler: ['Anna', 'Bernd', 'Carla', 'Dirk'],
      runden: [
        {
          rundennummer: 1,
          geber: 'Anna',
          spielmacher: 'Bernd',
          reizwert: 150,
          rundenausgang: 'gewonnenes_spiel',
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
})
