import { createApp } from 'vue';
import App from './App.vue';
import router from '@/router';
import store from '@/store/store';

import vuetify from '@/plugins/vuetify'; // path to vuetify export
import session from '@/plugins/session';

import Highcharts from 'highcharts';
import More from 'highcharts/highcharts-more';
import exporting from 'highcharts/modules/exporting';
import HighchartsVue from 'highcharts-vue';

import VueMatomo from 'vue-matomo'

// highcharts est une librairie pour créer des graphiques
More(Highcharts);
exporting(Highcharts);

// port d'ecoute du serveur backend 5000. Mettre le meme dans config/config.py
// Vue.config.devServer = { port: 8080, proxy: 'http://localhost:5005' };

const app = createApp(App);

// Configuration du compilateur de templates *à l'exécution* (utilisé par vue3-runtime-template
// pour le contenu markdown/CMS dynamique dans modules/content/content.vue) :
// - whitespace 'condense' : comportement par défaut Vue 3, réglé explicitement pour supprimer
//   l'avertissement CONFIG_WHITESPACE (sans changer le rendu, condense est déjà le comportement réel)
// - isCustomElement : le contenu CMS historique contient des balises HTML obsolètes mais toujours
//   valides (ex: <center>) que le compilateur ne reconnaît pas comme éléments natifs par défaut
app.config.compilerOptions.whitespace = 'condense';
app.config.compilerOptions.isCustomElement = (tag) => tag === 'center';

app.use(router);
app.use(store);
app.use(session);

// vutify est un framework css pour vuejs pour les formulaires, boutons, etc
app.use(vuetify);
app.use(HighchartsVue, {
  highcharts: Highcharts,
});

// vue-matomo est une librairie pour suivre les statistiques de visite (Matomo)
app.use(VueMatomo, {
  // Configurez votre instance Matomo en renseignant :
  host: 'https://stats.cevennes-parcnational.net',
  siteId: 6,
  router,
});

app.mount('#app');
