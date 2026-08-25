<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  ApiError,
  letzteRundeAktualisieren,
  punktestaendeLaden,
  rundeAuswerten,
  rundenHistorieLaden,
  spielLaden,
  type PunktestandMap,
  type Rundenhistorie,
  type RundeErgebnis,
  type RundeRequest,
  type RundeVorbelegung,
  type Spiel,
  type SterneMap,
} from '../api'
import { useSpielStore } from '../stores/spiel'
import { aktiveSpieler, geberFuerRunde } from '../domain/rotation'
import RundeForm from '../components/RundeForm.vue'
import Anschreibetabelle from '../components/Anschreibetabelle.vue'

const props = defineProps<{ spielId: string }>()
const spielStore = useSpielStore()

const spiel = ref<Spiel | null>(spielStore.aktuellesSpiel)
const laedt = ref(false)
const fehler = ref<string | null>(null)

const rundeLaedt = ref(false)
const rundeFehler = ref<string | null>(null)
const letztesErgebnis = ref<RundeErgebnis | null>(null)
const punktestaende = ref<PunktestandMap | null>(null)
const sterne = ref<SterneMap | null>(null)
const historie = ref<Rundenhistorie | null>(null)

/** Korrektur-Modus für die letzte Runde (TASK-014 Slice 6, ADR-015). */
const korrekturModus = ref(false)

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

/** Anzahl Tausender-Sterne eines Spielers (0, wenn keine geladen). */
function sterneVon(name: string): number {
  return sterne.value?.[name] ?? 0
}

async function punktestaendeAktualisieren(): Promise<void> {
  if (!spiel.value) return
  try {
    const antwort = await punktestaendeLaden(spiel.value.id)
    punktestaende.value = antwort.punktestaende
    sterne.value = antwort.sterne
  } catch {
    // Punktestände sind ergänzende Info – ein Ladefehler blockiert die Runde nicht.
    punktestaende.value = null
    sterne.value = null
  }
}

async function historieAktualisieren(): Promise<void> {
  if (!spiel.value) return
  try {
    historie.value = await rundenHistorieLaden(spiel.value.id)
    // Letzte Runde für die Korrektur bereitstellen (Slice 6).
    spielStore.setzeLetzteRunde(historie.value.runden.at(-1) ?? null)
  } catch {
    // Anschreibetabelle ist ergänzende Info – ein Ladefehler blockiert die Runde nicht.
    historie.value = null
    spielStore.setzeLetzteRunde(null)
  }
}

/** Interner Rundenausgang → Rundentyp der Erfassung (§16.1: doppeltes Abgehen wird abgeleitet). */
function ausgangZuTyp(ausgang: string): RundeVorbelegung['typ'] {
  switch (ausgang) {
    case 'einfaches_abgehen':
      return 'einfaches_abgehen'
    case 'tausender_gewonnen':
      return 'tausender_gewonnen'
    case 'tausender_verloren':
      return 'tausender_verloren'
    default:
      // gewonnenes_spiel und doppeltes_abgehen werden über „normal" erfasst.
      return 'normal'
  }
}

/** Die zu korrigierende (letzte) Runde aus dem Store. */
const korrekturRunde = computed(() => spielStore.letzteRunde)
const korrekturGeber = computed(() => korrekturRunde.value?.geber ?? '')
const korrekturAktive = computed(() =>
  spiel.value && korrekturRunde.value
    ? aktiveSpieler(spiel.value.spieler, korrekturGeber.value)
    : [],
)

/** Formular-Vorbelegung aus der letzten Runde (M|S je aktivem Spieler). */
const korrekturVorbelegung = computed<RundeVorbelegung | null>(() => {
  const runde = korrekturRunde.value
  if (!runde) return null
  const meldepunkte: Record<string, number> = {}
  const stichwerte: Record<string, number> = {}
  for (const name of korrekturAktive.value) {
    const zelle = runde.spieler[name]
    meldepunkte[name] = zelle?.meldepunkte ?? 0
    stichwerte[name] = zelle?.stichwerte ?? 0
  }
  return {
    typ: ausgangZuTyp(runde.rundenausgang),
    reizwert: runde.reizwert,
    spielmacher: runde.spielmacher,
    meldepunkte,
    stichwerte,
  }
})

/** Ob die Korrektur der letzten Runde angeboten werden kann. */
const kannKorrigieren = computed(() => !!korrekturRunde.value)

function korrekturStarten(): void {
  rundeFehler.value = null
  korrekturModus.value = true
}

function korrekturAbbrechen(): void {
  korrekturModus.value = false
  rundeFehler.value = null
}

