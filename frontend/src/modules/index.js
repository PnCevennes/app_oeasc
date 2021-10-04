import { ROUTE as user_routes, STORE as user_store } from "./user";
import { ROUTE as commons_routes, STORE as commons_store } from "./commons";
import { ROUTE as in_routes, STORE as in_store } from "./in";
import { ROUTE as chasse_routes, STORE as chasse_store } from "./chasse";
import { STORE as data_store } from "./data";

import { ROUTE as content_routes, STORE as content_store } from "./content";
import { ROUTE as declaration_routes, STORE as declaration_store} from "./declaration";
import { ROUTE as test_routes } from "./test";
import { ROUTE as restitution_routes, STORE as restitution_store } from "./restitution";
import { ROUTE as restitution2_routes, STORE as restitution2_store } from "./restitution2";
import { ROUTE as page_routes } from "./page";
import { STORE as map_store } from "./map";

const MODULES_ROUTES = [
  ...user_routes,
  ...in_routes,
  ...commons_routes,
  ...chasse_routes,
  ...content_routes,
  ...declaration_routes,
  ...test_routes,
  ...page_routes,
  ...restitution_routes,
  ...restitution2_routes,
];




const stores = [
  user_store,
  commons_store,
  in_store,
  chasse_store,
  data_store,
  map_store,
  declaration_store,
  content_store,
  restitution_store,
  restitution2_store,
];

const MODULES_STORE = {
  getters: {},
  mutations: {},
  actions: {},
  state: {}
};

for (const store of stores) {
  for (const key of Object.keys(MODULES_STORE)) {
    MODULES_STORE[key] = { ...MODULES_STORE[key], ...store[key] };
  }
}

export { MODULES_ROUTES, MODULES_STORE };
