import Vue from 'vue';
import Vuex from 'vuex';
import { MODULES_STORE } from '@/modules';

Vue.use(Vuex);

const storeDefinition = {
  getters: {},
  mutations: {},
  actions: {},
  state: {}
}

// const stores = [MODULES_STORE, SERVICES_STORE]
const stores = [MODULES_STORE]

for (const store of stores) {
  for (const key of Object.keys(storeDefinition)) {
    storeDefinition[key] = { ...storeDefinition[key], ... store[key] }
  }
}

let store = new Vuex.Store(storeDefinition);

export default store;
