/*
          Centralise les routes et les stores de tous les modules pour qu'ils soient accessibles depuis le store principal et le router principal
          MODULES_ROUTES, MODULES_STORE contiennent respectivement les routes et les stores de tous les modules
          MODULES_ROUTES et MODULES_STORE sont ensuite récépéré dans store/store.js et router/index.js pour être accessibles partout

          il suffit ici juste d'importer les routes ou les store et de les ajouter dans MODULES_ROUTES et stores

*/



// récupération des routes il fauda ensuite ajouter les nom à MODULES_ROUTES
import { ROUTE as user_routes, STORE as user_store } from "./user";
import { ROUTE as commons_routes, STORE as commons_store } from "./commons";
import { ROUTE as in_routes, STORE as in_store } from "./in";
import { ROUTE as chasse_routes, STORE as chasse_store } from "./chasse";
import { ROUTE as icia_routes } from "./icia";
import { ROUTE as degats_agricoles_routes } from "./degats_agricoles";
import { ROUTE as sylviculture_routes } from "./sylviculture";
import { ROUTE as content_routes, STORE as content_store } from "./content";
import { ROUTE as declaration_routes, STORE as declaration_store} from "./declaration";
import { ROUTE as test_routes } from "./test";
import { ROUTE as restitution_routes, STORE as restitution_store } from "./restitution";
import { ROUTE as restitution2_routes, STORE as restitution2_store } from "./restitution2";
import { ROUTE as page_routes } from "./page";



import { STORE as data_store } from "./data";
import { STORE as map_store } from "@/components/map";





// centralise toutes les routes récupérée dans les import dans une seule liste
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
  ...icia_routes,
  ...degats_agricoles_routes,
  ...sylviculture_routes
];



// Centralise toutes les stores récupérées dans les import dans une seule liste
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

// initialise MODULES_STORE avec des dict vides
const MODULES_STORE = {
  getters: {},
  mutations: {},
  actions: {},
  state: {}
};

// Pour chaque module, on ajoute ses store dans MODULES_STORE
for (const store of stores) {
  for (const key of Object.keys(MODULES_STORE)) {
    MODULES_STORE[key] = { ...MODULES_STORE[key], ...store[key] };
  }
}

// exporte les routes et les stores
export { MODULES_ROUTES, MODULES_STORE };
