import { createApp, configureCompat } from 'vue';
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

// COMPONENT_ASYNC, COMPONENT_FUNCTIONAL, COMPONENT_V_MODEL et ATTR_FALSE_VALUE sont désactivés
// globalement : ces heuristiques de @vue/compat s'appliquent à tout l'arbre de rendu, y compris à
// l'intérieur de librairies tierces 100% Vue 3 comme Vuetify (VSnackbar, VNavigationDrawer, VMenu),
// où elles provoquent soit des crashs (COMPONENT_ASYNC/FUNCTIONAL), soit du bruit non actionnable
// (COMPONENT_V_MODEL/ATTR_FALSE_VALUE, un composant tiers pré-compilé n'a pas de compatConfig
// accessible). Vérifié (2026-07-09) qu'aucun composant maison du projet ne dépend encore de
// l'ancienne convention value/input pour v-model avant de désactiver COMPONENT_V_MODEL.
// INSTANCE_LISTENERS (actif par défaut en MODE:2) exclut tous les props onXxx (ex: onClick) de
// $attrs pour reproduire le $listeners séparé de Vue 2. Conséquence critique : le mécanisme
// automatique de "fallthrough" des attrs de Vue 3 (qui propage $attrs sur l'élément racine d'un
// composant "transparent" comme VBtn qui ne consomme pas attrs lui-même) ne voit alors plus jamais
// les écouteurs d'événements — un @click sur <v-btn>/<v-app-bar-nav-icon> ne déclenche silencieusement
// rien. Confirmé par test navigateur (2026-07-09) : bouton natif OK, v-btn KO tant que ce flag est actif.
// Le projet n'utilise `this.$listeners` nulle part (vérifié en Phase 2), donc sans risque à désactiver.
// INSTANCE_ATTRS_CLASS_STYLE désactivé pour la même raison (exclusion class/style de $attrs).
// WATCH_ARRAY : ce warning se déclenche pour TOUT watcher ciblant un tableau tant que ce flag
// compat est actif, MÊME quand `deep: true` est déjà explicitement posé (vérifié dans le source
// @vue/compat, fonction createWatcher — le warning n'est pas conditionné à l'absence de `deep`).
// Les 3 watchers de tableau du projet ont été audités et corrigés avec `deep: true` explicite
// (2026-07-09, recherche exhaustive par agent dédié, aucun autre watcher de tableau trouvé) —
// donc sans risque de désactiver ce flag globalement.
configureCompat({
  MODE: 2,
  COMPONENT_ASYNC: false,
  COMPONENT_FUNCTIONAL: false,
  COMPONENT_V_MODEL: false,
  ATTR_FALSE_VALUE: false,
  RENDER_FUNCTION: false,
  INSTANCE_LISTENERS: false,
  INSTANCE_ATTRS_CLASS_STYLE: false,
  WATCH_ARRAY: false,
});

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
