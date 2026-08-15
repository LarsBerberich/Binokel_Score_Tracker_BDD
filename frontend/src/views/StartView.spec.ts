import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter, type Router } from 'vue-router'
import StartView from './StartView.vue'
import { ApiError } from '../api'
import { useSpielStore } from '../stores/spiel'

// API-Client mocken – wir testen die View-Orchestrierung, nicht das Netzwerk.
vi.mock('../api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api')>()
  return { ...actual, spielAnlegen: vi.fn() }
})
import { spielAnlegen } from '../api'

const spielAnlegenMock = vi.mocked(spielAnlegen)

function baueRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'start', component: StartView },
      { path: '/spiel/:spielId', name: 'spiel', component: { template: '<div />' } },
    ],
  })
}

async function mountView(router: Router) {
  await router.push('/')
  await router.isReady()
  return mount(StartView, { global: { plugins: [router] } })
}

async function fuelleGueltigesFormular(wrapper: Awaited<ReturnType<typeof mountView>>) {
  const namen = ['Anna', 'Bert', 'Cara', 'Dirk']
  for (let i = 0; i < 4; i++) {
    await wrapper.find(`[data-testid="spieler-${i}"]`).setValue(namen[i])
  }
  await wrapper.find('[data-testid="rundenanzahl"]').setValue(8)
}

describe('StartView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    spielAnlegenMock.mockReset()
  })

  it('rendert die App-Überschrift (Smoke)', async () => {
    const wrapper = await mountView(baueRouter())
    expect(wrapper.find('h1').text()).toBe('Binokel Score Tracker')
  })

  it('legt ein Spiel an, merkt es im Store und navigiert zur Spiel-Route', async () => {
    spielAnlegenMock.mockResolvedValue({ id: 7, rundenanzahl: 8, spieler: ['Anna', 'Bert', 'Cara', 'Dirk'] })
    const router = baueRouter()
    const wrapper = await mountView(router)

    await fuelleGueltigesFormular(wrapper)
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(spielAnlegenMock).toHaveBeenCalledWith({
      spieler: ['Anna', 'Bert', 'Cara', 'Dirk'],
      rundenanzahl: 8,
    })
    expect(useSpielStore().aktuellesSpiel?.id).toBe(7)
    expect(router.currentRoute.value.name).toBe('spiel')
    expect(router.currentRoute.value.params.spielId).toBe('7')
  })

  it('zeigt die Server-Fehlermeldung an und navigiert nicht', async () => {
    spielAnlegenMock.mockRejectedValue(new ApiError(400, 'Genau 4 Spieler erforderlich.'))
    const router = baueRouter()
    const wrapper = await mountView(router)

    await fuelleGueltigesFormular(wrapper)
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.find('[data-testid="server-fehler"]').text()).toBe(
      'Genau 4 Spieler erforderlich.',
    )
    expect(router.currentRoute.value.name).toBe('start')
  })
})
