<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import type { SpielAnlegenRequest } from '../api'
import { MAX_SPIELERZAHL, MIN_SPIELERZAHL } from '../domain/regeln'
import { geberSetztAus } from '../domain/rotation'

/**
 * Präsentationsnahes Formular zum Anlegen eines Spiels (Slice 1) für 3 oder 4 Spieler.
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

/** Pflichtfelder: die ersten drei Namen. Das vierte Feld ist optional (ADR-017). */
const ERFORDERLICHE_NAMEN = MIN_SPIELERZAHL

/** Vier Eingabefelder; ein leeres viertes Feld bedeutet „zu dritt". */
const spieler = reactive<string[]>(Array.from({ length: MAX_SPIELERZAHL }, () => ''))
const rundenanzahl = ref<number>(12)
const beruehrt = ref(false)

const namenGetrimmt = computed(() => spieler.map((name) => name.trim()))

/**
 * Spielerzahl = Variante: 4 Namen → der Geber setzt aus, 3 Namen → der Geber spielt mit.
 * Die Variante wird nicht gesondert gewählt, sie folgt aus den Namen.
 */
const spielerzahl = computed(() =>
  namenGetrimmt.value[MAX_SPIELERZAHL - 1].length > 0 ? MAX_SPIELERZAHL : MIN_SPIELERZAHL,
)

/** Die tatsächlich teilnehmenden Namen (3 oder 4) in Sitzreihenfolge. */
const teilnehmer = computed(() => namenGetrimmt.value.slice(0, spielerzahl.value))

const erforderlicheNamenGefuellt = computed(() =>
  namenGetrimmt.value.slice(0, ERFORDERLICHE_NAMEN).every((name) => name.length > 0),
)

const namenEindeutig = computed(() => new Set(teilnehmer.value).size === teilnehmer.value.length)

const rundenanzahlGueltig = computed(
  () =>
    Number.isInteger(rundenanzahl.value) &&
    rundenanzahl.value > 0 &&
    rundenanzahl.value % spielerzahl.value === 0,
)

/** Erste zutreffende Validierungsmeldung – oder null, wenn alles passt. */
const validierungsfehler = computed<string | null>(() => {
  if (!erforderlicheNamenGefuellt.value) {
    return 'Bitte mindestens drei Spielernamen ausfüllen (das vierte Feld ist optional).'
  }
  if (!namenEindeutig.value) return 'Die Spielernamen müssen eindeutig sein.'
  if (!rundenanzahlGueltig.value) {
    return `Die Rundenanzahl muss ein positives Vielfaches von ${spielerzahl.value} sein.`
  }
  return null
})

const istGueltig = computed(() => validierungsfehler.value === null)

function absenden(): void {
  beruehrt.value = true
  if (!istGueltig.value || props.laedt) return
  emit('absenden', {
    spieler: [...teilnehmer.value],
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
        <span class="text-sm text-slate-600">
          Spieler {{ i + 1 }}<template v-if="i >= ERFORDERLICHE_NAMEN"> (optional)</template>
        </span>
        <input
          v-model="spieler[i]"
          type="text"
          :required="i < ERFORDERLICHE_NAMEN"
          :data-testid="`spieler-${i}`"
          :placeholder="
            i < ERFORDERLICHE_NAMEN ? `Name Spieler ${i + 1}` : 'Leer lassen für ein Spiel zu dritt'
          "
          autocomplete="off"
          class="rounded border border-slate-300 px-3 py-2"
        />
      </label>

      <p data-testid="variante-hinweis" class="text-sm text-slate-500">
        {{ spielerzahl }} Spieler –
        {{ geberSetztAus(teilnehmer) ? 'der Geber setzt aus.' : 'der Geber spielt mit.' }}
      </p>

      <label class="flex flex-col gap-1">
        <span class="text-sm text-slate-600">Rundenanzahl (Vielfaches von {{ spielerzahl }})</span>
        <input
          v-model.number="rundenanzahl"
          type="number"
          :min="spielerzahl"
          :step="spielerzahl"
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
