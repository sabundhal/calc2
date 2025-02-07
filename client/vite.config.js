import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import vuetify from 'vite-plugin-vuetify'
import path from 'path';

export default defineConfig({
  plugins: [
    vue(),
    vuetify({
      autoImport: true,
    }),
  ],
  define: { 'process.env': {} },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
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