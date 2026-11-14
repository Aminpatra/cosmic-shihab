import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The API sends no CORS headers: the app calls relative /api/... paths.
// In development Vite forwards them to the FastAPI server (docs/DECISIONS.md, #8).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
