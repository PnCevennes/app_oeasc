import { defineAsyncComponent } from 'vue';
import storeUtils from '@/store/utils';
// import configStoreTag from './config/store-tag';
import configStoreObserver from './config/store-observer';
import configStoreCircuit from './config/store-circuit';
import configStoreRealisation from './config/store-realisation';

// composants disponibles dans les pages CMS (voir CONTENT plus bas) : chargés à la demande
// seulement quand une page en fait effectivement usage, pas à chaque démarrage de l'app
// (ce module est importé eagerly par modules/index.js pour construire le store Vuex central)
const inGraph = defineAsyncComponent(() => import('@/modules/in/in-graph.vue'));
const inTable = defineAsyncComponent(() => import('@/modules/in/in-table.vue'));

// route definitions

const ROUTE = [
  // {
  //   // index
  //   name: "in.index",
  //   path: "/in/index",
  //   label: "Indices nocturnes",
  //   type: "page",
  //   content: "in.index",
  //   parent: "page.accueil",
  //   access: 5
  // },

  {
    // admin
    name: 'in.admin',
    path: '/in/admin',
    label: 'Indices nocturnes ',
    // parent: "in.index",
    hideTitle: true,
    component: () => import('@/components/admin.vue'),
    props: {
      config: {
        title: 'Indice Nocturnes',
        tabs: {
          graphiques: {
            labels: 'Statistiques',
            type: 'in-table',
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
        },
      },
    },
    access: 5,
  },
  {
    // page resultats grand public
    path: '/resultats/in',
    name: 'resultats.in',
    label: 'Indices nocturnes',
    content: 'resultats.in',
    parent: 'resultats.index',
    type: 'page',
  },
  {
    // page resultats grand public (tous graphes)
    path: '/resultats/in_all',
    name: 'resultats.in2',
    label: 'Indices nocturnes',
    content: 'resultats.in_all',
    parent: 'resultats.index',
    type: 'page',
  },
];

const STORE = {};

storeUtils.addSimpleStore(STORE, 'inResults', 'api/in/results/');

storeUtils.addStore(STORE, configStoreCircuit);
storeUtils.addStore(STORE, configStoreObserver);
storeUtils.addStore(STORE, configStoreRealisation);

const CONTENT = {
  inGraph,
  inTable,
};

export { ROUTE, STORE, CONTENT };
