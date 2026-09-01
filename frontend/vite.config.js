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
    alias: [
      { find: '@', replacement: fileURLToPath(new URL('./src', import.meta.url)) },
      // vue3-runtime-template (contenu CMS/markdown dynamique dans modules/content/content.vue)
      // compile des templates à l'exécution : ça nécessite le build complet de Vue (avec compilateur),
      // alors que Vite résout "vue" vers le build runtime-only par défaut.
      { find: 'vue', replacement: 'vue/dist/vue.esm-bundler.js' },
    ],
    // webpack (Vue CLI) résolvait les imports de composants sans extension (ex: '@/components/app/app-bar')
    extensions: ['.mjs', '.js', '.mts', '.ts', '.jsx', '.tsx', '.json', '.vue'],
  },
  optimizeDeps: {
    // Sans ça, Vite découvre ces composants Vuetify au fil de la navigation (autoImport par composant)
    // et force plusieurs reloads complets en pleine navigation, ce qui casse le routeur au premier
    // accès à froid sur les routes qui les utilisent. Liste extraite de tous les tags <v-xxx> présents
    // dans src/**/*.vue : à compléter si un nouveau composant Vuetify est utilisé dans le futur.
    include: [
      'vuetify/components/VApp',
      'vuetify/components/VAppBar',
      'vuetify/components/VAutocomplete',
      'vuetify/components/VBreadcrumbs',
      'vuetify/components/VBtn',
      'vuetify/components/VBtnToggle',
      'vuetify/components/VCard',
      'vuetify/components/VCheckbox',
      'vuetify/components/VChip',
      'vuetify/components/VChipGroup',
      'vuetify/components/VCombobox',
      'vuetify/components/VDataTable',
      'vuetify/components/VDialog',
      'vuetify/components/VDivider',
      'vuetify/components/VExpansionPanel',
      'vuetify/components/VFileInput',
      'vuetify/components/VForm',
      'vuetify/components/VGrid',
      'vuetify/components/VIcon',
      'vuetify/components/VList',
      'vuetify/components/VMenu',
      'vuetify/components/VNavigationDrawer',
      'vuetify/components/VOverlay',
      'vuetify/components/VProgressCircular',
      'vuetify/components/VProgressLinear',
      'vuetify/components/VRadio',
      'vuetify/components/VRadioGroup',
      'vuetify/components/VSelect',
      'vuetify/components/VSnackbar',
      'vuetify/components/VSwitch',
      'vuetify/components/VTable',
      'vuetify/components/VTabs',
      'vuetify/components/VTextarea',
      'vuetify/components/VTextField',
      'vuetify/components/VTooltip',
      'vuetify/components/VWindow',
      'vuetify/components/transitions',
    ],
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
