import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Spiel } from '../api'

/**
 * Hält das aktuell aktive Spiel (nach dem Anlegen bzw. Laden).
 *
 * Bewusst schlank: nur das Nötigste für die Navigation zwischen den Views.
 * Runden-/Punktestand-State kommt in späteren Slices hinzu.
 */
export const useSpielStore = defineStore('spiel', () => {
  const aktuellesSpiel = ref<Spiel | null>(null)
  /** 1-basierte Nummer der aktuell zu erfassenden Runde. */
  const aktuelleRundennummer = ref(1)

  function setzeSpiel(spiel: Spiel): void {
    aktuellesSpiel.value = spiel
    aktuelleRundennummer.value = 1
  }

  function naechsteRunde(): void {
    aktuelleRundennummer.value += 1
  }

  return { aktuellesSpiel, aktuelleRundennummer, setzeSpiel, naechsteRunde }
})
