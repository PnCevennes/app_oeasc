import Vue from 'vue';
import Vuex from 'vuex';
import { MODULES_STORE } from '@/modules';
import { STORE as API_STORE } from "@/core/js/data/api.js"



Vue.use(Vuex);

const storeDefinition = {
  getters: {},
  mutations: {},
  actions: {},
  state: {}
}

const stores = [MODULES_STORE, API_STORE]
for (const store of stores) {
  for (const key of Object.keys(storeDefinition)) {
    storeDefinition[key] = { ...storeDefinition[key], ... store[key] }
  }
}



let store = new Vuex.Store(storeDefinition);

export default store;
