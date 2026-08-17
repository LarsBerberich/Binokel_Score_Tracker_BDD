<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import type { Gegenspieler, RundeRequest, Rundentyp } from '../api'
import { gegenspielerNamen } from '../domain/rotation'
import { REIZWERT_MINIMUM, STICHWERT_KONTROLLSUMME, ZEHNER_SCHRITT, MELDEPUNKTE_MAXIMUM } from '../domain/regeln'

/**
 * Erfassungsformular für eine einzelne Runde.
 *
 * Der Geber (setzt aus) und die aktiven Spieler werden von oben (SpielView)
 * hereingereicht; die Gegenspieler ergeben sich aus aktiven Spielern minus
 * Spielmacher. Bei gültiger Eingabe wird der passende `RundeRequest` emittiert.
 *
 * Rundentypen zur Auswahl (§16.2): Normales Spiel, Einfaches Abgehen,
 * Tausender gewonnen/verloren. „Doppeltes Abgehen" wird bei normalem Spiel
 * automatisch abgeleitet, wenn M+S < Reizwert (§16.1), und ist daher kein
 * eigener Auswahlpunkt. Sterne ergeben sich ausschließlich aus dem
 * Tausender-Ausgang und werden vom Backend gesetzt (§15.3/§15.5).
 */
const props = withDefaults(
  defineProps<{
    rundennummer: number
    geber: string
    aktive: string[]
    rundenanzahl?: number
    laedt?: boolean
    fehler?: string | null
  }>(),
  { rundenanzahl: 0, laedt: false, fehler: null },
)

const emit = defineEmits<{
  absenden: [payload: RundeRequest]
  'tiebreak-stichwerte': [werte: Record<string, number>]
}>()

const RUNDENTYPEN: { wert: Rundentyp; label: string }[] = [
  { wert: 'normal', label: 'Normales Spiel' },
  { wert: 'einfaches_abgehen', label: 'Einfaches Abgehen' },
  { wert: 'tausender_gewonnen', label: 'Tausender gewonnen' },
  { wert: 'tausender_verloren', label: 'Tausender verloren' },
]

interface SpielerDetail {
  meldepunkte: number
  stichwerte: number
}

const typ = ref<Rundentyp>('normal')
const spielmacher = ref<string>('')
const reizwert = ref<number>(REIZWERT_MINIMUM)

/** Detaileingaben je aktivem Spieler, unabhängig von der Spielmacher-Rolle. */
const details = reactive<Record<string, SpielerDetail>>({})

// Reihenfolge der zuletzt manuell erfassten Stichwerte (vorderster = neuester).
// Die zwei neuesten bleiben editierbar; der dritte Stichwert wird automatisch
// berechnet und gesperrt (012.5, §8.2).
const stichwertReihenfolge = ref<string[]>([])

// Optionale exakte 1er-Stichwerte je aktivem Spieler – nur letzte Runde, nur
// Gleichstand-Tiebreak (§9.4). Getrennt von den Zehner-Stichwerten, die in den
// STAND einfließen.
const tiebreakStichwerte = reactive<Record<string, number>>({})

function synchronisiereDetails(namen: string[]): void {
  for (const name of namen) {
    if (!details[name]) {
      details[name] = { meldepunkte: 0, stichwerte: 0 }
    }
    if (tiebreakStichwerte[name] === undefined) tiebreakStichwerte[name] = 0
  }
  for (const name of Object.keys(details)) {
    if (!namen.includes(name)) delete details[name]
  }
  for (const name of Object.keys(tiebreakStichwerte)) {
    if (!namen.includes(name)) delete tiebreakStichwerte[name]
  }
}

/** Setzt alle Eingaben auf die Startwerte der nächsten Runde zurück (012.6). */
function resetEingaben(): void {
  typ.value = 'normal'
  reizwert.value = REIZWERT_MINIMUM
  stichwertReihenfolge.value = []
  for (const name of Object.keys(details)) {
    details[name].meldepunkte = 0
    details[name].stichwerte = 0
  }
  for (const name of Object.keys(tiebreakStichwerte)) {
    tiebreakStichwerte[name] = 0
  }
}

// Spielmacher + Detaileinträge an die aktiven Spieler koppeln (Runden-/Geberwechsel).
watch(
  () => props.aktive,
  (neu) => {
    synchronisiereDetails(neu)
    stichwertReihenfolge.value = []
    if (!neu.includes(spielmacher.value)) spielmacher.value = neu[0] ?? ''
  },
  { immediate: true },
)

