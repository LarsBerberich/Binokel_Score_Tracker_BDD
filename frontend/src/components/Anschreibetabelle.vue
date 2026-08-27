<script setup lang="ts">
import { computed } from 'vue'
import { RUNDENAUSGANG } from '../api'
import type { Rundenhistorie, RundenhistorieRunde } from '../api'

const props = defineProps<{ historie: Rundenhistorie }>()

/**
 * Darstellungs-Variante einer Rundenzelle je Spieler (docs/Anschreibetabelle_4_Spieler.md §5):
 * - `setzt-aus`: der Geber setzt aus.
 * - `stern`:     Tausender-Stern (★); der STAND friert ein.
 * - `verlust`:   verlierender Spielmacher; der eingeklammerte Verlustwert rückt ins erste Feld.
 * - `werte`:     reguläres „M / S (/ Mit)" (Schneider = 0 Stiche wird annotiert, SOLLTE-6).
 * `zeige_mit`: Mitpunkte entstehen nur beim Abgehen; bei gewonnenem Spiel/Tausender entfällt die Mit-Zeile.
 */
type ZellDarstellung =
  | { art: 'setzt-aus' }
  | { art: 'stern' }
  | { art: 'verlust'; wert: string; zeige_mit: boolean }
  | { art: 'werte'; m: number; s: number; mit: number; schneider: boolean; zeige_mit: boolean }

/** Mitpunkte sind nur bei den beiden Abgeh-Ausgängen relevant (Gegenspieler kassieren „Mit"). */
function zeigtMitpunkte(runde: RundenhistorieRunde): boolean {
  return (
    runde.rundenausgang === RUNDENAUSGANG.EINFACHES_ABGEHEN ||
    runde.rundenausgang === RUNDENAUSGANG.DOPPELTES_ABGEHEN
  )
}

function zellDarstellung(runde: RundenhistorieRunde, name: string): ZellDarstellung {
  const zelle = runde.spieler[name]
  if (zelle.rolle === 'geber') return { art: 'setzt-aus' }
  if (zelle.stern) return { art: 'stern' }
  if (zelle.rolle === 'spielmacher' && runde.verlustwert < 0) {
    return { art: 'verlust', wert: `(${runde.verlustwert})`, zeige_mit: zeigtMitpunkte(runde) }
  }
  // Schneider = verfallene Meldung (0 Stiche bei geltendem Stich-Zwang, §2/§5).
  // Bei einfachem Abgehen entfällt der Stich-Zwang, bei Tausender friert der STAND
  // ein – dort ist „0 Stiche" kein Schneider und wird NICHT annotiert.
  const schneider =
    zelle.rolle === 'gegenspieler' &&
    !zelle.hat_eigenen_stich &&
    !runde.ist_tausender &&
    runde.rundenausgang !== RUNDENAUSGANG.EINFACHES_ABGEHEN
  return {
    art: 'werte',
    m: zelle.meldepunkte,
    s: zelle.stichwerte,
    mit: zelle.mitpunkte,
    schneider,
    zeige_mit: zeigtMitpunkte(runde),
  }
}

/** Vorberechnete zweizeilige Struktur (Rundenzelle + STAND) je Runde und Spieler. */
const zeilen = computed(() =>
  props.historie.runden.map((runde) => ({
    runde,
    zellen: props.historie.spieler.map((name) => ({
      name,
      darstellung: zellDarstellung(runde, name),
      stand: runde.stand[name],
    })),
  })),
)

/**
 * Kurzlabel des Rundenausgangs für die „Gereizt bis"-Spalte (§5-Annotation, FND-005):
 * macht den Ausgang jeder Runde auf einen Blick sichtbar (gewonnen / abgegangen / Tausender).
 */
function ausgangLabel(runde: RundenhistorieRunde): string {
  switch (runde.rundenausgang) {
    case RUNDENAUSGANG.GEWONNENES_SPIEL:
      return 'gewonnen'
    case RUNDENAUSGANG.EINFACHES_ABGEHEN:
      return 'einfaches Abgehen'
    case RUNDENAUSGANG.DOPPELTES_ABGEHEN:
      return 'doppeltes Abgehen'
    case RUNDENAUSGANG.TAUSENDER_GEWONNEN:
      return 'gewonnen'
    case RUNDENAUSGANG.TAUSENDER_VERLOREN:
      return 'verloren'
    default:
      return ''
  }
}
</script>

