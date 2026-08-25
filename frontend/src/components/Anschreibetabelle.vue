<script setup lang="ts">
import { computed } from 'vue'
import type { Rundenhistorie, RundenhistorieRunde } from '../api'

const props = defineProps<{ historie: Rundenhistorie }>()

/**
 * Darstellungs-Variante einer Rundenzelle je Spieler (docs/Anschreibetabelle_4_Spieler.md §5):
 * - `setzt-aus`: der Geber setzt aus.
 * - `stern`:     Tausender-Stern (★); der STAND friert ein.
 * - `verlust`:   verlierender Spielmacher; der eingeklammerte Verlustwert rückt ins erste Feld.
 * - `werte`:     reguläres „M | S | Mit" (Schneider = 0 Stiche wird annotiert, SOLLTE-6).
 */
type ZellDarstellung =
  | { art: 'setzt-aus' }
  | { art: 'stern' }
  | { art: 'verlust'; wert: string }
  | { art: 'werte'; m: number; s: number; mit: number; schneider: boolean }

function zellDarstellung(runde: RundenhistorieRunde, name: string): ZellDarstellung {
  const zelle = runde.spieler[name]
  if (zelle.rolle === 'geber') return { art: 'setzt-aus' }
  if (zelle.stern) return { art: 'stern' }
  if (zelle.rolle === 'spielmacher' && runde.verlustwert < 0) {
    return { art: 'verlust', wert: `(${runde.verlustwert})` }
  }
  // Schneider = verfallene Meldung (0 Stiche bei geltendem Stich-Zwang, §2/§5).
  // Bei einfachem Abgehen entfällt der Stich-Zwang, bei Tausender friert der STAND
  // ein – dort ist „0 Stiche" kein Schneider und wird NICHT annotiert.
  const schneider =
    zelle.rolle === 'gegenspieler' &&
    !zelle.hat_eigenen_stich &&
    !runde.ist_tausender &&
    runde.rundenausgang !== 'einfaches_abgehen'
  return {
    art: 'werte',
    m: zelle.meldepunkte,
    s: zelle.stichwerte,
    mit: zelle.mitpunkte,
    schneider,
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
            <div class="text-xs font-normal text-slate-400">M | S | Mit</div>
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

              <span
                v-else-if="zelle.darstellung.art === 'verlust'"
                :data-testid="`verlust-${zeile.runde.rundennummer}-${zelle.name}`"
                class="font-semibold text-red-700"
              >{{ zelle.darstellung.wert }} | 0 | 0</span>

              <span v-else>
                {{ zelle.darstellung.m }} | {{ zelle.darstellung.s }} | {{ zelle.darstellung.mit }}
                <span
                  v-if="zelle.darstellung.schneider"
                  :data-testid="`schneider-${zeile.runde.rundennummer}-${zelle.name}`"
                  class="text-xs italic text-slate-400"
                >(0 Stiche)</span>
              </span>
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
