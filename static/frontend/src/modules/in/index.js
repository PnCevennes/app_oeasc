import inTest from "./in-test";
import inTable from "./in-table";
import genericForm from "@/components/form/generic-form";
import genericTable from "@/components/table/generic-table";
import configRealisationForm from "./config/form-realisation";
import configRealisationTable from "./config/table-realisation";
import { apiRequest } from "@/core/js/data/api.js";
import storeUtils from '@/store/utils';


const ROUTE = [
  {
    name: "in.index",
    path: "/in/index",
    label: "Indices nocturnes",
    type: "page",
    content: "in.index",
    parent: "page.accueil",
    access: 5
  },
  {
    name: "in.resultats",
    path: "/in/resultats",
    label: "Résultats",
    type: "page",
    content: "in.resultats",
    parent: "in.index",
    access: 5
  },
  {
    name: "in.tableau",
    path: "/in/tableau",
    label: "In - Tableau de données",
    parent: "in.index",
    hideTitle: true,
    component: inTable,
    access: 5
  },
  {
    name: "in.realisation",
    path: "/in/realisation/:id?",
    label: "In - Réalisation",
    parent: "in.index",
    hideTitle: true,
    component: genericForm,
    props: {config: configRealisationForm},
    access: 5,
  },

  {
    name: "in.realisations",
    path: "/in/realisations",
    label: "In - Réalisations",
    parent: "in.index",
    hideTitle: true,
    component: genericTable,
    props: {config: configRealisationTable},
    access: 5,
  },

  {
    name: "in.graphiques",
    path: "/in/graphiques",
    label: "Graphiques",
    parent: "in.index",
    component: inTest,
    access: 5
  },
  {
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

storeUtils.addStore(STORE, 'inRealisation', 'api/generic/in/realisation', 'id_realisation');
storeUtils.addStore(STORE, 'inCircuit', 'api/generic/in/circuit', 'id_circuit');

export { ROUTE, STORE };
