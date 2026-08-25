import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { RundenhistorieRunde, Spiel } from '../api'

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
  /**
   * Zuletzt erfasste Runde der Anschreibetabelle (für die Korrektur der letzten
   * Runde, TASK-014 Slice 6). `null`, solange keine Runde gespielt wurde.
   */
  const letzteRunde = ref<RundenhistorieRunde | null>(null)
  /**
   * Exakte 1er-Stichwerte der aktiven Spieler aus der letzten Runde (§9.4).
   * Fließen NICHT in den STAND ein, sondern dienen ausschließlich dem
   * Gleichstand-Tiebreak in `SpielendeView` (§9.3). `null`, solange keine
   * erfasst wurden.
   */
  const endrundenStichwerte = ref<Record<string, number> | null>(null)

  function setzeSpiel(spiel: Spiel): void {
    aktuellesSpiel.value = spiel
    aktuelleRundennummer.value = 1
    letzteRunde.value = null
    endrundenStichwerte.value = null
  }

  function naechsteRunde(): void {
    aktuelleRundennummer.value += 1
  }

  function setzeLetzteRunde(runde: RundenhistorieRunde | null): void {
    letzteRunde.value = runde
  }

  function setzeEndrundenStichwerte(werte: Record<string, number> | null): void {
    endrundenStichwerte.value = werte && Object.keys(werte).length > 0 ? werte : null
  }

  return {
    aktuellesSpiel,
    aktuelleRundennummer,
    letzteRunde,
    endrundenStichwerte,
    setzeSpiel,
    naechsteRunde,
    setzeLetzteRunde,
    setzeEndrundenStichwerte,
  }
})