// Nach erfolgreicher Wertung erhöht der Parent die Rundennummer → Formular zurücksetzen.
// Der Reset kommt bewusst aus dem Parent, da RundeForm den POST-Erfolg nicht kennt (012.6).
watch(
  () => props.rundennummer,
  () => resetEingaben(),
)

const gegenspieler = computed(() => gegenspielerNamen(props.aktive, spielmacher.value))
const spielmacherDetail = computed(() => details[spielmacher.value])

const istTausender = computed(
  () => typ.value === 'tausender_gewonnen' || typ.value === 'tausender_verloren',
)
const istNormal = computed(() => typ.value === 'normal')
const istEinfachesAbgehen = computed(() => typ.value === 'einfaches_abgehen')

// In der letzten Runde werden zusätzlich optionale exakte 1er-Stichwerte für den
// Gleichstand-Tiebreak angeboten (§9.4). Die Rundenanzahl kommt vom Parent.
const istLetzteRunde = computed(
  () => props.rundenanzahl > 0 && props.rundennummer === props.rundenanzahl,
)

const brauchtReizwert = computed(() => !istTausender.value)
const reizwertGueltig = computed(
  () =>
    !brauchtReizwert.value ||
    (Number.isInteger(reizwert.value) && reizwert.value >= REIZWERT_MINIMUM),
)

/** Manuell erfasste Stichwert-Spieler (max. 2, neueste zuerst). */
const manuelleStichwertSpieler = computed(() =>
  stichwertReihenfolge.value.filter((name) => props.aktive.includes(name)).slice(0, 2),
)

/**
 * Der aktive Spieler, dessen Stichwert automatisch aus 250 minus den beiden
 * manuell erfassten Werten berechnet wird (§8.2). Erst wenn genau zwei der drei
 * aktiven Spieler manuell erfasst sind, steht der dritte fest.
 */
const autoStichwertSpieler = computed(() => {
  if (props.aktive.length < 3) return null
  if (manuelleStichwertSpieler.value.length < 2) return null
  return props.aktive.find((name) => !manuelleStichwertSpieler.value.includes(name)) ?? null
})

/** Merkt sich, welcher Stichwert zuletzt manuell bearbeitet wurde (012.5). */
function stichwertErfasst(name: string): void {
  // Wird ein Feld geleert/auf 0 gesetzt, gilt es nicht mehr als manuell erfasst;
  // der Spieler wird aus der Reihenfolge entfernt, damit das automatische dritte
  // Feld wieder frei editierbar wird (FND-001, §8.2).
  if (!details[name]?.stichwerte) {
    stichwertReihenfolge.value = stichwertReihenfolge.value.filter((n) => n !== name)
    return
  }
  stichwertReihenfolge.value = [name, ...stichwertReihenfolge.value.filter((n) => n !== name)]
}

// Dritten Stichwert automatisch = 250 − (beide manuellen) setzen und gesperrt halten.
watch(
  () =>
    manuelleStichwertSpieler.value
      .map((name) => `${name}:${details[name]?.stichwerte ?? 0}`)
      .join('|'),
  () => {
    const auto = autoStichwertSpieler.value
    if (!auto || !details[auto]) return
    const summe = manuelleStichwertSpieler.value.reduce(
      (s, name) => s + (details[name]?.stichwerte ?? 0),
      0,
    )
    details[auto].stichwerte = STICHWERT_KONTROLLSUMME - summe
  },
)

/** Summe der Stichwerte aller drei aktiven Spieler (Spielmacher + Gegenspieler). */
const stichwerteSumme = computed(() =>
  props.aktive.reduce((summe, name) => summe + (details[name]?.stichwerte ?? 0), 0),
)
const stichwerteGueltig = computed(() => stichwerteSumme.value === STICHWERT_KONTROLLSUMME)

// Meldepunkte je Spieler dürfen das theoretische Maximum (1800) nicht überschreiten
// und nicht negativ sein (Plausibilitätsgrenze, §7.1).
const meldepunkteGueltig = computed(() =>
  props.aktive.every((name) => {
    const m = details[name]?.meldepunkte ?? 0
    return Number.isInteger(m) && m >= 0 && m <= MELDEPUNKTE_MAXIMUM
  }),
)
const meldepunkteZuHoch = computed(() =>
  props.aktive.some((name) => (details[name]?.meldepunkte ?? 0) > MELDEPUNKTE_MAXIMUM),
)

// Zu hohe manuelle Werte lassen den automatischen dritten Wert negativ werden (ungültig).
const stichwerteNegativ = computed(() =>
  props.aktive.some((name) => (details[name]?.stichwerte ?? 0) < 0),
)

