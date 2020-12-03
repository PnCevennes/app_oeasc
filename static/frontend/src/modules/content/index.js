import storeUtils from "@/store/utils";
import content from "./content";
import actualite from "./actualite";
import { apiRequest } from "@/core/js/data/api.js";
import admin from "@/components/admin";

import configContentTable from "./config/table-content";
import configTagTable from "./config/table-tag";

const configAdmin = {
  title: "Contenu",
  tabs: {
    content: {
      config: configContentTable,
      label: "Contenus",
      type: "generic-table"
    },
    tag: {
      config: configTagTable,
      label: "Tags",
      type: "generic-table"
    }
  }
};

const ROUTE = [
  {
    path: "/content/admin",
    label: "Contenu",
    name: "content.admin",
    component: admin,
    props: {
      config: configAdmin
    }
  },
  {
    path: "/actualites",
    label: "Actualités",
    name: "actualite.index",
    parent: "page.accueil",
    component: actualite,
    props: {
      tagNames: ["actualité"]
    }
  },
  {
    path: "/actualite/:code",
    name: "actualite.content",
    parent: "actualite.index",
    type: "page"
  },
  {
    path: "/content/:code",
    label: "content",
    name: "content",
    component: content,
    props: {
      page: true,
    }
  },
  {
    path: "/actualite/",
    label: "actualite",
    name: "actualite.new",
    parent: "actualite.index",
    component: content,
    props: {
      page: true,
      code: null,
      tagNames:['actualité'] 
    }
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

storeUtils.addStore(STORE, "commonsContent", "api/generic/commons/content", {
  idFieldName: "id_content",
  displayFieldName: "code"
});
storeUtils.addStore(STORE, "commonsTag", "api/generic/commons/tag", {
  idFieldName: "id_tag",
  displayFieldName: "nom_tag"
});
export { ROUTE, STORE, content };