async function rundeAbsenden(payload: RundeRequest): Promise<void> {
  if (!spiel.value) return
  rundeLaedt.value = true
  rundeFehler.value = null
  try {
    letztesErgebnis.value = await rundeAuswerten(spiel.value.id, payload)
    spielStore.naechsteRunde()
    await punktestaendeAktualisieren()
    await historieAktualisieren()
  } catch (error) {
    rundeFehler.value =
      error instanceof ApiError ? error.message : 'Runde konnte nicht ausgewertet werden.'
  } finally {
    rundeLaedt.value = false
  }
}

/** PUT-Korrektur der letzten Runde; danach Punktestände, Sterne & Anschreibetabelle neu laden. */
async function korrekturAbsenden(payload: RundeRequest): Promise<void> {
  if (!spiel.value || !korrekturRunde.value) return
  rundeLaedt.value = true
  rundeFehler.value = null
  try {
    letztesErgebnis.value = await letzteRundeAktualisieren(
      spiel.value.id,
      korrekturRunde.value.rundennummer,
      payload,
    )
    korrekturModus.value = false
    // Punktestände + Sterne und Anschreibetabelle spiegeln die neu berechneten
    // Stände; der Sieger wird serverseitig neu berechnet und von SpielendeView
    // beim Öffnen frisch geladen (§9.3).
    await punktestaendeAktualisieren()
    await historieAktualisieren()
  } catch (error) {
    rundeFehler.value =
      error instanceof ApiError ? error.message : 'Korrektur konnte nicht gespeichert werden.'
  } finally {
    rundeLaedt.value = false
  }
}

/** Exakte 1er-Stichwerte der letzten Runde im Store ablegen (Tiebreak, §9.4). */
function tiebreakStichwerteErfassen(werte: Record<string, number>): void {
  spielStore.setzeEndrundenStichwerte(werte)
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
  await historieAktualisieren()
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
            <span class="flex items-center gap-2">
              <span
                v-if="sterneVon(eintrag.name) > 0"
                :data-testid="`sterne-${eintrag.name}`"
                :title="`${sterneVon(eintrag.name)} Tausender-Stern(e)`"
                class="text-amber-500"
              >{{ '★'.repeat(sterneVon(eintrag.name)) }}</span>
              <span data-testid="punktestand-wert">{{ eintrag.punkte }}</span>
            </span>
          </li>
        </ol>
      </section>

      <section v-if="!istBeendet && !korrekturModus" class="flex flex-col gap-3">
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
          :rundenanzahl="spiel.rundenanzahl"
          :laedt="rundeLaedt"
          :fehler="rundeFehler"
          @absenden="rundeAbsenden"
          @tiebreak-stichwerte="tiebreakStichwerteErfassen"
        />

        <button
          v-if="kannKorrigieren"
          type="button"
          data-testid="korrektur-starten"
          class="self-start rounded border border-amber-500 px-4 py-2 text-sm font-semibold text-amber-700 hover:bg-amber-50"
          @click="korrekturStarten"
        >
          Letzte Runde korrigieren
        </button>
      </section>

      <section
        v-else-if="istBeendet && !korrekturModus"
        data-testid="beendet"
        class="flex flex-col gap-3"
      >
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

        <button
          v-if="kannKorrigieren"
          type="button"
          data-testid="korrektur-starten"
          class="self-start rounded border border-amber-500 px-4 py-2 text-sm font-semibold text-amber-700 hover:bg-amber-50"
          @click="korrekturStarten"
        >
          Letzte Runde korrigieren
        </button>
      </section>

      <section
        v-else-if="korrekturModus && korrekturRunde"
        data-testid="korrektur"
        class="flex flex-col gap-3 rounded border border-amber-300 bg-amber-50 p-3"
      >
        <p class="text-sm text-amber-800">
          Korrektur der letzten Runde
          (<strong>Runde {{ korrekturRunde.rundennummer }}</strong>,
          Geber setzt aus: {{ korrekturGeber }}). Nur diese Runde ist editierbar (ADR-015).
        </p>

        <RundeForm
          :key="`korrektur-${korrekturRunde.rundennummer}`"
          :korrektur-modus="true"
          :vorbelegung="korrekturVorbelegung"
          :rundennummer="korrekturRunde.rundennummer"
          :geber="korrekturGeber"
          :aktive="korrekturAktive"
          :rundenanzahl="spiel.rundenanzahl"
          :laedt="rundeLaedt"
          :fehler="rundeFehler"
          @absenden="korrekturAbsenden"
          @tiebreak-stichwerte="tiebreakStichwerteErfassen"
        />

        <button
          type="button"
          data-testid="korrektur-abbrechen"
          class="self-start rounded border border-slate-300 px-4 py-2 text-sm text-slate-600 hover:bg-slate-100"
          @click="korrekturAbbrechen"
        >
          Abbrechen
        </button>
      </section>

      <Anschreibetabelle v-if="historie && historie.runden.length" :historie="historie" />
    </template>
  </main>
</template>
