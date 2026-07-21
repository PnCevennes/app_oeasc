// importé dans le main.js
// configuration de vutify qui est un framework css pour vuejs

import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import { aliases } from 'vuetify/iconsets/md';
import { app as appIconSet } from './icons.js';
import { fr } from 'vuetify/locale';

export default createVuetify({
  components,
  directives,
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