// Alle Werte, die in den kumulierten STAND einfließen, müssen Vielfache von 10
// sein (§9.1/§9.4). step=10 allein genügt nicht, da getippte Einerwerte (z. B. 99)
// durchrutschen könnten – daher explizite Modulo-Prüfung als Absperr-Bedingung.
const werteInStand = computed<number[]>(() => {
  const werte: number[] = []
  if (brauchtReizwert.value) werte.push(reizwert.value)
  if (istNormal.value) {
    for (const name of props.aktive) {
      werte.push(details[name]?.meldepunkte ?? 0, details[name]?.stichwerte ?? 0)
    }
  } else if (istEinfachesAbgehen.value) {
    for (const name of gegenspieler.value) werte.push(details[name]?.meldepunkte ?? 0)
  }
  return werte
})
const moduloVerstoss = computed(() =>
  werteInStand.value.some((w) => !Number.isInteger(w) || w % ZEHNER_SCHRITT !== 0),
)

/** Gesamtwert des Spielmachers (M + S); < Reizwert ⇒ Runde wird doppeltes Abgehen (§16.1). */
const spielmacherGesamt = computed(
  () => (spielmacherDetail.value?.meldepunkte ?? 0) + (spielmacherDetail.value?.stichwerte ?? 0),
)
const wirdDoppeltesAbgehen = computed(
  () => istNormal.value && stichwerteGueltig.value && spielmacherGesamt.value < reizwert.value,
)

const normalGueltig = computed(
  () =>
    reizwertGueltig.value &&
    stichwerteGueltig.value &&
    !stichwerteNegativ.value &&
    !moduloVerstoss.value &&
    meldepunkteGueltig.value,
)

const istGueltig = computed(() => {
  if (spielmacher.value === '') return false
  if (istTausender.value) return true
  if (istNormal.value) return normalGueltig.value
  // Abgehen: nur der Reizwert ist zwingend; keine 250er-Kontrollsumme,
  // da die Stichwerte des Spielmachers nicht erfasst werden.
  return reizwertGueltig.value && !moduloVerstoss.value && meldepunkteGueltig.value
})

function baueGegenspielerNutzlast(): Gegenspieler[] {
  return gegenspieler.value.map((name) => ({
    name,
    meldepunkte: details[name].meldepunkte,
    stichwerte: details[name].stichwerte,
    // Stich-Zwang (§10.3): ein Stichwert > 0 bedeutet mindestens einen eigenen Stich. Zulässig,
    // weil das württembergische Blatt ohne Siebener keinen 0-Augen-Stich kennt (§5.2, kleinster
    // Stich = 6 = drei Unter) – Stichwert 0 heißt also zwingend „kein Stich".
    hat_eigenen_stich: details[name].stichwerte > 0,
  }))
}

function absenden(): void {
  if (!istGueltig.value || props.laedt) return

  // In der letzten Runde die optionalen exakten 1er-Stichwerte an den Parent
  // reichen (Ablage im Pinia-Store → Tiebreak in SpielendeView, §9.4).
  if (istLetzteRunde.value) {
    const exakte: Record<string, number> = {}
    for (const name of props.aktive) {
      const wert = tiebreakStichwerte[name] ?? 0
      if (wert > 0) exakte[name] = wert
    }
    emit('tiebreak-stichwerte', exakte)
  }

  const basis = {
    rundennummer: props.rundennummer,
    spielmacher: spielmacher.value,
    geber: props.geber,
  }

  if (istTausender.value) {
    emit('absenden', { ...basis, typ: typ.value } as RundeRequest)
    return
  }

  if (istNormal.value) {
    emit('absenden', {
      ...basis,
      typ: 'normal',
      reizwert: reizwert.value,
      meldepunkte: spielmacherDetail.value.meldepunkte,
      stichwerte: spielmacherDetail.value.stichwerte,
      // Stich-Zwang gilt auch für den Spielmacher (§10.4); aus dem Stichwert abgeleitet.
      hat_eigenen_stich: spielmacherDetail.value.stichwerte > 0,
      gegenspieler: baueGegenspielerNutzlast(),
    })
    return
  }

  if (istEinfachesAbgehen.value) {
    // Einfaches Abgehen: nur Meldepunkte je Gegenspieler, kein Stich-Zwang.
    emit('absenden', {
      ...basis,
      typ: 'einfaches_abgehen',
      reizwert: reizwert.value,
      gegenspieler: gegenspieler.value.map((name) => ({
        name,
        meldepunkte: details[name].meldepunkte,
      })),
    })
  }
}
</script>

