import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

// Leere Route-Struktur passend zu den fachlichen Slices 1–6.
// Views sind vorerst Platzhalter und werden in TASK-008/009 gefüllt.
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'start',
    // Slice 1: Spiel anlegen
    component: () => import('../views/StartView.vue'),
  },
  {
    path: '/spiel/:spielId',
    name: 'spiel',
    // Slices 2–5: Runde eingeben und auswerten
    component: () => import('../views/SpielView.vue'),
    props: true,
  },
  {
    path: '/spiel/:spielId/ende',
    name: 'spielende',
    // Slice 6: Spielende und Siegerermittlung
    component: () => import('../views/SpielendeView.vue'),
    props: true,
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/NotFoundView.vue'),
  },
]

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
