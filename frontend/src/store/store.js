/*
  Les stores sont directement ajoutés depuis modules/index.js pour les modules
  depuis /core/js/data/api.js pour la gestion des requête api vers le back
  depuis /components/form pour la gestion des formulaires.
  Si il faut en rajouter en lien avec des modules, i
*/

import { createStore } from 'vuex';
import { MODULES_STORE } from '@/modules';
import { STORE as FORM_STORE } from '@/components/form';

const storeDefinition = {
  getters: {},
  mutations: {},
  actions: {},
  state: {},
};

const stores = [MODULES_STORE, FORM_STORE];

for (const store of stores) {
  for (const key of Object.keys(storeDefinition)) {
    storeDefinition[key] = { ...storeDefinition[key], ...store[key] };
  }
}

let store = createStore(storeDefinition);

// Après toute écriture API réussie (POST/PATCH/PUT/DELETE, cf. core/js/data/api.js), on vide les
// caches qui ne sont pas mis à jour par les actions génériques, pour que les listes se rechargent.
// Les stores génériques (addStore) mettent déjà leur état à jour eux-mêmes.
window.addEventListener('api-write', (event) => {
  const url = String((event.detail && event.detail.url) || '').replace(/^\//, '');
  if (url.startsWith('api/declaration/')) {
    store.commit('declarations', []);
  }
});

export default store;
