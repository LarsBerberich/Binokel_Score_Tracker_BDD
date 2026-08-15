/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  // Dev-Server spiegelt das Prod-Same-Origin-Setup (ADR-010): Anfragen an /api
  // und /health werden an das lokale Django (127.0.0.1:8000) weitergereicht,
  // sodass der Frontend-Code dieselben relativen URLs wie in Produktion nutzt.
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['src/**/*.{test,spec}.ts'],
  },
})
