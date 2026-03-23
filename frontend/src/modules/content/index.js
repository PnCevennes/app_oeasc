import storeUtils from '@/store/utils';
import content from './content';
import actualite from './actualite';
// import { apiRequest } from "@/core/js/data/api.js";
import admin from '@/components/admin';

import configStoreTag from './config/store-tag';
import configStoreContent from './config/store-content';

// Récup«ration des  routes des actus et des commons pour les ajouter aux routes globales
const ROUTE = [
  {
    // admin
    name: 'content.admin',
    path: '/content/admin',
    label: 'Contenus',
    hideTitle: true,
    component: admin,
    props: {
      config: {
        title: 'Contenus',
        tabs: {
          content: {
            storeName: 'commonsContent',
          },
          tag: {
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
    component: actualite,
    props: {
      tagNames: ['actualité'],
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
    component: content,
    props: {
      page: true,
    },
  },
  {
    path: '/actualite/',
    label: 'actualite',
    name: 'actualite.new',
    parent: 'actualite.index',
    component: content,
    props: {
      page: true,
      code: null,
      tagNames: ['actualité'],
    },
  },
];

const STORE = {};

// on récupère les stores de content et tag pour les ajouter au store global
storeUtils.addStore(STORE, configStoreContent);
storeUtils.addStore(STORE, configStoreTag);

export { ROUTE, STORE, content };
