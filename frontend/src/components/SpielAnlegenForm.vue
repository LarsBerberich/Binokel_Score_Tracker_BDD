<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import type { SpielAnlegenRequest } from '../api'

/**
 * Präsentationsnahes Formular zum Anlegen eines Spiels (Slice 1).
 *
 * Kennt keine API: es validiert die Eingaben und meldet ein gültiges
 * Ergebnis per `absenden`-Event nach oben. Der API-Aufruf, Fehlerbehandlung
 * und Navigation liegen in der View (StartView).
 */
const props = withDefaults(
  defineProps<{
    /** true, solange das Anlegen läuft – sperrt das Formular. */
    laedt?: boolean
    /** Fehlermeldung vom Server (z. B. Validierung im Backend). */
    fehler?: string | null
  }>(),
  { laedt: false, fehler: null },
)

const emit = defineEmits<{ absenden: [payload: SpielAnlegenRequest] }>()

/** Genau vier Spielernamen (Binokel zu viert). */
const spieler = reactive<string[]>(['', '', '', ''])
const rundenanzahl = ref<number>(12)
const beruehrt = ref(false)

const namenGetrimmt = computed(() => spieler.map((name) => name.trim()))

const alleNamenGefuellt = computed(() =>
  namenGetrimmt.value.every((name) => name.length > 0),
)

const namenEindeutig = computed(() => {
  const gefuellt = namenGetrimmt.value.filter((name) => name.length > 0)
  return new Set(gefuellt).size === gefuellt.length
})

const rundenanzahlGueltig = computed(
  () => Number.isInteger(rundenanzahl.value) && rundenanzahl.value > 0 && rundenanzahl.value % 4 === 0,
)

/** Erste zutreffende Validierungsmeldung – oder null, wenn alles passt. */
const validierungsfehler = computed<string | null>(() => {
  if (!alleNamenGefuellt.value) return 'Bitte alle vier Spielernamen ausfüllen.'
  if (!namenEindeutig.value) return 'Die Spielernamen müssen eindeutig sein.'
  if (!rundenanzahlGueltig.value) return 'Die Rundenanzahl muss ein positives Vielfaches von 4 sein.'
  return null
})

const istGueltig = computed(() => validierungsfehler.value === null)

function absenden(): void {
  beruehrt.value = true
  if (!istGueltig.value || props.laedt) return
  emit('absenden', {
    spieler: [...namenGetrimmt.value],
    rundenanzahl: rundenanzahl.value,
  })
}
</script>

<template>
  <form
    class="flex flex-col gap-4"
    novalidate
    @submit.prevent="absenden"
    @input="beruehrt = true"
  >
    <fieldset class="flex flex-col gap-3 border-0 p-0" :disabled="laedt">
      <legend class="mb-1 text-lg font-semibold">Neues Spiel</legend>

      <label v-for="(_, i) in spieler" :key="i" class="flex flex-col gap-1">
        <span class="text-sm text-slate-600">Spieler {{ i + 1 }}</span>
        <input
          v-model="spieler[i]"
          type="text"
          :data-testid="`spieler-${i}`"
          :placeholder="`Name Spieler ${i + 1}`"
          autocomplete="off"
          class="rounded border border-slate-300 px-3 py-2"
        />
      </label>

      <label class="flex flex-col gap-1">
        <span class="text-sm text-slate-600">Rundenanzahl (Vielfaches von 4)</span>
        <input
          v-model.number="rundenanzahl"
          type="number"
          min="4"
          step="4"
          data-testid="rundenanzahl"
          class="rounded border border-slate-300 px-3 py-2"
        />
      </label>
    </fieldset>

    <p
      v-if="beruehrt && validierungsfehler"
      data-testid="validierungsfehler"
      class="text-sm text-amber-700"
    >
      {{ validierungsfehler }}
    </p>
    <p
      v-if="fehler"
      data-testid="server-fehler"
      role="alert"
      class="text-sm text-red-700"
    >
      {{ fehler }}
    </p>

    <button
      type="submit"
      data-testid="absenden"
      :disabled="!istGueltig || laedt"
      class="rounded bg-emerald-600 px-4 py-2 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
    >
      {{ laedt ? 'Wird angelegt …' : 'Spiel starten' }}
    </button>
  </form>
</template>
