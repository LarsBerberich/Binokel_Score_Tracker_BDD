import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount, RouterLinkStub } from '@vue/test-utils'
import SpielendeView from './SpielendeView.vue'

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
    siegerErmittelnMock.mockReset()
  })

  it('zeigt den alleinigen Sieger und den absteigend sortierten Endstand', async () => {
    siegerErmittelnMock.mockResolvedValue({
      spiel_id: 3,
      punktestaende: { Anna: 580, Bernd: 620, Carla: 610, Dirk: 540 },
      sieger: ['Bernd'],
    })
    const wrapper = mountView()
    await flushPromises()

    expect(siegerErmittelnMock).toHaveBeenCalledWith(3)
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
})
