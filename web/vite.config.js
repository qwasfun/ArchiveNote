import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    tailwindcss(),
    vue(),
    vueDevTools(),
    VitePWA({
      registerType: 'autoUpdate',

      manifest: {
        name: 'ArchiveNote',
        short_name: 'ArchiveNote',
        description: 'ArchiveNote 是一个用于归档文件并记录笔记的工具',
        theme_color: '#ffffff',
        background_color: '#ffffff',
        display: 'standalone',
        start_url: '/',
        icons: [
          { src: 'icons/48.png', sizes: '48x48', type: 'image/png', purpose: 'maskable' },
          { src: 'icons/72.png', sizes: '72x72', type: 'image/png', purpose: 'maskable' },
          { src: 'icons/96.png', sizes: '96x96', type: 'image/png', purpose: 'maskable' },
          { src: 'icons/128.png', sizes: '128x128', type: 'image/png', purpose: 'maskable' },
          { src: 'icons/144.png', sizes: '144x144', type: 'image/png', purpose: 'maskable' },
          {
            src: 'icons/192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'maskable',
          },
          { src: 'icons/256.png', sizes: '256x256', type: 'image/png', purpose: 'maskable' },
          { src: 'icons/512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
