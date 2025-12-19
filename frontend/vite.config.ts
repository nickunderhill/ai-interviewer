import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Listen on all interfaces for Docker
    port: 3000, // Changed from default 5173 for Docker
    strictPort: true,
    watch: {
      usePolling: true, // Required for file watching in Docker
      interval: 1000,
    },
  },
});
