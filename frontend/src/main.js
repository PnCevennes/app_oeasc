import { createApp } from 'vue';
import App from './App.vue';
import router from '@/router';
import { installGuards } from '@/router/guards.js';
import store from '@/store/store';
import { ecouterAncienHash } from '@/router/legacy-hash.js';

import vuetify from '@/plugins/vuetify'; // path to vuetify export

import VueMatomo from 'vue-matomo';
import { config } from '@/config/config.js';

// port d'ecoute du serveur backend 5000. Mettre le meme dans config/config.py

const app = createApp(App);

// Configuration du compilateur de templates *à l'exécution* (utilisé par vue3-runtime-template
// pour le contenu markdown/CMS dynamique dans modules/content/content.vue) :
// - whitespace 'condense' : comportement par défaut Vue 3, réglé explicitement pour supprimer
//   l'avertissement CONFIG_WHITESPACE (sans changer le rendu, condense est déjà le comportement réel)
// - isCustomElement : le contenu CMS historique contient des balises HTML obsolètes mais toujours
//   valides (ex: <center>) que le compilateur ne reconnaît pas comme éléments natifs par défaut
app.config.compilerOptions.whitespace = 'condense';
app.config.compilerOptions.isCustomElement = (tag) => tag === 'center';

ecouterAncienHash(router);
installGuards(router, store); // avant app.use(router) : la navigation initiale passe par les gardes
app.use(router);
app.use(store);

// vutify est un framework css pour vuejs pour les formulaires, boutons, etc
app.use(vuetify);

// vue-matomo est une librairie pour suivre les statistiques de visite (Matomo)
// configuré dans install/config_principal.yaml (frontend.matomo) ; désactivé si host est vide
if (config.MATOMO.host) {
  app.use(VueMatomo, {
    host: config.MATOMO.host,
    siteId: config.MATOMO.site_id,
    router,
  });
}

app.mount('#app');
