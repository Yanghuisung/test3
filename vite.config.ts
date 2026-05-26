import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const repoBase = process.env.GITHUB_PAGES === 'true' ? '/test2/' : '/'

export default defineConfig({
  plugins: [react()],
  base: repoBase,
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    emptyOutDir: true,
  },
  server: {
    host: true,
    port: 5174,
  },
})
