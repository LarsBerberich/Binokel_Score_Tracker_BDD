import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { RundenhistorieRunde, Spiel } from '../api'

/**
 * Hält das aktuell aktive Spiel (nach dem Anlegen bzw. Laden).
 *
 * Bewusst schlank: nur das Nötigste für die Navigation zwischen den Views.
 * Die gezählte Rundennummer, der Geber und der Spielfortschritt werden NICHT
 * hier gehalten, sondern in der SpielView aus der autoritativen Rundenhistorie
 * abgeleitet (FND-006: Tausender laufen außer Konkurrenz und zählen nicht).
 */
export const useSpielStore = defineStore('spiel', () => {
  const aktuellesSpiel = ref<Spiel | null>(null)
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
    letzteRunde.value = null
    endrundenStichwerte.value = null
  }

  function setzeLetzteRunde(runde: RundenhistorieRunde | null): void {
    letzteRunde.value = runde
  }

  function setzeEndrundenStichwerte(werte: Record<string, number> | null): void {
    endrundenStichwerte.value = werte && Object.keys(werte).length > 0 ? werte : null
  }

  return {
    aktuellesSpiel,
    letzteRunde,
    endrundenStichwerte,
    setzeSpiel,
    setzeLetzteRunde,
    setzeEndrundenStichwerte,
  }
})
