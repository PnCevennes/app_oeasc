import storeUtils from "@/store/utils";
import admin from "@/components/admin";
import configStoreTag from './config/store-tag';
import configStoreObserver from "./config/store-observer";
import configStoreCircuit from "./config/store-circuit";
import configStoreRealisation from "./config/store-realisation";

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
          // graphiques: {
          //   label: "Statistiques",
          //   type: "in-table"
          // },
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
    name: "resultats.in",
    label: "Indices nocturnes",
    content: "resultats.in_all",
    parent: "resultats.index",
    type: "page"
  }
];

const STORE = {}

storeUtils.addSimpleStore(STORE, "inResults", "api/in/results/");

// storeUtils.addStore(STORE, "Realisation")
storeUtils.addStore(STORE, configStoreCircuit)
storeUtils.addStore(STORE, configStoreObserver)
storeUtils.addStore(STORE, configStoreTag)
storeUtils.addStore(STORE, configStoreRealisation)


export { ROUTE, STORE };
