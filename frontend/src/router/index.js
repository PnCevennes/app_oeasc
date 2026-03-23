// importe les routes depuis les modules dans le repertoire modules/

import Vue from 'vue';
import Router from 'vue-router';
import { page } from '@/modules/page';
import { MODULES_ROUTES } from '@/modules';

Vue.use(Router);

// récupère les routes dans modules.index.js qui ont été rassemblées dans MODULES_ROUTES.
export default new Router({
  routes: [
    // Ajout des routes des modules
    ...MODULES_ROUTES.map((route) => {
      const defaultConfig =
        route.type == 'page'
          ? {
              component: page,
            }
          : {};

      return {
        // retourne un objet avec les propriétés de route et les propriétés de defaultConfig
        ...defaultConfig,
        ...route,
        meta: {
          access: route.access || 0,
          content: route.content, // clé dans la bdd si c'est une page
          hideTitle: route.hideTitle,
          label: route.label,
          title: route.title,
        },
      };
    }),
  ],
});
