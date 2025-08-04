import { apiRequest } from "@/core/js/data/api.js";
import { dataString } from "./functions";

/**
 * @namespace STORE
 * @description
 * Module Vuex pour la gestion des nomenclatures dans l'application.
 * Il contient l'état, les getters, les mutations et les actions liés aux nomenclatures.
 *
 * @property {Object} state
 *   @property {Array<Object>} _nomenclatures - Tableau contenant toutes les nomenclatures chargées.
 *
 * @property {Object} getters
 *   @property {Function} nomenclatures - Retourne toutes les nomenclatures. Utilisé pour lister ou afficher toutes les nomenclatures.
 *   @property {Function} nomenclature - Retourne une nomenclature selon son identifiant. Utilisé lors de la sélection ou l'affichage d'une nomenclature précise.
 *   @property {Function} nomenclatureFromCdNomenclature - Retourne une nomenclature selon son type et son code. Utile pour retrouver une nomenclature spécifique selon des critères.
 *   @property {Function} nomenclaturesOfType - Retourne toutes les nomenclatures d'un type donné. Utilisé pour filtrer les nomenclatures par type.
 *   @property {Function} nomenclatureString - Retourne une chaîne de caractères représentant une ou plusieurs nomenclatures selon des identifiants et une clé. Utile pour l'affichage ou la concaténation de labels.
 *
 * @property {Object} mutations
 *   @property {Function} nomenclatures - Met à jour la liste des nomenclatures dans l'état. Utilisé lors du chargement ou de la mise à jour des nomenclatures.
 *
 * @property {Object} actions
 *   @property {Function} nomenclatures - Action asynchrone pour charger les nomenclatures depuis l'API. Utilisée au démarrage de l'application ou lors du rafraîchissement des données.
 *     - Si les nomenclatures sont déjà chargées, elle retourne celles-ci.
 *     - Sinon, elle effectue une requête API, transforme les données et les enregistre dans l'état.
 */
const STORE = {
  state: {
    _nomenclatures: []
  },

  getters: {
    nomenclatures: state => state._nomenclatures,
    nomenclature: state => id_nomenclature =>
      state._nomenclatures.find(n => n.id_nomenclature === id_nomenclature),
    nomenclatureFromCdNomenclature: state => (type, cd_nomenclature) =>
      state._nomenclatures.find(
        n => n.type == type && n.cd_nomenclature === cd_nomenclature
      ),
    nomenclaturesOfType: state => type =>
      state._nomenclatures.filter(n => n.type === type),
    nomenclatureString: state => (ids, key = "label_fr") =>
      dataString(STORE, state, "nomenclature", ids, key)
  },

  mutations: {
    nomenclatures: (state, nomenclatures) => {
      state._nomenclatures = nomenclatures; 
    }
  },

  actions: {
    nomenclatures: ({ commit, getters }) => {
      return new Promise((resolve, reject) => {

        const nomenclatures = getters.nomenclatures.length;
        if (nomenclatures) {
          resolve(nomenclatures);
          return;
        }
        apiRequest("GET", "api/oeasc/nomenclatures").then(
          apiData => {
            const data = [];
            for (const nomenclatureType of Object.values(apiData).filter(
              n => !!n
            )) {
              for (const nomenclature of nomenclatureType.values) {
                nomenclature.type = nomenclatureType.mnemonique;
                data.push(nomenclature);
              }
            }
            commit("nomenclatures", data);
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

export { STORE };
