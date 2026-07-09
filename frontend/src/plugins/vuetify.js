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
});
