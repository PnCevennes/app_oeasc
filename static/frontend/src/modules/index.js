import { ROUTE as content_routes } from './content';
import { ROUTE as user_routes, STORE as user_store } from './user';
import { ROUTE as declaration_routes, STORE as declaration_store } from './declaration'
import { STORE as data_store } from './data'
import { ROUTE as test_routes } from './test'
import { STORE as map_store } from './map'

const MODULES_ROUTES = [...content_routes, ...user_routes, ...declaration_routes, ...test_routes];

const stores = [user_store, data_store, map_store, declaration_store]

const MODULES_STORE = {
  getters: {},
  mutations: {},
  actions: {},
  state: {}
}

for (const store of stores) {
  for (const key of Object.keys(MODULES_STORE)) {
    MODULES_STORE[key] = { ...MODULES_STORE[key], ... store[key] }
  }
}

export { MODULES_ROUTES, MODULES_STORE };
