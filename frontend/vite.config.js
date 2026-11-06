import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vuetify from 'vite-plugin-vuetify';
import { existsSync, readFileSync } from 'node:fs';
import yaml from 'js-yaml';

// Expose au frontend, depuis install/config_principal.yaml (repli sur le .sample si le fichier réel
// est absent, ex. CI), uniquement :
//   - `virtual:config-declaration` : declaration.STATUT_DECLARATION
//   - `virtual:config-frontend`    : urls (application, frontend), application.id_app et section `frontend`
//     (matomo, mapbox)
// Les autres sections contiennent des secrets : elles ne doivent jamais atteindre le bundle.
const CONFIG_DECLARATION_ID = 'virtual:config-declaration';
const CONFIG_FRONTEND_ID = 'virtual:config-frontend';

// "localhost:5005" -> "http://localhost:5005" : le navigateur a besoin d'un schéma explicite
const avecSchema = (url) => (/^https?:\/\//.test(url) ? url : `http://${url}`);

function configPrincipal() {
  const dossier = fileURLToPath(new URL('../install/', import.meta.url));
  const reel = `${dossier}config_principal.yaml`;
  const fichier = process.env.OEASC_CONFIG || (existsSync(reel) ? reel : `${reel}.sample`);
  const exposes = {
    [CONFIG_DECLARATION_ID]: (c) => ({ STATUT_DECLARATION: c.declaration.STATUT_DECLARATION }),
    [CONFIG_FRONTEND_ID]: (c) => ({
      // normalisées comme dans backend/config.py : le code concatène URL_APPLICATION + '/api/...'
      URL_APPLICATION: avecSchema(c.urls.application).replace(/\/+$/, ''),
      URL_FRONTEND: `${avecSchema(c.urls.frontend).replace(/\/+$/, '')}/`,
      ID_APPLICATION: String(c.application.id_app),
      MATOMO: c.frontend?.matomo || {},
      MAPBOX: c.frontend?.mapbox || {},
    }),
  };
  return {
    name: 'oeasc-config-principal',
    resolveId: (id) => (id in exposes ? `\0${id}` : null),
    load(id) {
      const cle = id.slice(1);
      if (!id.startsWith('\0') || !(cle in exposes)) return null;
      this.addWatchFile(fichier);
      const config = yaml.load(readFileSync(fichier, 'utf-8'));
      return `export default ${JSON.stringify(exposes[cle](config))};`;
    },
  };
}

export default defineConfig(({ mode }) => ({
  // autoImport : n'importe que les composants Vuetify réellement utilisés dans chaque .vue,
  // au lieu de charger les ~300 composants/directives de la librairie sur toutes les pages
  // (c'était la cause des centaines de requêtes .js/.vue sans rapport à chaque rechargement)
  plugins: [vue(), vuetify({ autoImport: true }), configPrincipal()],
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
      'vuetify/components/VNumberInput',
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
