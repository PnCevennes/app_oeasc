import declarationForm from "./declaration-form";
import declarationList from "./declaration-list";
import declaration from "./declaration.vue";
import { apiRequest } from "@/core/js/data/api.js";
import storeUtils from "@/store/utils";
import configResitutionDeclaration from "./config/restitution-declaration";

const ROUTE = [
  {
    path: "/declaration/declarer_en_ligne",
    label: "Créér déclaration",
    access: 1,
    name: "post_declaration",
    hideTitle: true,
    parent: "declaration.systeme_alerte",
    component: declarationForm
  },

  {
    path: "/declaration/declarer_en_ligne/:id",
    label: "Modifier déclaration",
    access: 1,
    hideTitle: true,
    parent: "declaration.liste_declarations",
    name: "patch_declaration",
    component: declarationForm
  },

  {
    path: "/declaration/liste",
    label: "Alerte signalées",
    access: 1,
    name: "declaration.liste_declarations",
    parent: "declaration.systeme_alerte",
    component: declarationList
  },

  {
    path: "/declaration/voir_declaration/:id",
    label: "Déclaration",
    access: 1,
    name: "voir_declaration",
    parent: "declaration.liste_declarations",
    component: declaration
  },

  {
    path: "/declaration/degat_grand_gibier",
    name: "declaration.degat_grand_gibier",
    content: "degat_grand_gibier",
    label: "Les dégâts de grand gibier",
    parent: "declaration.systeme_alerte",
    type: "page"
  },

  {
    path: "/declaration/systeme_alerte",
    name: "declaration.systeme_alerte",
    content: "systeme_alerte",
    label: "Le système d'alerte",
    parent: "page.accueil",
    type: "page"
  },

  {
    path: "/declaration/signaler_degat_explication",
    name: "declaration.signaler_degat_explication",
    label: "Je signale des dégâts en forêt",
    content: "signaler_degat_explication",
    parent: "declaration.systeme_alerte",
    access: 1,
    type: "page"
  },
  {
    path: "/resultats/declarations",
    name: "resultats.declarations",
    label: "Système d'alerte",
    content: "resultats.declarations",
    parent: "resultats.index",
    type: "page"
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

    foret: state => id_foret => {
      return state._foret[id_foret];
    },
    nbDeclarationsValid: (state) => {
      // depuis degats et remove doublons
      console.log('nb dec', state.degats)

      return state.degats && state.degats.filter(d => d.valide=='Validé')
        .map(d => d.id_declaration)
        .filter((id, index, self) => self.indexOf(id) == index).length || '(...chargement en cours)';
    },
    nbDegatsValid: state => {
      return state.degats && state.degats.filter(d => d.valide=='Validé').length || '(...chargement en cours)';
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
    declarationForm: ({ commit }, id) => {
      return new Promise((resolve, reject) => {
        apiRequest("GET", `api/degat_foret/declaration/${id || ""}`).then(
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

    // pb
    foretFromCode: ({ commit }, codeForet) => {
      return new Promise((resolve, reject) => {
        apiRequest("GET", `api/degat_foret/foret_from_code/${codeForet}`).then(
          apiData => {
            commit("foret", apiData);
            resolve(apiData);
          },
          error => {
            console.error(`subscribe foret error: ${error}`);
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
            console.error(`subscribe proprietaire error: ${error}`);
            reject(error);
          }
        );
      });
    }
  }
};

storeUtils.addStore(STORE, "degat", "api/declaration/degat", {
  idFieldName: "id_declaration"
});

storeUtils.addStoreRestitution(
  STORE,
  "declaration",
  "getAllDegat",
  configResitutionDeclaration
);

export { ROUTE, STORE };
