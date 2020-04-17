import content from "./content";
import { apiRequest } from "@/core/js/data/api.js";

const ROUTE = [
  {
    path: "/content/:code",
    label: "content",
    name: "content",
    component: content
  }
];

const STORE = {
  state: {
    _contents: {}
  },
  getters: {
    content: state => code => {
      return state._contents[code];
    }
  },
  mutations: {
    content: (state, code, data) => {
      state._contents[code] = data;
    }
  },
  actions: {
    content: ({ getters, commit }, code) => {
      return new Promise((resolve, reject) => {
        const content = getters.content(code);
        if (content) {
          resolve(content);
        }
        apiRequest("GET", `api/commons/content/${code}`).then(
          data => {
            commit("content", code, data);
            resolve(data);
          },
          error => {
            reject(error);
          }
        );
      });
    }
  }
};

export { ROUTE, STORE, content };
