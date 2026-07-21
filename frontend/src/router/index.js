// importe les routes depuis les modules dans le repertoire modules/

import { createRouter, createWebHashHistory } from 'vue-router';
import { page } from '@/modules/page';
import { MODULES_ROUTES } from '@/modules';

// récupère les routes dans modules.index.js qui ont été rassemblées dans MODULES_ROUTES.
export default createRouter({
  history: createWebHashHistory(),
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
          large: route.large, // page CMS large (voir modules/page/page.css .page.large)
        },
      };
    }),
  ],
});
