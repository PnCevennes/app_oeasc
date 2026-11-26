import storeUtils from '@/store/utils';
import configResitutionDeclaration from './config/restitution-declaration';
import configStoreDegat from './config/store-degat';

import { DROITS } from '@/config/droits.js';
const ROUTE = [
  {
    path: '/declaration/declarer_en_ligne',
    label: 'Créér déclaration',
    access: DROITS.CONNECTE,
    name: 'nouvelle_declaration',
    hideTitle: true,
    parent: 'declaration.systeme_alerte',
    component: () => import('./modifier-declaration.vue'),
  },

  {
    path: '/declaration/modifier_declaration',
    label: 'Modifier déclaration',
    access: DROITS.CONNECTE,
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
    name: 'declaration.relances_auto',
    path: '/declaration/relances-auto',
    label: 'Relances automatiques', // titre dans le menu (Administration)
    hideTitle: true,
    component: () => import('./relances-auto.vue'),
    access: DROITS.ANIMATEUR, // garde de redirection (App.vue checkRigths)
    hidden: ({ $store }) => $store.getters.droitMax < DROITS.ANIMATEUR,
  },

  {
    path: '/declaration/liste',
    label: 'Alerte signalées',
    access: DROITS.CONNECTE,
    name: 'declaration.liste_declarations',
    parent: 'declaration.systeme_alerte',
    component: () => import('./declaration-liste.vue'),
  },

  {
    path: '/declaration/voir_declaration/:id', // nouvelle vertion de voir_declaration. Supprimer l'anctienne quand c'est finit
    label: 'Déclaration',
    access: DROITS.CONNECTE,
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
    access: DROITS.CONNECTE,
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

const STORE = { state: {}, getters: {}, mutations: {}, actions: {} };

// liste des déclarations : mise en cache par TanStack Query (clé ['simple', url]) et invalidée
// automatiquement par toute écriture sur api/declaration/* (cf. store/store.js)
storeUtils.addSimpleStore(STORE, 'declarations', 'api/declaration/declarations');

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
