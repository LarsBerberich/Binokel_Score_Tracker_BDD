<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  ApiError,
  rundenHistorieLaden,
  siegerErmitteln,
  spielAnlegen,
  spielLaden,
  type Rundenhistorie,
  type SiegerErgebnis,
  type Spiel,
} from '../api'
import { useSpielStore } from '../stores/spiel'
import Anschreibetabelle from '../components/Anschreibetabelle.vue'

const props = defineProps<{ spielId: string }>()
const router = useRouter()
const spielStore = useSpielStore()

const ergebnis = ref<SiegerErgebnis | null>(null)
/** Vollständige Anschreibetabelle samt Abrechnung für die Endabrechnung (weich geladen). */
const historie = ref<Rundenhistorie | null>(null)
/** Das beendete Spiel – liefert Teilnehmer und Rundenzahl für „Neues Spiel mit gleichen Teilnehmern". */
const spiel = ref<Spiel | null>(null)
const laedt = ref(false)
const fehler = ref<string | null>(null)

const neuesSpielLaedt = ref(false)
const neuesSpielFehler = ref<string | null>(null)

const sieger = computed(() => ergebnis.value?.sieger ?? [])
const istGleichstand = computed(() => sieger.value.length > 1)

/** Startet sofort ein neues Spiel mit denselben Teilnehmern, derselben Reihenfolge und Rundenzahl. */
async function neuesSpielMitGleichenTeilnehmern(): Promise<void> {
  if (!spiel.value) return
  neuesSpielLaedt.value = true
  neuesSpielFehler.value = null
  try {
    const neu = await spielAnlegen({
      spieler: [...spiel.value.spieler],
      rundenanzahl: spiel.value.rundenanzahl,
    })
    spielStore.setzeSpiel(neu)
    await router.push({ name: 'spiel', params: { spielId: String(neu.id) } })
  } catch (error) {
    neuesSpielFehler.value =
      error instanceof ApiError ? error.message : 'Das neue Spiel konnte nicht angelegt werden.'
  } finally {
    neuesSpielLaedt.value = false
  }
}

onMounted(async () => {
  laedt.value = true
  fehler.value = null
  const id = Number(props.spielId)
  try {
    // Exakte 1er-Stichwerte der letzten Runde als Tiebreak durchreichen (§9.3/§9.4);
    // ohne erfasste Werte wie bisher ohne Parameter ermitteln.
    const exakte = spielStore.endrundenStichwerte
    const query =
      exakte && Object.keys(exakte).length > 0
        ? Object.entries(exakte)
            .map(([name, wert]) => `${name}:${wert}`)
            .join(',')
        : undefined
    ergebnis.value = await siegerErmitteln(id, query)

    // Die folgenden Angaben sind ergänzend: Ein Ladefehler blendet nur die Tabelle bzw. sperrt den
    // Knopf, Sieger und Ergebnis bleiben sichtbar.
    try {
      historie.value = await rundenHistorieLaden(id)
    } catch {
      historie.value = null
    }
    const imStore = spielStore.aktuellesSpiel
    if (imStore && imStore.id === id) {
      spiel.value = imStore
    } else {
      try {
        spiel.value = await spielLaden(id)
      } catch {
        spiel.value = null
      }
    }
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

      <Anschreibetabelle v-if="historie" :historie="historie" spielende />

      <div class="flex flex-wrap items-center gap-3">
        <RouterLink
          :to="{ name: 'start' }"
          data-testid="neues-spiel"
          class="rounded bg-emerald-600 px-4 py-2 font-semibold text-white hover:bg-emerald-700"
        >
          Neues Spiel
        </RouterLink>
        <button
          type="button"
          data-testid="neues-spiel-gleiche-teilnehmer"
          :disabled="!spiel || neuesSpielLaedt"
          class="rounded border border-emerald-600 px-4 py-2 font-semibold text-emerald-700 hover:bg-emerald-50 disabled:cursor-not-allowed disabled:opacity-50"
          @click="neuesSpielMitGleichenTeilnehmern"
        >
          Neues Spiel mit gleichen Teilnehmern
        </button>
      </div>
      <p
        v-if="neuesSpielFehler"
        data-testid="neues-spiel-fehler"
        role="alert"
        class="text-sm text-red-700"
      >
        {{ neuesSpielFehler }}
      </p>
    </template>
  </main>
</template>