<template>
  <form class="flex flex-col gap-4" novalidate @submit.prevent="absenden">
    <fieldset class="flex flex-col gap-3 border-0 p-0" :disabled="laedt">
      <legend class="text-lg font-semibold">Runde {{ rundennummer }} erfassen</legend>

      <label class="flex flex-col gap-1">
        <span class="text-sm text-slate-600">Rundentyp</span>
        <select v-model="typ" data-testid="typ" class="rounded border border-slate-300 px-3 py-2">
          <option v-for="rt in RUNDENTYPEN" :key="rt.wert" :value="rt.wert">{{ rt.label }}</option>
        </select>
      </label>

      <label class="flex flex-col gap-1">
        <span class="text-sm text-slate-600">Spielmacher</span>
        <select
          v-model="spielmacher"
          data-testid="spielmacher"
          class="rounded border border-slate-300 px-3 py-2"
        >
          <option v-for="name in aktive" :key="name" :value="name">{{ name }}</option>
        </select>
      </label>

      <p class="text-sm text-slate-600">
        Gegenspieler: <strong data-testid="gegenspieler">{{ gegenspieler.join(', ') }}</strong>
      </p>

      <label v-if="brauchtReizwert" class="flex flex-col gap-1">
        <span class="text-sm text-slate-600">Reizwert</span>
        <input
          v-model.number="reizwert"
          type="number"
          :min="REIZWERT_MINIMUM"
          :step="ZEHNER_SCHRITT"
          data-testid="reizwert"
          class="rounded border border-slate-300 px-3 py-2"
        />
      </label>

      <!-- Detailfelder: normale Runde (009.3) -->
      <div v-if="istNormal && spielmacherDetail" class="flex flex-col gap-3">
        <fieldset class="flex flex-col gap-2 rounded border border-slate-200 p-3">
          <legend class="px-1 text-sm font-semibold text-emerald-700">
            Spielmacher: {{ spielmacher }}
          </legend>
          <label class="flex flex-col gap-1">
            <span class="text-sm text-slate-600">Meldepunkte</span>
            <input
              v-model.number="spielmacherDetail.meldepunkte"
              type="number"
              min="0"
              :max="MELDEPUNKTE_MAXIMUM"
              :step="ZEHNER_SCHRITT"
              data-testid="sm-meldepunkte"
              class="rounded border border-slate-300 px-3 py-2"
            />
          </label>
          <label class="flex flex-col gap-1">
            <span class="text-sm text-slate-600">
              Stichwerte (inkl. gedrückter Karten)
              <span v-if="spielmacher === autoStichwertSpieler" class="text-slate-400"
                >— automatisch</span
              >
            </span>
            <input
              v-model.number="spielmacherDetail.stichwerte"
              type="number"
              min="0"
              :step="ZEHNER_SCHRITT"
              :readonly="spielmacher === autoStichwertSpieler"
              data-testid="sm-stichwerte"
              class="rounded border border-slate-300 px-3 py-2 read-only:bg-slate-100 read-only:text-slate-500"
              @input="stichwertErfasst(spielmacher)"
            />
          </label>
        </fieldset>

        <fieldset
          v-for="name in gegenspieler"
          :key="name"
          class="flex flex-col gap-2 rounded border border-slate-200 p-3"
        >
          <legend class="px-1 text-sm font-semibold text-slate-700">Gegenspieler: {{ name }}</legend>
          <label class="flex flex-col gap-1">
            <span class="text-sm text-slate-600">Meldepunkte</span>
            <input
              v-model.number="details[name].meldepunkte"
              type="number"
              min="0"
              :max="MELDEPUNKTE_MAXIMUM"
              :step="ZEHNER_SCHRITT"
              :data-testid="`gs-meldepunkte-${name}`"
              class="rounded border border-slate-300 px-3 py-2"
            />
          </label>
          <label class="flex flex-col gap-1">
            <span class="text-sm text-slate-600">
              Stichwerte
              <span v-if="name === autoStichwertSpieler" class="text-slate-400">— automatisch</span>
            </span>
            <input
              v-model.number="details[name].stichwerte"
              type="number"
              min="0"
              :step="ZEHNER_SCHRITT"
              :readonly="name === autoStichwertSpieler"
              :data-testid="`gs-stichwerte-${name}`"
              class="rounded border border-slate-300 px-3 py-2 read-only:bg-slate-100 read-only:text-slate-500"
              @input="stichwertErfasst(name)"
            />
          </label>
        </fieldset>

        <p
          data-testid="stichwerte-summe"
          class="text-sm"
          :class="stichwerteGueltig ? 'text-emerald-700' : 'text-amber-700'"
        >
          Stichwerte-Summe: {{ stichwerteSumme }} / {{ STICHWERT_KONTROLLSUMME }}
          <span v-if="!stichwerteGueltig"> — muss genau {{ STICHWERT_KONTROLLSUMME }} ergeben</span>
        </p>

        <p class="text-xs text-slate-500">
          Zwei Stichwerte genügen – der dritte wird automatisch berechnet. Stichwerte auf die
          nächste Zehner runden (Eingabeschritt 10).
        </p>

        <p v-if="stichwerteNegativ" data-testid="stichwerte-fehler" class="text-sm text-red-700">
          Die erfassten Stichwerte übersteigen {{ STICHWERT_KONTROLLSUMME }} – bitte korrigieren.
        </p>

        <p v-if="meldepunkteZuHoch" data-testid="meldepunkte-fehler" class="text-sm text-red-700">
          Meldepunkte eines Spielers können höchstens {{ MELDEPUNKTE_MAXIMUM }} betragen – bitte
          korrigieren.
        </p>

        <p
          v-if="wirdDoppeltesAbgehen"
          data-testid="doppeltes-abgehen-hinweis"
          class="text-sm text-amber-700"
        >
          {{ spielmacher }} erreicht den Reizwert nicht (M+S {{ spielmacherGesamt }} &lt;
          {{ reizwert }}) – die Runde wird als doppeltes Abgehen gewertet.
        </p>
      </div>

      <!-- Detailfelder: Einfaches Abgehen (009.4) -->
      <div v-if="istEinfachesAbgehen" class="flex flex-col gap-3">
        <p data-testid="abgehen-hinweis" class="text-sm text-slate-600">
          {{ spielmacher }} geht ab – einfacher Verlust. Die Gegenspieler erhalten je 30 Mitpunkte.
        </p>

        <fieldset
          v-for="name in gegenspieler"
          :key="name"
          class="flex flex-col gap-2 rounded border border-slate-200 p-3"
        >
          <legend class="px-1 text-sm font-semibold text-slate-700">Gegenspieler: {{ name }}</legend>
          <label class="flex flex-col gap-1">
            <span class="text-sm text-slate-600">Meldepunkte</span>
            <input
              v-model.number="details[name].meldepunkte"
              type="number"
              min="0"
              :max="MELDEPUNKTE_MAXIMUM"
              :step="ZEHNER_SCHRITT"
              :data-testid="`gs-meldepunkte-${name}`"
              class="rounded border border-slate-300 px-3 py-2"
            />
          </label>
        </fieldset>

        <p v-if="meldepunkteZuHoch" data-testid="meldepunkte-fehler" class="text-sm text-red-700">
          Meldepunkte eines Spielers können höchstens {{ MELDEPUNKTE_MAXIMUM }} betragen – bitte
          korrigieren.
        </p>
      </div>

      <!-- Letzte Runde: optionale exakte 1er-Stichwerte für den Gleichstand-Tiebreak (§9.4) -->
      <fieldset
        v-if="istLetzteRunde && !istTausender"
        data-testid="tiebreak-block"
        class="flex flex-col gap-2 rounded border border-amber-200 bg-amber-50 p-3"
      >
        <legend class="px-1 text-sm font-semibold text-amber-800">
          Letzte Runde – exakte Stichwerte (Tiebreak, optional)
        </legend>
        <p class="text-xs text-amber-700">
          Nur bei möglichem Gleichstand um den Gesamtsieg nötig: die exakten 1er-Stichwerte je
          Spieler. Sie fließen nicht in den STAND ein.
        </p>
        <label v-for="name in aktive" :key="name" class="flex flex-col gap-1">
          <span class="text-sm text-slate-600">{{ name }}</span>
          <input
            v-model.number="tiebreakStichwerte[name]"
            type="number"
            min="0"
            step="1"
            :data-testid="`tiebreak-${name}`"
            class="rounded border border-slate-300 px-3 py-2"
          />
        </label>
      </fieldset>
    </fieldset>

    <p
      v-if="moduloVerstoss"
      data-testid="stichwerte-modulo-fehler"
      class="text-sm text-red-700"
    >
      Alle Werte, die in den STAND einfließen (Reizwert, Meldepunkte, Stichwerte), müssen volle
      Zehner sein (Vielfache von {{ ZEHNER_SCHRITT }}) – bitte korrigieren.
    </p>

    <p v-if="fehler" data-testid="runde-fehler" role="alert" class="text-sm text-red-700">
      {{ fehler }}
    </p>

    <button
      type="submit"
      data-testid="runde-absenden"
      :disabled="!istGueltig || laedt"
      class="rounded bg-emerald-600 px-4 py-2 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
    >
      {{ laedt ? 'Wird gewertet …' : 'Runde werten' }}
    </button>
  </form>
</template>
