<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ApiError, siegerErmitteln, type SiegerErgebnis } from '../api'

const props = defineProps<{ spielId: string }>()

const ergebnis = ref<SiegerErgebnis | null>(null)
const laedt = ref(false)
const fehler = ref<string | null>(null)

/** Endstand absteigend (höchster Punktestand zuerst). */
const sortierteStaende = computed(() => {
  if (!ergebnis.value) return []
  return Object.entries(ergebnis.value.punktestaende)
    .map(([name, punkte]) => ({ name, punkte }))
    .sort((a, b) => b.punkte - a.punkte)
})

const sieger = computed(() => ergebnis.value?.sieger ?? [])
const istGleichstand = computed(() => sieger.value.length > 1)

function istSieger(name: string): boolean {
  return sieger.value.includes(name)
}

onMounted(async () => {
  laedt.value = true
  fehler.value = null
  try {
    ergebnis.value = await siegerErmitteln(Number(props.spielId))
  } catch (error) {
    fehler.value =
      error instanceof ApiError ? error.message : 'Sieger konnte nicht ermittelt werden.'
  } finally {
    laedt.value = false
  }
})
</script>

<template>
  <main class="view view--spielende flex flex-col gap-4">
    <h1 class="text-2xl font-bold text-emerald-700">Spielende</h1>

    <p v-if="laedt" class="text-slate-600">Ermittle Sieger …</p>
    <p v-else-if="fehler" data-testid="fehler" role="alert" class="text-red-700">{{ fehler }}</p>

    <template v-else-if="ergebnis">
      <section
        data-testid="sieger"
        class="rounded border border-emerald-300 bg-emerald-50 p-4 text-emerald-800"
      >
        <p v-if="istGleichstand" class="text-lg font-semibold">
          Gleichstand – mehrere Sieger:
          <span data-testid="sieger-namen">{{ sieger.join(', ') }}</span>
        </p>
        <p v-else class="text-lg font-semibold">
          Sieger: <span data-testid="sieger-namen">{{ sieger[0] }}</span>
        </p>
      </section>

      <section data-testid="endstand" class="flex flex-col gap-2 rounded border border-slate-200 p-3">
        <h2 class="text-lg font-semibold text-slate-700">Endstand</h2>
        <ol class="flex flex-col gap-1">
          <li
            v-for="(eintrag, i) in sortierteStaende"
            :key="eintrag.name"
            :data-testid="`endstand-${eintrag.name}`"
            class="flex items-center justify-between rounded px-2 py-1"
            :class="istSieger(eintrag.name) ? 'bg-emerald-50 font-semibold text-emerald-800' : 'text-slate-700'"
          >
            <span>{{ i + 1 }}. {{ eintrag.name }}</span>
            <span>{{ eintrag.punkte }}</span>
          </li>
        </ol>
      </section>

      <RouterLink
        :to="{ name: 'start' }"
        data-testid="neues-spiel"
        class="self-start rounded bg-emerald-600 px-4 py-2 font-semibold text-white hover:bg-emerald-700"
      >
        Neues Spiel
      </RouterLink>
    </template>
  </main>
</template>
