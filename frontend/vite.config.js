import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vuetify from 'vite-plugin-vuetify';

export default defineConfig(({ mode }) => ({
  // autoImport : n'importe que les composants Vuetify réellement utilisés dans chaque .vue,
  // au lieu de charger les ~300 composants/directives de la librairie sur toutes les pages
  // (c'était la cause des centaines de requêtes .js/.vue sans rapport à chaque rechargement)
  plugins: [vue(), vuetify({ autoImport: true })],
  resolve: {
    alias: [{ find: '@', replacement: fileURLToPath(new URL('./src', import.meta.url)) }],
    // webpack (Vue CLI) résolvait les imports de composants sans extension (ex: '@/components/app/app-bar')
    extensions: ['.mjs', '.js', '.mts', '.ts', '.jsx', '.tsx', '.json', '.vue'],
  },
  define: {
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_DEVTOOLS__: false,
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false,
  },
  base: mode === 'production' ? '/front/' : '/',
  server: {
    port: 8080,
  },
  test: {
    environment: 'jsdom',
  },
}));
