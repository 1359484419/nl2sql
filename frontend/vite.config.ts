import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api/v1/query': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/api/v1/schema': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/api/v1/index': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/api/v1/learning': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
