import inTest from "./in-test";
import inTable from "./in-table";
import { apiRequest } from "@/core/js/data/api.js";


const ROUTE = [
  {
    name: "in.index",
    path: "/in/index",
    label: "Indices Nocturnes",
    type: "page",
    content: "in.index",
    parent:"page.accueil"
  },
  {
    name: "in.tableau",
    path: "/in/tableau",
    label: "Tabelau de données",
    parent: 'in.index',
    hideTitle: true,
    component: inTable
  },
  {
    name: "in.graphiques",
    path: "/in/graphiques",
    label: "Graphiques",
    parent: 'in.index',
    component: inTest
  }
];

const STORE = {
  actions: {
    in_results: () => apiRequest('GET', 'api/in/results/')
  },
  getters: {

  },
  state: {

  },
  mutations: {

  }
}
export { ROUTE, STORE };
