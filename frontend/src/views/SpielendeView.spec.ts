import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter, type Router } from 'vue-router'
import SpielendeView from './SpielendeView.vue'
import { useSpielStore } from '../stores/spiel'

vi.mock('../api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api')>()
  return {
    ...actual,
    siegerErmitteln: vi.fn(),
    rundenHistorieLaden: vi.fn(),
    spielLaden: vi.fn(),
    spielAnlegen: vi.fn(),
  }
})
import {
  ApiError,
  rundenHistorieLaden,
  siegerErmitteln,
  spielAnlegen,
  spielLaden,
  type Rundenhistorie,
} from '../api'

const siegerErmittelnMock = vi.mocked(siegerErmitteln)
const rundenHistorieLadenMock = vi.mocked(rundenHistorieLaden)
const spielLadenMock = vi.mocked(spielLaden)
const spielAnlegenMock = vi.mocked(spielAnlegen)

const spielDaten = { id: 3, rundenanzahl: 12, spieler: ['Anna', 'Bernd', 'Carla', 'Dirk'] }

const endergebnis = {
  spiel_id: 3,
  punktestaende: { Anna: 0, Bernd: 250, Carla: 90, Dirk: 60 },
  sterne: { Anna: 0, Bernd: 0, Carla: 0, Dirk: 0 },
  sieger: ['Bernd'],
}

/** Normalisiert das geschützte Leerzeichen, das Intl vor dem Euro-Zeichen setzt. */
const normal = (text: string) => text.replace(/ /g, ' ')

function baueRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'start', component: { template: '<div />' } },
      { path: '/spiel/:spielId', name: 'spiel', component: { template: '<div />' } },
      { path: '/spiel/:spielId/ende', name: 'spielende', component: SpielendeView },
    ],
  })
}

async function mountView(router: Router = baueRouter()) {
  await router.push('/spiel/3/ende')
  await router.isReady()
  return mount(SpielendeView, { props: { spielId: '3' }, global: { plugins: [router] } })
}

