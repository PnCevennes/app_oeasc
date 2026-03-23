import storeUtils from '@/store/utils.js';
import admin from '@/components/admin.vue';
import configStoreSecteur from './config/store-secteur.js';
import configStoreEspece from './config/store-espece.js';
import configStoreNomenclature from './config/store-nomenclature.js';
import configStoreNomenclatureType from './config/store-nomenclature-type.js';

/**
 * @constant {Array<Object>} ROUTE
 * @description
 * Tableau contenant la configuration des routes pour le module "commons".
 * Chaque objet représente une route spécifique avec ses propriétés :
 *
 * - name : Nom unique de la route, utilisé pour l'identification interne.
 * - path : Chemin URL associé à la route.
 * - label : Libellé affiché pour la route dans l'interface utilisateur.
 * - hideTitle : Booléen indiquant si le titre doit être masqué dans l'affichage.
 * - component : Composant Vue.js à rendre pour cette route.
 * - props : Propriétés passées au composant, incluant la configuration :
 *    - config : Objet de configuration contenant :
 *        - title : Titre affiché dans le composant.
 *        - tabs : Liste des onglets disponibles, chacun avec :
 *            - storeName : Nom du store Vuex associé à l'onglet.
 * - access : Niveau d'accès requis pour afficher la route (ici 5 = admin).
 */
const ROUTE = [
  {
    // admin
    name: 'commons.admin',
    path: '/commons/admin',
    label: 'Données commons',
    hideTitle: true,
    component: admin,
    props: {
      config: {
        title: 'Commons',
        tabs: {
          nomenclature: {
            storeName: 'commonsNomenclature',
          },
          nomenclatureType: {
            storeName: 'commonsNomenclatureType',
          },
          secteur: {
            storeName: 'commonsSecteur',
          },
          espece: {
            storeName: 'commonsEspece',
          },
        },
      },
    },
    access: 5,
  },
];

const STORE = {};
storeUtils.addStore(STORE, configStoreEspece);
storeUtils.addStore(STORE, configStoreSecteur);
storeUtils.addStore(STORE, configStoreNomenclature);
storeUtils.addStore(STORE, configStoreNomenclatureType);

export { ROUTE, STORE };
