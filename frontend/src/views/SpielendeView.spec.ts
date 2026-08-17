import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount, RouterLinkStub } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import SpielendeView from './SpielendeView.vue'
import { useSpielStore } from '../stores/spiel'

vi.mock('../api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api')>()
  return { ...actual, siegerErmitteln: vi.fn() }
})
import { ApiError, siegerErmitteln } from '../api'

const siegerErmittelnMock = vi.mocked(siegerErmitteln)

function mountView() {
  return mount(SpielendeView, {
    props: { spielId: '3' },
    global: { stubs: { RouterLink: RouterLinkStub } },
  })
}

describe('SpielendeView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    siegerErmittelnMock.mockReset()
  })

  it('zeigt den alleinigen Sieger und den absteigend sortierten Endstand', async () => {
    siegerErmittelnMock.mockResolvedValue({
      spiel_id: 3,
      punktestaende: { Anna: 580, Bernd: 620, Carla: 610, Dirk: 540 },
      sterne: { Anna: 0, Bernd: 0, Carla: 0, Dirk: 0 },
      sieger: ['Bernd'],
    })
    const wrapper = mountView()
    await flushPromises()

    expect(siegerErmittelnMock).toHaveBeenCalledWith(3, undefined)
    expect(wrapper.find('[data-testid="sieger-namen"]').text()).toBe('Bernd')

    const reihenfolge = wrapper
      .findAll('[data-testid^="endstand-"]')
      .map((el) => el.attributes('data-testid'))
      .filter((id): id is string => id !== 'endstand')
    expect(reihenfolge).toEqual([
      'endstand-Bernd',
      'endstand-Carla',
      'endstand-Anna',
      'endstand-Dirk',
    ])
  })

  it('weist bei Gleichstand mehrere Sieger aus', async () => {
    siegerErmittelnMock.mockResolvedValue({
      spiel_id: 3,
      punktestaende: { Anna: 600, Bernd: 600, Carla: 500, Dirk: 480 },
      sterne: { Anna: 0, Bernd: 0, Carla: 0, Dirk: 0 },
      sieger: ['Anna', 'Bernd'],
    })
    const wrapper = mountView()
    await flushPromises()

    expect(wrapper.find('[data-testid="sieger"]').text()).toContain('Gleichstand')
    expect(wrapper.find('[data-testid="sieger-namen"]').text()).toBe('Anna, Bernd')
  })

  it('zeigt eine Fehlermeldung, wenn die Ermittlung scheitert', async () => {
    siegerErmittelnMock.mockRejectedValue(new ApiError(404, 'Spiel 3 nicht gefunden.'))
    const wrapper = mountView()
    await flushPromises()

    expect(wrapper.find('[data-testid="fehler"]').text()).toBe('Spiel 3 nicht gefunden.')
  })

  it('zeigt Tausender-Sterne im Endstand', async () => {
    siegerErmittelnMock.mockResolvedValue({
      spiel_id: 3,
      punktestaende: { Anna: 580, Bernd: 620, Carla: 610, Dirk: 540 },
      sterne: { Anna: 1, Bernd: 0, Carla: 3, Dirk: 0 },
      sieger: ['Bernd'],
    })
    const wrapper = mountView()
    await flushPromises()

    expect(wrapper.find('[data-testid="sterne-Carla"]').text()).toBe('★★★')
    expect(wrapper.find('[data-testid="sterne-Anna"]').text()).toBe('★')
    expect(wrapper.find('[data-testid="sterne-Bernd"]').exists()).toBe(false)
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
    mountView()
    await flushPromises()

    expect(siegerErmittelnMock).toHaveBeenCalledWith(3, 'Bernd:78,Carla:72')
  })
})
