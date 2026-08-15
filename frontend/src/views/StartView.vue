<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ApiError, spielAnlegen, type SpielAnlegenRequest } from '../api'
import { useSpielStore } from '../stores/spiel'
import SpielAnlegenForm from '../components/SpielAnlegenForm.vue'

const router = useRouter()
const spielStore = useSpielStore()

const laedt = ref(false)
const fehler = ref<string | null>(null)

async function anlegen(payload: SpielAnlegenRequest): Promise<void> {
  laedt.value = true
  fehler.value = null
  try {
    const spiel = await spielAnlegen(payload)
    spielStore.setzeSpiel(spiel)
    await router.push({ name: 'spiel', params: { spielId: String(spiel.id) } })
  } catch (error) {
    fehler.value =
      error instanceof ApiError ? error.message : 'Unbekannter Fehler beim Anlegen des Spiels.'
  } finally {
    laedt.value = false
  }
}
</script>

<template>
  <main class="view view--start flex flex-col gap-4">
    <h1 class="text-2xl font-bold text-emerald-700">Binokel Score Tracker</h1>
    <SpielAnlegenForm :laedt="laedt" :fehler="fehler" @absenden="anlegen" />
  </main>
</template>
