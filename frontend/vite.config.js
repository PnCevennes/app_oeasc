import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// Migration Vue 2 -> Vue 3 (Phase 3/4) : 'vue' est aliasé vers '@vue/compat', le build de
// migration officiel qui reproduit le comportement Vue 2 par défaut (MODE: 2) tout en tournant
// sur le runtime Vue 3. Chaque composant peut ensuite désactiver le compat mode localement
// (compatConfig: { MODE: 3 }) une fois migré, jusqu'à suppression complète de @vue/compat.
// Le build bundler de @vue/compat inclut déjà le compilateur de templates (nécessaire pour
// vue3-runtime-template dans frontend/src/modules/content/content.vue), pas besoin d'alias supplémentaire.
export default defineConfig(({ mode }) => ({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          compatConfig: { MODE: 2 },
        },
      },
    }),
  ],
  resolve: {
    alias: [
      { find: /^vue$/, replacement: '@vue/compat' },
      { find: '@', replacement: fileURLToPath(new URL('./src', import.meta.url)) },
    ],
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
}));
