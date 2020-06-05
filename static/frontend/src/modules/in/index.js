import inTest from "./in-test";
import inTable from "./in-table";
import inForm from "./in-form";
import { apiRequest } from "@/core/js/data/api.js";

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
    name: "in.tableau",
    path: "/in/tableau",
    label: "Tableau de données",
    parent: "in.index",
    hideTitle: true,
    component: inTable,
    access: 5
  },
  {
    name: "in.saisie",
    path: "/in/saisie/:idRealisation",
    label: "Saisie",
    parent: "in.index",
    hideTitle: true,
    component: inForm,
    access: 5
  },
  {
    name: "in.saisie_new",
    path: "/in/saisie/",
    label: "Saisie",
    parent: "in.index",
    hideTitle: true,
    component: inForm,
    access: 5
  },
  {
    name: "in.graphiques",
    path: "/in/graphiques",
    label: "Graphiques",
    parent: "in.index",
    component: inTest,
    access: 5
  }
];

const STORE = {
  actions: {
    in_results: () => apiRequest("GET", "api/in/results/"),
    in_realisation: ({ getters }, idRealisation) => {
      getters;
      return apiRequest("GET", `api/in/realisation/${idRealisation}`);
    }
  },
  getters: {},
  state: {},
  mutations: {}
};
export { ROUTE, STORE };
