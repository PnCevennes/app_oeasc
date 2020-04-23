import declarationForm from "./declaration-form";
import declarationList from "./declaration-list";
import declaration from "./declaration.vue";
import { apiRequest } from "@/core/js/data/api.js";

const ROUTE = [
  {
    path: "/declaration/declarer_en_ligne",
    label: "declarer_en_ligne",
    access: 1,
    name: "post_declaration",
    hideTitle: true,
    component: declarationForm
  },

  {
    path: "/declaration/declarer_en_ligne/:idDeclaration",
    label: "declarer_en_ligne",
    access: 1,
    hideTitle: true,
    name: "patch_declaration",
    component: declarationForm
  },

  {
    path: "/declaration/liste",
    label: "Alerte déclarées",
    access: 1,
    name: "declaration.liste_declarations",
    component: declarationList
  },

  {
    path: "/declaration/voir_declaration/:idDeclaration",
    label: "voir_declaration",
    access: 1,
    name: "voir_declaration",
    component: declaration
  }
];

const STORE = {
  state: {
    _configDeclaration: {},
    _declarationForm: {},
    _declarations: [],
    _foret: {},
    _declarationTableHeight: null
  },

  getters: {
    declarationTableHeight: state => state._declarationTableHeight,

    configDeclaration: state => {
      return state._configDeclaration;
    },

    declarationForm: state => {
      return state._declarationForm;
    },

    declarations: state => {
      return state._declarations;
    },

    foret: id_foret => state => {
      return state._foret[id_foret];
    }
  },

  mutations: {
    declarationTableHeight: (state, h) => {
      state._declarationTableHeight = h;
    },

    configDeclaration: (state, configDeclaration) => {
      state._configDeclaration = configDeclaration;
    },

    declarationForm: (state, declarationForm) => {
      state._declarationForm = declarationForm;
      state._declarations = [];
    },

    declarations: (state, declarations) => {
      state._declarations = declarations;
    },

    foret: (state, foret) => {
      state._foret[foret.id_foret] = foret;
    }
  },

  actions: {
    declarationForm: ({ commit }, idDeclaration) => {
      return new Promise((resolve, reject) => {
        apiRequest(
          "GET",
          `api/degat_foret/declaration/${idDeclaration || ""}`
        ).then(
          apiData => {
            commit("declarationForm", apiData);
            resolve(apiData);
          },
          error => {
            commit("declarationForm", {});
            reject(error);
          }
        );
      });
    },

    declarations: ({ state, commit }) => {
      return new Promise((resolve, reject) => {
        if (state._declarations.length) {
          resolve(state._declarations);
          return;
        }
        apiRequest("GET", `api/declaration/declarations`).then(
          apiData => {
            commit("declarations", apiData);
            resolve(apiData);
          },
          error => {
            commit("declarations", []);
            reject(error);
          }
        );
      });
    },

    foretFromCode: ({ commit }, codeForet) => {
      return new Promise((resolve, reject) => {
        apiRequest("GET", `api/degat_foret/foret_from_code/${codeForet}`).then(
          apiData => {
            commit("foret", apiData);
            resolve(apiData);
          },
          error => {
            console.log(`subscribe foret error: ${error}`);
            reject(error);
          }
        );
      });
    },

    proprietaireFromIdDeclarant: ({ commit }, idDeclarant) => {
      return new Promise((resolve, reject) => {
        apiRequest(
          "GET",
          `api/degat_foret/proprietaire_from_id_declarant/${idDeclarant}`
        ).then(
          apiData => {
            commit;
            resolve(apiData);
          },
          error => {
            console.log(`subscribe proprietaire error: ${error}`);
            reject(error);
          }
        );
      });
    }
  }
};

export { ROUTE, STORE };