describe('SpielendeView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    siegerErmittelnMock.mockReset()
    rundenHistorieLadenMock.mockReset()
    spielLadenMock.mockReset()
    spielAnlegenMock.mockReset()
    rundenHistorieLadenMock.mockResolvedValue({
      spiel_id: 3,
      spieler: ['Anna', 'Bernd', 'Carla', 'Dirk'],
      runden: [],
    })
    spielLadenMock.mockResolvedValue(spielDaten)
  })

  it('zeigt den alleinigen Sieger', async () => {
    siegerErmittelnMock.mockResolvedValue({ ...endergebnis, sieger: ['Bernd'] })
    const wrapper = await mountView()
    await flushPromises()

    expect(siegerErmittelnMock).toHaveBeenCalledWith(3, undefined)
    expect(wrapper.find('[data-testid="sieger-namen"]').text()).toBe('Bernd')
  })

  it('zeigt keine separate Endstand-Liste: die Anschreibetabelle enthält alles', async () => {
    siegerErmittelnMock.mockResolvedValue(endergebnis)
    const wrapper = await mountView()
    await flushPromises()

    expect(wrapper.find('[data-testid="endstand"]').exists()).toBe(false)
    expect(wrapper.text()).not.toContain('Endstand')
  })

  it('weist bei Gleichstand mehrere Sieger aus', async () => {
    siegerErmittelnMock.mockResolvedValue({
      spiel_id: 3,
      punktestaende: { Anna: 600, Bernd: 600, Carla: 500, Dirk: 480 },
      sterne: { Anna: 0, Bernd: 0, Carla: 0, Dirk: 0 },
      sieger: ['Anna', 'Bernd'],
    })
    const wrapper = await mountView()
    await flushPromises()

    expect(wrapper.find('[data-testid="sieger"]').text()).toContain('Gleichstand')
    expect(wrapper.find('[data-testid="sieger-namen"]').text()).toBe('Anna, Bernd')
  })

  it('zeigt eine Fehlermeldung, wenn die Ermittlung scheitert', async () => {
    siegerErmittelnMock.mockRejectedValue(new ApiError(404, 'Spiel 3 nicht gefunden.'))
    const wrapper = await mountView()
    await flushPromises()

    expect(wrapper.find('[data-testid="fehler"]').text()).toBe('Spiel 3 nicht gefunden.')
  })

  it('reicht die exakten 1er-Stichwerte der letzten Runde aus dem Store an siegerErmitteln (§9.4)', async () => {
    // Letzte Runde hat einen Zehner-Gleichstand erzeugt; der Tiebreak entscheidet.
    const store = useSpielStore()
    store.setzeEndrundenStichwerte({ Bernd: 78, Carla: 72 })

    siegerErmittelnMock.mockResolvedValue({
      spiel_id: 3,
      punktestaende: { Anna: -400, Bernd: 130, Carla: 130, Dirk: 0 },
      sterne: { Anna: 0, Bernd: 0, Carla: 0, Dirk: 0 },
      sieger: ['Bernd'],
    })
    await mountView()
    await flushPromises()

    expect(siegerErmittelnMock).toHaveBeenCalledWith(3, 'Bernd:78,Carla:72')
  })

  describe('Anschreibetabelle in der Endabrechnung', () => {
    const historieMitRunde: Rundenhistorie = {
      spiel_id: 3,
      spieler: ['Anna', 'Bernd', 'Carla', 'Dirk'],
      runden: [
        {
          rundennummer: 1, sequenz: 1, zaehlrunde: 1, geber: 'Anna', spielmacher: 'Bernd',
          reizwert: 150, rundenausgang: 'gewonnenes Spiel', ist_tausender: false, verlustwert: 0,
          spieler: {
            Anna: { rolle: 'geber', ist_geber: true, meldepunkte: 0, stichwerte: 0, mitpunkte: 0, hat_eigenen_stich: false, stern: false },
            Bernd: { rolle: 'spielmacher', ist_geber: false, meldepunkte: 150, stichwerte: 100, mitpunkte: 0, hat_eigenen_stich: true, stern: false },
            Carla: { rolle: 'gegenspieler', ist_geber: false, meldepunkte: 0, stichwerte: 90, mitpunkte: 0, hat_eigenen_stich: true, stern: false },
            Dirk: { rolle: 'gegenspieler', ist_geber: false, meldepunkte: 0, stichwerte: 60, mitpunkte: 0, hat_eigenen_stich: true, stern: false },
          },
          stand: { Anna: 0, Bernd: 250, Carla: 90, Dirk: 60 },
        },
      ],
      zu_zahlen_cent: { Anna: 125, Bernd: 0, Carla: 80, Dirk: 95 },
    }

    it('zeigt die vollständige Anschreibetabelle mit allen Details', async () => {
      siegerErmittelnMock.mockResolvedValue(endergebnis)
      rundenHistorieLadenMock.mockResolvedValue(historieMitRunde)
      const wrapper = await mountView()
      await flushPromises()

      expect(rundenHistorieLadenMock).toHaveBeenCalledWith(3)
      expect(wrapper.find('[data-testid="anschreibetabelle"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="stand-1-Bernd"]').text()).toBe('250')
    })

    it('enthält die Abrechnung: wer wie viel zahlen muss', async () => {
      siegerErmittelnMock.mockResolvedValue(endergebnis)
      rundenHistorieLadenMock.mockResolvedValue(historieMitRunde)
      const wrapper = await mountView()
      await flushPromises()

      expect(normal(wrapper.find('[data-testid="zu-zahlen-Carla"]').text())).toBe('0,80 €')
      expect(wrapper.find('[data-testid="zu-zahlen-Bernd"]').text()).toBe('')
    })

    it('beschriftet die Abrechnungszeile zum Spielende mit „Wer zahlt was in die Kasse"', async () => {
      siegerErmittelnMock.mockResolvedValue(endergebnis)
      rundenHistorieLadenMock.mockResolvedValue(historieMitRunde)
      const wrapper = await mountView()
      await flushPromises()

      const zeile = wrapper.find('[data-testid="zu-zahlen"]').text()
      expect(zeile).toContain('Wer zahlt was in die Kasse')
      expect(zeile).not.toContain('jetzt endet')
    })

    it('zeigt die Sternesumme, wenn ein Tausender gespielt wurde', async () => {
      siegerErmittelnMock.mockResolvedValue(endergebnis)
      const tausender = {
        ...historieMitRunde.runden[0],
        rundennummer: 2, sequenz: 2, zaehlrunde: null, ist_tausender: true,
        rundenausgang: 'Tausender gewonnen' as const,
      }
      rundenHistorieLadenMock.mockResolvedValue({
        ...historieMitRunde,
        runden: [historieMitRunde.runden[0], tausender],
        sterne: { Anna: 0, Bernd: 2, Carla: 0, Dirk: 0 },
      })
      const wrapper = await mountView()
      await flushPromises()

      expect(wrapper.find('[data-testid="sterne-summe"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="sterne-summe-Bernd"]').text()).toBe('★★')
    })

    it('blendet die Sternesumme aus, wenn kein Tausender gespielt wurde', async () => {
      siegerErmittelnMock.mockResolvedValue(endergebnis)
      rundenHistorieLadenMock.mockResolvedValue({
        ...historieMitRunde,
        sterne: { Anna: 0, Bernd: 0, Carla: 0, Dirk: 0 },
      })
      const wrapper = await mountView()
      await flushPromises()

      expect(wrapper.find('[data-testid="sterne-summe"]').exists()).toBe(false)
    })

    it('zeigt Sieger auch dann, wenn die Historie nicht geladen werden kann', async () => {
      siegerErmittelnMock.mockResolvedValue(endergebnis)
      rundenHistorieLadenMock.mockRejectedValue(new ApiError(500, 'Fehler'))
      const wrapper = await mountView()
      await flushPromises()

      expect(wrapper.find('[data-testid="sieger-namen"]').text()).toBe('Bernd')
      expect(wrapper.find('[data-testid="anschreibetabelle"]').exists()).toBe(false)
      expect(wrapper.find('[data-testid="fehler"]').exists()).toBe(false)
    })
  })

  describe('Neues Spiel', () => {
    const gleicheTeilnehmer = '[data-testid="neues-spiel-gleiche-teilnehmer"]'

    beforeEach(() => {
      siegerErmittelnMock.mockResolvedValue(endergebnis)
    })

    it('bietet weiterhin „Neues Spiel" und zusätzlich „Neues Spiel mit gleichen Teilnehmern" an', async () => {
      const wrapper = await mountView()
      await flushPromises()

      expect(wrapper.find('[data-testid="neues-spiel"]').text()).toBe('Neues Spiel')
      expect(wrapper.find(gleicheTeilnehmer).text()).toBe('Neues Spiel mit gleichen Teilnehmern')
    })

    it('legt ein Spiel mit denselben Teilnehmern und Rundenzahl an und öffnet es', async () => {
      useSpielStore().setzeSpiel(spielDaten)
      spielAnlegenMock.mockResolvedValue({ id: 9, rundenanzahl: 12, spieler: spielDaten.spieler })
      const router = baueRouter()
      const wrapper = await mountView(router)
      await flushPromises()

      await wrapper.find(gleicheTeilnehmer).trigger('click')
      await flushPromises()

      expect(spielAnlegenMock).toHaveBeenCalledWith({
        spieler: ['Anna', 'Bernd', 'Carla', 'Dirk'],
        rundenanzahl: 12,
      })
      expect(useSpielStore().aktuellesSpiel?.id).toBe(9)
      expect(router.currentRoute.value.name).toBe('spiel')
      expect(router.currentRoute.value.params.spielId).toBe('9')
    })

    it('behält die Spielerzahl: ein Spiel zu dritt bleibt zu dritt', async () => {
      const zuDritt = { id: 3, rundenanzahl: 9, spieler: ['Anna', 'Bernd', 'Carla'] }
      useSpielStore().setzeSpiel(zuDritt)
      spielAnlegenMock.mockResolvedValue({ ...zuDritt, id: 10 })
      const wrapper = await mountView()
      await flushPromises()

      await wrapper.find(gleicheTeilnehmer).trigger('click')
      await flushPromises()

      expect(spielAnlegenMock).toHaveBeenCalledWith({
        spieler: ['Anna', 'Bernd', 'Carla'],
        rundenanzahl: 9,
      })
    })

    it('lädt das Spiel nach, wenn die Seite direkt geöffnet wurde (Store leer)', async () => {
      spielAnlegenMock.mockResolvedValue({ id: 11, rundenanzahl: 12, spieler: spielDaten.spieler })
      const wrapper = await mountView()
      await flushPromises()

      expect(spielLadenMock).toHaveBeenCalledWith(3)
      await wrapper.find(gleicheTeilnehmer).trigger('click')
      await flushPromises()
      expect(spielAnlegenMock).toHaveBeenCalledWith({
        spieler: spielDaten.spieler,
        rundenanzahl: 12,
      })
    })

    it('lädt das Spiel nicht nach, wenn es schon im Store liegt', async () => {
      useSpielStore().setzeSpiel(spielDaten)
      await mountView()
      await flushPromises()

      expect(spielLadenMock).not.toHaveBeenCalled()
    })

    it('ist gesperrt, solange die Teilnehmer unbekannt sind', async () => {
      spielLadenMock.mockRejectedValue(new ApiError(404, 'Spiel 3 nicht gefunden.'))
      const wrapper = await mountView()
      await flushPromises()

      expect(wrapper.find(gleicheTeilnehmer).attributes('disabled')).toBeDefined()
    })

    it('zeigt eine Fehlermeldung und bleibt auf der Seite, wenn das Anlegen scheitert', async () => {
      useSpielStore().setzeSpiel(spielDaten)
      spielAnlegenMock.mockRejectedValue(new ApiError(400, 'Ungültige Spielerzahl.'))
      const router = baueRouter()
      const wrapper = await mountView(router)
      await flushPromises()

      await wrapper.find(gleicheTeilnehmer).trigger('click')
      await flushPromises()

      expect(wrapper.find('[data-testid="neues-spiel-fehler"]').text()).toBe('Ungültige Spielerzahl.')
      expect(router.currentRoute.value.name).toBe('spielende')
    })
  })
})
