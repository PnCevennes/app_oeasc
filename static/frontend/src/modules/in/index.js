import inTest from "./in-test";
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
    name: "in.test",
    path: "/in/test",
    label: "Indices Nocturnes (Test)",
    parent: 'in.index',
    component: inTest
  }
];

const STORE = {
  actions: {
    in_results: () => apiRequest('GET', 'api/in/results')
  },
  getters: {

  },
  state: {

  },
  mutations: {

  }
}
export { ROUTE, STORE };
