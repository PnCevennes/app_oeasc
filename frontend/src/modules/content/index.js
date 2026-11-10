import storeUtils from '@/store/utils';

import configStoreContent from './config/store-content';

// Récup«ration des  routes des actus et des commons pour les ajouter aux routes globales
const ROUTE = [
  {
    // admin
    name: 'content.admin',
    path: '/content/admin',
    label: 'Contenus',
    hideTitle: true,
    component: () => import('@/components/admin.vue'),
    props: {
      config: {
        title: 'Contenus',
        tabs: {
          content: {
            storeName: 'commonsContent',
          },
        },
      },
    },
    access: 5,
  },

  {
    path: '/actualites',
    label: 'Actualités',
    name: 'actualite.index',
    parent: 'page.accueil',
    component: () => import('./actualite.vue'),
    props: {
      typePage: 'actualite',
    },
  },
  {
    path: '/actualite/:code',
    name: 'actualite.content',
    parent: 'actualite.index',
    type: 'page',
  },
  {
    path: '/content/:code',
    label: 'content',
    name: 'content',
    component: () => import('./content.vue'),
    props: {
      page: true,
    },
  },
  {
    path: '/actualite/',
    label: 'actualite',
    name: 'actualite.new',
    parent: 'actualite.index',
    component: () => import('./content.vue'),
    props: {
      page: true,
      code: null,
      typePage: 'actualite',
    },
  },
];

const STORE = {};

// on récupère le store de content pour les ajouter au store global
storeUtils.addStore(STORE, configStoreContent);

export { ROUTE, STORE };
