import Vue from 'vue'
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'
import fr from 'vuetify/src/locale/fr.ts';

Vue.use(Vuetify)

const opts = {
    lang: { locales: { fr }, current: 'fr' }
}

export default new Vuetify(opts)
