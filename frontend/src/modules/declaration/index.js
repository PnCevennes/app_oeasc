import { apiRequest } from '@/core/js/data/api.js';
import storeUtils from '@/store/utils';
import configResitutionDeclaration from './config/restitution-declaration';
import configStoreDegat from './config/store-degat';

const ROUTE = [
  {
    path: '/declaration/declarer_en_ligne',
    label: 'Créér déclaration',
    access: 1,
    name: 'nouvelle_declaration',
    hideTitle: true,
    parent: 'declaration.systeme_alerte',
    component: () => import('./modifier-declaration.vue'),
  },

  {
    path: '/declaration/modifier_declaration',
    label: 'Modifier déclaration',
    access: 1,
    hideTitle: true,
    parent: 'declaration.liste_declarations',
    name: 'modifier_declaration',
    component: () => import('./modifier-declaration.vue'),
  },

  // pas de access ici car l'identification se fait via un token
  {
    path: '/declaration/actualisation_declaration',
    label: 'Actualisation déclaration',
    hideTitle: true,
    parent: 'declaration.liste_declarations',
    name: 'actualisation_declaration',
    component: () => import('./modifier-declaration.vue'),
  },

  {
    path: '/declaration/liste',
    label: 'Alerte signalées',
    access: 1,
    name: 'declaration.liste_declarations',
    parent: 'declaration.systeme_alerte',
    component: () => import('./declaration-liste.vue'),
  },

  {
    path: '/declaration/voir_declaration/:id', // nouvelle vertion de voir_declaration. Supprimer l'anctienne quand c'est finit
    label: 'Déclaration',
    access: 1,
    name: 'voir_declaration',
    parent: 'declaration.liste_declarations',
    component: () => import('./voir_declaration.vue'),
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
    large: true, // page contenant des graphiques, a besoin de plus de largeur que la colonne de lecture par défaut
  },
];

const STORE = {
  state: {
    _declarations: [],
  },

  getters: {

    declarations: (state) => {
      return state._declarations;
    },

    //   // depuis degats et remove doublons
    //   return (
    //     (state.declarationDegats &&
    //       state.declarationDegats
    //         .filter((d) => d.valide == 'Validé')
    //         .map((d) => d.id_declaration)
    //         .filter((id, index, self) => self.indexOf(id) == index).length) ||
    //     '(...chargement en cours)'
    //   return (
    //     (state.declarationDegats &&
    //       state.declarationDegats.filter((d) => d.valide == 'Validé').length) ||
    //     '(...chargement en cours)'
  },

  mutations: {

    declarations: (state, declarations) => {
      state._declarations = declarations;
    },

  },

  actions: {
    // récupère les données sur une déclaration et l'enregistre en cache dans le state _declarationForm

    declarations: ({ state, commit }) => {
      return new Promise((resolve, reject) => {
        if (state._declarations.length) {
          resolve(state._declarations);
          return;
        }
        apiRequest('GET', `api/declaration/declarations`).then(
          (apiData) => {
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
