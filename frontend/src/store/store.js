/*
  Les stores sont directement ajoutés depuis modules/index.js pour les modules
  depuis /core/js/data/api.js pour la gestion des requête api vers le back
  depuis /components/form pour la gestion des formulaires.
  Si il faut en rajouter en lien avec des modules, i
*/


import Vue from 'vue';
import Vuex from 'vuex';
import { MODULES_STORE } from '@/modules';
import { STORE as API_STORE } from "@/core/js/data/api.js"
import { STORE as FORM_STORE } from "@/components/form"



Vue.use(Vuex);

const storeDefinition = {
  getters: {},
  mutations: {},
  actions: {},
  state: {}
}



const stores = [
  MODULES_STORE,
  API_STORE,
  FORM_STORE
];

for (const store of stores) {
  for (const key of Object.keys(storeDefinition)) {
    storeDefinition[key] = { ...storeDefinition[key], ... store[key] }
  }
}

let store = new Vuex.Store(storeDefinition);

export default store;
