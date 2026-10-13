import storeUtils from '@/store/utils.js'; // pour importer addStore qui construit les states, mutations, actions et getters

// Import des fichiers de configuration des stores
import configStoreDeclaration from './config/store-declaration.js';
import configStoreSaison from './config/store-saison.js';
import configStoreCulture from './config/store-culture.js';
import configStoreTypeCulture from './config/store-type-culture.js';
import configStoreUgAgricole from './config/store-ug-agricole.js';
import configStoreCommune from './config/store-commune.js';

const ROUTE = [
  {
    name: 'degats_agricoles.restitution_gd_public',
    path: '/degats_agricoles/restitution_gd_public',
    label: 'Dégâts agricoles',
    hideTitle: true, // True => cache le bandeau header pour plus de place
    component: () => import('./page-degats-agricoles.vue'),
    parent: 'resultats.index', // définit la place dans le menu. Ici dans "resultats des suivis"
    // pas de `access` : page publique, accessible sans être connecté
  },

  {
    name: 'degats_agricoles.imports',
    path: '/degats_agricoles/imports',
    label: 'Importation dégâts agricoles', // titre dans le menu (Administration)
    hideTitle: true, // True => cache le bandeau header pour plus de place
    component: () => import('./imports-degats-agricoles.vue'),
    access: 5, // droit d'accès minimum
  },

  {
    // Route vers les tableaux des données de dégâts agricoles
    name: 'degats_agricoles.admin',
    path: '/degats_agricoles/admin',
    label: 'Données dégâts agricoles', // titre dans le menu (Administration)
    hideTitle: true,
    component: () => import('@/components/admin.vue'), // composant générique : un generic-table par onglet
    props: {
      config: {
        // titre affiché en haut de page suivi de "- Page d'administration"
        title: 'Données dégâts agricoles',
        tabs: {
          declaration_tab: {
            storeName: 'agricoleDeclaration',
            labels: 'Déclaration dégâts',
          },
          saison_tab: {
            storeName: 'agricoleSaison',
            labels: 'Saisons',
          },
          culture_tab: {
            storeName: 'agricoleCulture',
            labels: 'Cultures',
          },
          typeCulture_tab: {
            storeName: 'agricoleTypeCulture',
            labels: 'Types de culture',
          },
          ugAgricole_tab: {
            storeName: 'agricoleUgAgricole',
            labels: 'Unités de gestion',
          },
        },
      },
    },
    access: 5,
  },
];

const STORE = {};

// Ajout des configStore en fonction des fichiers dans config
storeUtils.addStore(STORE, configStoreDeclaration);
storeUtils.addStore(STORE, configStoreSaison);
storeUtils.addStore(STORE, configStoreCulture);
storeUtils.addStore(STORE, configStoreTypeCulture);
storeUtils.addStore(STORE, configStoreUgAgricole);
storeUtils.addStore(STORE, configStoreCommune);

export { ROUTE, STORE };
