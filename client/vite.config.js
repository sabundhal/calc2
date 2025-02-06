import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
    server: {
    port: 8080,
    //прокси только для локального использования, в проде весь трафик идет через nginx
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000'
      },
    },
  }
})