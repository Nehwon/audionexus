import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: process.env.NODE_ENV !== 'production', // Désactiver sourcemaps en prod pour performance
    minify: 'esbuild', // Plus rapide que terser
    target: 'es2020', // Optimisé pour navigateurs modernes
    chunkSizeWarningLimit: 1000, // Prévenir gros bundles

    // Optimisations de build CRITIQUES pour <2s
    rollupOptions: {
      output: {
        manualChunks: {
          // Séparation en chunks pour chargement différé
          'react-vendor': ['react', 'react-dom'],
          'ui-vendor': ['framer-motion', 'react-icons', 'lucide-react'],
          'charts': ['chart.js', 'react-chartjs-2', 'recharts'],
          'auth': ['axios', '@tanstack/react-query'],
          'audio': ['react-audio-player'],
          'forms': ['react-hook-form', 'react-dropzone'],
        },

        // Noms optimisés pour cache
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name?.split('.') ?? []
          let extType = info[info.length - 1]
          if (/\.(png|jpe?g|gif|svg|ico|webp)$/i.test(assetInfo.name ?? '')) {
            extType = 'img'
          }
          return `assets/${extType}/[name]-[hash][extname]`
        },
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
      },
    },

    // Optimisations performance
    cssMinify: true,
    reportCompressedSize: false, // Désactiver rapport compression (ralentit build)
    watch: process.env.NODE_ENV === 'development' ? {} : null,
  },

  // Optimisations DEV SERVER
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      '@tanstack/react-query',
      'axios',
      'framer-motion'
    ],
    exclude: ['lucide-react'],
  },

  // Configuration de test déplacée vers vitest.config.ts
})