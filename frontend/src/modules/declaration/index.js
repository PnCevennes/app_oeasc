// import declarationForm from "./declaration-form.vue";
import modifier_declaration from './modifier-declaration.vue';
// import declarationList from './declaration-list';
// import declaration from './declaration.vue';
import { apiRequest } from '@/core/js/data/api.js';
import storeUtils from '@/store/utils';
import configResitutionDeclaration from './config/restitution-declaration';
import configStoreDegat from './config/store-degat';
import voir_declaration from './voir_declaration.vue';

import declarationListe from './declaration-liste.vue';

const ROUTE = [
  {
    path: '/declaration/declarer_en_ligne',
    label: 'Créér déclaration',
    access: 1,
    name: 'post_declaration',
    hideTitle: true,
    parent: 'declaration.systeme_alerte',
    // component: declarationForm
    component: modifier_declaration,
  },

  {
    path: '/declaration/declarer_en_ligne/:id',
    label: 'Modifier déclaration',
    access: 1,
    hideTitle: true,
    parent: 'declaration.liste_declarations',
    name: 'patch_declaration',
    // component: declarationForm
    component: modifier_declaration,
  },

  {
    path: '/declaration/modifier_declaration/:id',
    label: 'Modifier déclaration',
    access: 1,
    hideTitle: true,
    parent: 'declaration.liste_declarations',
    name: 'modifier_declaration',
    component: modifier_declaration,
  },

  // {
  //   path: '/declaration/liste',
  //   label: 'Alerte signalées',
  //   access: 1,
  //   name: 'declaration.liste_declarations',
  //   parent: 'declaration.systeme_alerte',
  //   component: declarationList,
  // },

  // remplacera la version au dessus lorsque ce sera terminé.
  {
    path: '/declaration/liste',
    label: 'Alerte signalées',
    access: 1,
    name: 'declaration.liste_declarations',
    parent: 'declaration.systeme_alerte',
    component: declarationListe,
  },

  // {
  //   path: '/declaration/voir_declaration/:id', // ancienne version. A supprimer quand celle d'en dessous sera fonctionnelle
  //   label: 'Déclaration',
  //   access: 1,
  //   name: 'voir_declaration',
  //   parent: 'declaration.liste_declarations',
  //   component: declaration,
  // },

  {
    path: '/declaration/voir_declaration/:id', // nouvelle vertion de voir_declaration. Supprimer l'anctienne quand c'est finit
    label: 'Déclaration',
    access: 1,
    name: 'voir_declaration',
    parent: 'declaration.liste_declarations',
    component: voir_declaration,
  },

  {
    path: '/declaration/degat_grand_gibier',
    name: 'declaration.degat_grand_gibier',
    content: 'degat_grand_gibier',
    label: 'Les dégâts de grand gibier',
    parent: 'declaration.systeme_alerte',
    type: 'page',
  },

  {
    path: '/declaration/systeme_alerte',
    name: 'declaration.systeme_alerte',
    content: 'systeme_alerte',
    label: "Le système d'alerte",
    parent: 'page.accueil',
    type: 'page',
  },

  {
    path: '/declaration/signaler_degat_explication',
    name: 'declaration.signaler_degat_explication',
    label: 'Je signale des dégâts en forêt',
    content: 'signaler_degat_explication',
    parent: 'declaration.systeme_alerte',
    access: 1,
    type: 'page',
  },
  {
    path: '/resultats/declarations',
    name: 'resultats.declarations',
    label: "Système d'alerte",
    content: 'resultats.declarations',
    parent: 'resultats.index',
    type: 'page',
  },
];

const STORE = {
  state: {
    _configDeclaration: {},
    _declarationForm: {},
    _declarations: [],
    _foret: {},
    _declarationTableHeight: null,
  },

  getters: {
    declarationTableHeight: (state) => state._declarationTableHeight,

    configDeclaration: (state) => {
      return state._configDeclaration;
    },

    declarationForm: (state) => {
      return state._declarationForm;
    },

    declarations: (state) => {
      return state._declarations;
    },

    foret: (state) => (id_foret) => {
      return state._foret[id_foret];
    },
    nbDeclarationsValid: (state) => {
      // depuis degats et remove doublons
      return (
        (state.declarationDegats &&
          state.declarationDegats
            .filter((d) => d.valide == 'Validé')
            .map((d) => d.id_declaration)
            .filter((id, index, self) => self.indexOf(id) == index).length) ||
        '(...chargement en cours)'
      );
    },
    nbDegatsValid: (state) => {
      return (
        (state.declarationDegats &&
          state.declarationDegats.filter((d) => d.valide == 'Validé').length) ||
        '(...chargement en cours)'
      );
    },
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
    },
  },

  actions: {
    // récupère les données sur une déclaration et l'enregistre en cache dans le state _declarationForm
    declarationForm: ({ commit }, id) => {
      return new Promise((resolve, reject) => {
        apiRequest('GET', `api/declaration/declaration/${id || ''}`).then(
          (apiData) => {
            commit('declarationForm', apiData);
            resolve(apiData);
          },
          (error) => {
            commit('declarationForm', {});
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
        apiRequest('GET', `api/declaration/declarations`).then(
          (apiData) => {
            console.log('Données des déclarations reçues :', apiData);
            commit('declarations', apiData);
            resolve(apiData);
          },
          (error) => {
            commit('declarations', []);
            reject(error);
          }
        );
      });
    },

    // pb
    foretFromCode: ({ commit }, codeForet) => {
      return new Promise((resolve, reject) => {
        apiRequest('GET', `api/declaration/foret_from_code/${codeForet}`).then(
          (apiData) => {
            commit('foret', apiData);
            resolve(apiData);
          },
          (error) => {
            console.error(`subscribe foret error: ${error}`);
            reject(error);
          }
        );
      });
    },

    proprietaireFromIdDeclarant: ({ commit }, idDeclarant) => {
      return new Promise((resolve, reject) => {
        apiRequest('GET', `api/declaration/proprietaire_from_id_declarant/${idDeclarant}`).then(
          (apiData) => {
            commit;
            resolve(apiData);
          },
          (error) => {
            console.error(`subscribe proprietaire error: ${error}`);
            reject(error);
          }
        );
      });
    },

    proprietaireFromId: ({ commit }, idProprietaire) => {
      return new Promise((resolve, reject) => {
        apiRequest('GET', `api/declaration/proprietaire_from_id/${idProprietaire}`).then(
          (apiData) => {
            commit;
            resolve(apiData);
          },
          (error) => {
            console.error(`subscribe proprietaire error: ${error}`);
            reject(error);
          }
        );
      });
    },
  },
};

storeUtils.addStore(STORE, configStoreDegat);

storeUtils.addStoreRestitution(
  STORE,
  'declaration',
  'getAllDeclarationDegat',
  configResitutionDeclaration
);

// mettre ici les composants spécifiques aux déclarations qui pourraient être utilisés dans les pages dynamiques.
const CONTENT = {};

export { ROUTE, STORE, CONTENT };
