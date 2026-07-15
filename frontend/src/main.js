import Vue from 'vue';
import App from './App.vue';
import router from '@/router';
import store from '@/store/store';

import vuetify from '@/plugins/vuetify'; // path to vuetify export
import { Promised } from 'vue-promised';
import VueSession from 'vue-session';

import Highcharts from 'highcharts';
import More from 'highcharts/highcharts-more';
import exporting from 'highcharts/modules/exporting';
import HighchartsVue from 'highcharts-vue';

import VueMatomo from 'vue-matomo'

// highcharts est une librairie pour créer des graphiques
More(Highcharts);
exporting(Highcharts);

Vue.config.productionTip = false;
// port d'ecoute du serveur backend 5000. Mettre le meme dans config/config.py
// Vue.config.devServer = { port: 8080, proxy: 'http://localhost:5005' };

// VueSession est une librairie pour gérer les utilisateurs
// persist: true permet de garder les données en mémoire même après un rafraichissement de la page ou fermeture du navigateur
Vue.use(VueSession, { persist: true });

// vutify est un framework css pour vuejs pour les formulaires, boutons, etc
Vue.use(vuetify);
Vue.use(HighchartsVue, {
  highcharts: Highcharts,
});

// vue-matomo est une librairie pour suivre les statistiques de visite (Matomo)
Vue.use(VueMatomo, {
  // Configurez votre instance Matomo en renseignant :
  host: 'https://oeasc-cevennes-parcnational.net/stats/',
  siteId: 6,
  router,
});

// Register the component globally

Vue.component('Promised', Promised);

// Vue.prototype.$apiRequest = apiRequest;
// Vue.prototype.$fail = fail;
new Vue({
  router,
  store,
  vuetify,
  VueSession,
  render: (h) => h(App),
}).$mount('#app');
