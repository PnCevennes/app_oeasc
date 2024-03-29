import storeUtils from "@/store/utils";
import admin from "@/components/admin";
import configStoreTag from './config/store-tag';
import configStoreObserver from "./config/store-observer";
import configStoreCircuit from "./config/store-circuit";
import configStoreRealisation from "./config/store-realisation";
import inGraph from "@/modules/in/in-graph.vue";
import inTable from "@/modules/in/in-table.vue";

// route definitions

const ROUTE = [
  {
    // index
    name: "in.index",
    path: "/in/index",
    label: "Indices nocturnes",
    type: "page",
    content: "in.index",
    parent: "page.accueil",
    access: 5
  },
  {
    // admin
    name: "in.admin",
    path: "/in/admin",
    label: "Indices nocturnes ",
    // parent: "in.index",
    hideTitle: true,
    component: admin,
    props: {
      config: {
        title: "Indice Nocturnes",
        tabs: {
          graphiques: {
            labels: "Statistiques",
            type: "in-table"
          },
          realisation: {
            storeName: 'inRealisation',
          },
          circuit: {
            storeName: 'inCircuit',
          },
          observer: {
            storeName: 'inObserver',
          },
          tag: {
            storeName: 'inTag',
          },
        }      
      }
    },
    access: 5
  },
  {
    // page resultats grand public
    path: "/resultats/in",
    name: "resultats.in",
    label: "Indices nocturnes",
    content: "resultats.in",
    parent: "resultats.index",
    type: "page"
  },
  {
    // page resultats grand public (tous graphes)
    path: "/resultats/in_all",
    name: "resultats.in2",
    label: "Indices nocturnes",
    content: "resultats.in_all",
    parent: "resultats.index",
    type: "page"
  }
];

const STORE = {}

storeUtils.addSimpleStore(STORE, "inResults", "api/in/results/");

storeUtils.addStore(STORE, configStoreCircuit)
storeUtils.addStore(STORE, configStoreObserver)
storeUtils.addStore(STORE, configStoreTag)
storeUtils.addStore(STORE, configStoreRealisation)

const CONTENT = {
  inGraph, inTable
}

export { ROUTE, STORE, CONTENT };
