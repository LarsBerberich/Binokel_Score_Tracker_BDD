<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  ApiError,
  punktestaendeLaden,
  rundeAuswerten,
  spielLaden,
  type PunktestandMap,
  type RundeErgebnis,
  type RundeRequest,
  type Spiel,
} from '../api'
import { useSpielStore } from '../stores/spiel'
import { aktiveSpieler, geberFuerRunde } from '../domain/rotation'
import RundeForm from '../components/RundeForm.vue'

const props = defineProps<{ spielId: string }>()
const spielStore = useSpielStore()

const spiel = ref<Spiel | null>(spielStore.aktuellesSpiel)
const laedt = ref(false)
const fehler = ref<string | null>(null)

const rundeLaedt = ref(false)
const rundeFehler = ref<string | null>(null)
const letztesErgebnis = ref<RundeErgebnis | null>(null)
const punktestaende = ref<PunktestandMap | null>(null)

const rundennummer = computed(() => spielStore.aktuelleRundennummer)
const geber = computed(() =>
  spiel.value ? geberFuerRunde(spiel.value.spieler, rundennummer.value) : '',
)
const aktive = computed(() =>
  spiel.value ? aktiveSpieler(spiel.value.spieler, geber.value) : [],
)
const istBeendet = computed(() =>
  spiel.value ? rundennummer.value > spiel.value.rundenanzahl : false,
)

/** Punktestände absteigend (höchster zuerst – führt zur Siegerermittlung). */
const sortierteStaende = computed(() => {
  if (!punktestaende.value) return []
  return Object.entries(punktestaende.value)
    .map(([name, punkte]) => ({ name, punkte }))
    .sort((a, b) => b.punkte - a.punkte)
})

async function punktestaendeAktualisieren(): Promise<void> {
  if (!spiel.value) return
  try {
    const antwort = await punktestaendeLaden(spiel.value.id)
    punktestaende.value = antwort.punktestaende
  } catch {
    // Punktestände sind ergänzende Info – ein Ladefehler blockiert die Runde nicht.
    punktestaende.value = null
  }
}

async function rundeAbsenden(payload: RundeRequest): Promise<void> {
  if (!spiel.value) return
  rundeLaedt.value = true
  rundeFehler.value = null
  try {
    letztesErgebnis.value = await rundeAuswerten(spiel.value.id, payload)
    spielStore.naechsteRunde()
    await punktestaendeAktualisieren()
  } catch (error) {
    rundeFehler.value =
      error instanceof ApiError ? error.message : 'Runde konnte nicht ausgewertet werden.'
  } finally {
    rundeLaedt.value = false
  }
}

onMounted(async () => {
  const id = Number(props.spielId)
  // Aus StartView kommend liegt das Spiel bereits im Store – dann kein Reload.
  if (!spiel.value || spiel.value.id !== id) {
    laedt.value = true
    fehler.value = null
    try {
      const geladen = await spielLaden(id)
      spielStore.setzeSpiel(geladen)
      spiel.value = geladen
    } catch (error) {
      fehler.value =
        error instanceof ApiError ? error.message : 'Spiel konnte nicht geladen werden.'
      return
    } finally {
      laedt.value = false
    }
  }
  await punktestaendeAktualisieren()
})
</script>

<template>
  <main class="view view--spiel flex flex-col gap-4">
    <p v-if="laedt" class="text-slate-600">Lädt …</p>
    <p v-else-if="fehler" data-testid="fehler" role="alert" class="text-red-700">{{ fehler }}</p>

    <template v-else-if="spiel">
      <header class="flex items-baseline justify-between gap-2">
        <h1 class="text-2xl font-bold text-emerald-700">Spiel</h1>
        <span data-testid="rundenfortschritt" class="text-slate-600">
          Runde {{ rundennummer }} / {{ spiel.rundenanzahl }}
        </span>
      </header>

      <section
        v-if="sortierteStaende.length"
        data-testid="punktestaende"
        class="flex flex-col gap-2 rounded border border-slate-200 p-3"
      >
        <h2 class="text-lg font-semibold text-slate-700">Punktestand</h2>
        <ol class="flex flex-col gap-1">
          <li
            v-for="(eintrag, i) in sortierteStaende"
            :key="eintrag.name"
            :data-testid="`punktestand-${eintrag.name}`"
            class="flex items-center justify-between rounded px-2 py-1"
            :class="i === 0 ? 'bg-emerald-50 font-semibold text-emerald-800' : 'text-slate-700'"
          >
            <span>{{ i + 1 }}. {{ eintrag.name }}</span>
            <span data-testid="punktestand-wert">{{ eintrag.punkte }}</span>
          </li>
        </ol>
      </section>

      <section v-if="!istBeendet" class="flex flex-col gap-3">
        <p class="text-slate-600">
          Geber (setzt aus): <strong data-testid="geber">{{ geber }}</strong>
        </p>
        <ul class="flex flex-col gap-1">
          <li
            v-for="name in spiel.spieler"
            :key="name"
            class="flex items-center justify-between rounded border border-slate-200 px-3 py-2"
            :class="name === geber ? 'bg-slate-100 text-slate-500' : 'bg-white'"
          >
            <span>{{ name }}</span>
            <span v-if="name === geber" class="text-sm">Geber – setzt aus</span>
            <span v-else class="text-sm text-emerald-700">aktiv</span>
          </li>
        </ul>

        <p
          v-if="letztesErgebnis"
          data-testid="letztes-ergebnis"
          class="rounded bg-emerald-50 px-3 py-2 text-sm text-emerald-800"
        >
          Zuletzt gewertet: {{ letztesErgebnis.rundenausgang }}
          (Spielmacher-Punkte: {{ letztesErgebnis.spielmacher_punkte }},
          Verlustwert: {{ letztesErgebnis.verlustwert }})
        </p>

        <RundeForm
          :rundennummer="rundennummer"
          :geber="geber"
          :aktive="aktive"
          :laedt="rundeLaedt"
          :fehler="rundeFehler"
          @absenden="rundeAbsenden"
        />
      </section>

      <section v-else data-testid="beendet" class="flex flex-col gap-3">
        <p class="text-slate-700">Alle {{ spiel.rundenanzahl }} Runden gespielt.</p>

        <p
          v-if="letztesErgebnis"
          data-testid="letztes-ergebnis"
          class="rounded bg-emerald-50 px-3 py-2 text-sm text-emerald-800"
        >
          Zuletzt gewertet: {{ letztesErgebnis.rundenausgang }}
          (Spielmacher-Punkte: {{ letztesErgebnis.spielmacher_punkte }},
          Verlustwert: {{ letztesErgebnis.verlustwert }})
        </p>

        <RouterLink
          :to="{ name: 'spielende', params: { spielId: String(spiel.id) } }"
          data-testid="zum-spielende"
          class="self-start rounded bg-emerald-600 px-4 py-2 font-semibold text-white hover:bg-emerald-700"
        >
          Zur Auswertung
        </RouterLink>
      </section>
    </template>
  </main>
</template>
