// importé dans le main.js
// configuration de vutify qui est un framework css pour vuejs

import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import { aliases } from 'vuetify/iconsets/md';
import { app as appIconSet } from './icons.js';
import { fr } from 'vuetify/locale';

// components/directives ne sont plus importés en bloc ici : vite-plugin-vuetify
// (voir vite.config.js, autoImport: true) injecte à la compilation, pour chaque .vue,
// uniquement les composants/directives Vuetify réellement utilisés dans son template.
// 'vuetify/styles' est gardé (setup standard documenté par vite-plugin-vuetify) : c'est UN SEUL
// fichier CSS déjà compilé (~18000 lignes, node_modules/vuetify/lib/styles/main.css), pas une pile
// de fichiers par composant — il fournit les classes utilitaires/animations qui ne sont liées à
// aucun composant précis (bg-*, elevation-*, @keyframes v-shake, etc.), pas fournies autrement.
// Ne pas le retirer : la vraie cause d'un chargement massif de CSS par composant sans rapport
// avec la page (VFab/VRating/VStepper/...) était ailleurs, voir generic-table.vue plus bas.
export default createVuetify({
  icons: {
    defaultSet: 'app',
    aliases,
    sets: { app: appIconSet },
  },
  locale: {
    locale: 'fr',
    fallback: 'en',
    messages: { fr },
  },
  defaults: {
    // Vuetify 3 utilise par défaut le variant "filled" (fond grisé) pour les champs de saisie,
    // contrairement à Vuetify 2 qui n'appliquait pas de fond. On revient à un style sans fond
    // pour conserver l'apparence d'origine de l'application.
    VTextField: { variant: 'underlined' },
    VSelect: { variant: 'underlined' },
    VAutocomplete: { variant: 'underlined' },
    VCombobox: { variant: 'underlined' },
    VTextarea: { variant: 'underlined' },
    VFileInput: { variant: 'underlined' },
  },
});
