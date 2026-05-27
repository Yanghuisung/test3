import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const repoBase = process.env.GITHUB_PAGES === 'true' ? '/test2/' : '/'

export default defineConfig({
  plugins: [react()],
  base: repoBase,
  define: {
    'import.meta.env.VITE_SUPABASE_URL': JSON.stringify(process.env.VITE_SUPABASE_URL ?? ''),
    'import.meta.env.VITE_SUPABASE_ANON_KEY': JSON.stringify(process.env.VITE_SUPABASE_ANON_KEY ?? ''),
  },
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
