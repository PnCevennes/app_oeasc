import storeUtils from '@/store/utils';
import { apiRequest } from "@/core/js/data/api.js";

// import inTest from "./in-test";
// import inTable from "./in-table";
import inAdmin from "./in-admin";

// import genericTable from "@/components/table/generic-table";
// import configRealisationTable from "./config/table-realisation";
// import configCircuitTable from "./config/table-circuit";
// import configSecteurTable from "./config/table-secteur";

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
  },  {
    // index
    name: "in.admin",
    path: "/in/admin",
    label: "In - administration",
    parent: "in.index",
    hideTitle: true,
    component: inAdmin,
    access: 5,
  }, {
    // resultats (public)
    name: "in.resultats",
    path: "/in/resultats",
    label: "Résultats",
    type: "page",
    content: "in.resultats",
    parent: "in.index",
    access: 5
  }, 
  // {
  //   // resultat (admin)
  //   name: "in.tableau",
  //   path: "/in/tableau",
  //   label: "In - Analyse des données",
  //   parent: "in.index",
  //   hideTitle: true,
  //   component: inTable,
  //   access: 5
  //  },
   // {
  //   // test graphiques (admin)
  //   name: "in.graphiques",
  //   path: "/in/graphiques",
  //   label: "Graphiques",
  //   parent: "in.index",
  //   component: inTest,
  //   access: 5
  // }, 
  {
    // page resultats ??
    path: "/resultats/in",
    name: "resultats.in",
    label: "Indices nocturnes",
    content: "resultats.in",
    parent: "resultats.index",
    type: "page"
  }

];

const STORE = {
  actions: {
    inResults: () => apiRequest("GET", "api/in/results/"),
  },
  getters: {},
  state: {},
  mutations: {}
};

storeUtils.addStore(STORE, 'inRealisation', 'api/generic/in/realisation', {idFieldName: 'id_realisation'});
storeUtils.addStore(STORE, 'inCircuit', 'api/generic/in/circuit', {idFieldName: 'id_circuit', displayFieldName: 'nom_circuit'});
storeUtils.addStore(STORE, 'inSecteur', 'api/generic/in/secteur', {idFieldName: 'id_secteur', displayFieldName: 'nom_secteur'});
storeUtils.addStore(STORE, 'inObserver', 'api/generic/in/observer', {idFieldName: 'id_observer', displayFieldName: 'nom_observer'});
storeUtils.addStore(STORE, 'inTag', 'api/generic/in/tag', {idFieldName: 'id_tag', displayFieldName: 'nom_tag'});
storeUtils.addStore(STORE, 'inEspece', 'api/generic/in/espece', {idFieldName: 'id_espece', displayFieldName: 'nom_espece'});


export { ROUTE, STORE };