<template>
  <section
    data-testid="anschreibetabelle"
    class="flex flex-col gap-2 rounded border border-slate-200 p-3"
  >
    <h2 class="text-lg font-semibold text-slate-700">Anschreibetabelle</h2>

    <p
      v-if="!historie.runden.length"
      data-testid="anschreibetabelle-leer"
      class="text-sm text-slate-500"
    >
      Noch keine Runden erfasst.
    </p>

    <table v-else class="w-full border-collapse text-center text-sm">
      <thead>
        <tr class="border-b border-slate-300 text-slate-600">
          <th class="px-2 py-1">Runde</th>
          <th class="px-2 py-1">Geber</th>
          <th class="px-2 py-1">Gereizt bis</th>
          <th class="px-2 py-1">Wert</th>
          <th v-for="name in historie.spieler" :key="name" class="px-2 py-1">
            {{ name }}
          </th>
        </tr>
      </thead>
      <tbody>
        <template v-for="zeile in zeilen" :key="zeile.runde.rundennummer">
          <!-- Rundenzeile: getrennte M | S | Mit-Erfassung -->
          <tr :data-testid="`runde-${zeile.runde.rundennummer}`" class="border-t border-slate-200">
            <td :rowspan="2" class="px-2 py-1 font-semibold">{{ zeile.runde.rundennummer }}</td>
            <td :rowspan="2" class="px-2 py-1">{{ zeile.runde.geber }}</td>
            <td :rowspan="2" class="px-2 py-1">
              <span v-if="zeile.runde.ist_tausender" :data-testid="`tausender-${zeile.runde.rundennummer}`">
                Tausender
              </span>
              <span v-else>{{ zeile.runde.reizwert }}</span>
              <div class="text-xs text-slate-400">/ {{ zeile.runde.spielmacher }}</div>
              <div
                class="text-xs italic text-slate-500"
                :data-testid="`ausgang-${zeile.runde.rundennummer}`"
              >{{ ausgangLabel(zeile.runde) }}</div>
            </td>
            <td class="px-2 py-1 text-slate-500">Runde</td>
            <td
              v-for="zelle in zeile.zellen"
              :key="zelle.name"
              :data-testid="`runde-${zeile.runde.rundennummer}-${zelle.name}`"
              class="px-2 py-1"
            >
              <span
                v-if="zelle.darstellung.art === 'setzt-aus'"
                :data-testid="`setzt-aus-${zeile.runde.rundennummer}-${zelle.name}`"
                class="italic text-slate-400"
              >— (setzt aus)</span>

              <span
                v-else-if="zelle.darstellung.art === 'stern'"
                :data-testid="`stern-${zeile.runde.rundennummer}-${zelle.name}`"
                class="text-amber-500"
              >★</span>

              <div
                v-else-if="zelle.darstellung.art === 'verlust'"
                :data-testid="`verlust-${zeile.runde.rundennummer}-${zelle.name}`"
                class="mx-auto grid w-fit grid-cols-[auto_auto] items-baseline gap-x-2 tabular-nums"
              >
                <span class="text-left text-xs text-slate-400">M</span>
                <span class="text-right font-semibold text-red-700">{{ zelle.darstellung.wert }}</span>
                <span class="text-left text-xs text-slate-400">S</span>
                <span class="text-right">0</span>
                <template v-if="zelle.darstellung.zeige_mit">
                  <span class="text-left text-xs text-slate-400">Mit</span>
                  <span class="text-right">0</span>
                </template>
              </div>

              <div v-else class="flex flex-col items-center">
                <div class="grid w-fit grid-cols-[auto_auto] items-baseline gap-x-2 tabular-nums">
                  <span class="text-left text-xs text-slate-400">M</span>
                  <span class="text-right">{{ zelle.darstellung.m }}</span>
                  <span class="text-left text-xs text-slate-400">S</span>
                  <span class="text-right">{{ zelle.darstellung.s }}</span>
                  <template v-if="zelle.darstellung.zeige_mit">
                    <span class="text-left text-xs text-slate-400">Mit</span>
                    <span class="text-right">{{ zelle.darstellung.mit }}</span>
                  </template>
                </div>
                <span
                  v-if="zelle.darstellung.schneider"
                  :data-testid="`schneider-${zeile.runde.rundennummer}-${zelle.name}`"
                  class="text-xs italic text-slate-400"
                >(0 Stiche)</span>
              </div>
            </td>
          </tr>

          <!-- STAND-Zeile: kumulierter Kontostand -->
          <tr class="border-b border-slate-200 font-semibold">
            <td class="px-2 py-1 text-slate-500">STAND</td>
            <td
              v-for="zelle in zeile.zellen"
              :key="zelle.name"
              :data-testid="`stand-${zeile.runde.rundennummer}-${zelle.name}`"
              class="px-2 py-1"
            >{{ zelle.stand }}</td>
          </tr>
        </template>
      </tbody>
    </table>
  </section>
</template>
