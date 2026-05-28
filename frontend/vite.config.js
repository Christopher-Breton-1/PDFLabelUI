import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vite.dev/config/
export default defineConfig({
  plugins: [svelte()],
  server: {
    host: '0.0.0.0', // bind to all network interfaces
    port: 5174,
    watch: {
      usePolling: true, // necessary for docker environments
    },
    strictPort: true,
  },
});