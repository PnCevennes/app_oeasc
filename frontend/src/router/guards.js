// Gardes de navigation : session utilisateur + contrôle d'accès (meta.access) AVANT le rendu de la route.
// La vraie sécurité reste côté backend ; ceci évite de monter un composant protégé puis de rediriger.

import { appliquerSeo } from './seo.js';

let initialCheckDone = false;

export function installGuards(router, store) {
  // met à jour l'utilisateur du store depuis la session Flask
  const refreshUser = () =>
    store.dispatch('testConnexion', {}).then(
      (user) => store.commit('user', user),
      () => store.commit('user', {})
    );

  router.beforeEach(async (to) => {
    const access = to.meta.access || 0;
    // session testée à la première navigation, puis seulement avant une route protégée
    // (le store est tenu à jour par login/logout)
    if (!initialCheckDone || access) {
      await refreshUser();
      initialCheckDone = true;
    }
    if (access > store.getters.droitMax) {
      return { name: 'user.login', query: { redirect: to.fullPath } };
    }
  });

  // titre, description, canonical, robots et Open Graph (voir router/seo.js). Les pages de contenu CMS
  // affinent ensuite titre et description une fois leur texte chargé (modules/content/content.vue).
  router.afterEach((to) => appliquerSeo(to));
}
