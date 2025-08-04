import { apiRequest } from "@/core/js/data/api.js";

// Définition de l'objet STORE utilisé comme module Vuex pour la gestion du cache des données API
const STORE = {
  state: {
    // _cache : objet utilisé pour stocker les données mises en cache
    _cache: {}
  },
  mutations: {
    /**
     * setCache
     * Mutation utilisée pour enregistrer des données dans le cache.
     * cacheKeys : tableau de clés pour accéder à la bonne profondeur dans l'objet _cache (ex: ["nomenclature", "TYPE_SITE"])
     * data : données à stocker
     * Utilisée lors de la réception de nouvelles données depuis l'API, généralement appelée dans l'action cacheOrRequest.
     */
    setCache: (state, cacheKeys, data) => {
      let cur = state._cache;
      for (const [i, key] in cacheKeys.entries()) {
        // Si on est sur le dernier élément du tableau de clés, on stocke la donnée
        if (i === cacheKeys.length - 1) {
          cur[key] = data;
          return;
        }
        // Sinon, on descend dans l'objet, ou on crée un nouvel objet si nécessaire
        cur = cur[key] || {};
      }
    }
  },
  getters: {
    /**
     * getFromCache
     * Getter permettant de récupérer une donnée depuis le cache à partir d'un tableau de clés.
     * cacheKeys : tableau de clés pour accéder à la donnée
     * Utilisé pour vérifier si une donnée est déjà présente dans le cache avant de faire une requête API.
     */
    getFromCache: state => cacheKeys => {
      let cur = state._cache;
      for (const key of cacheKeys) {
        cur = cur[key];
        if (!cur) {
          // Si la donnée n'existe pas, on retourne undefined
          return;
        }
        return cur;
      }
    }
    
  },

  actions: {
    /**
     * cacheOrRequest
     * Action permettant de récupérer une donnée soit depuis le cache, soit via une requête API.
     * - Si la donnée est présente dans le cache, elle est retournée immédiatement.
     * - Sinon, une requête API est effectuée, la donnée est mise en cache puis retournée.
     * Utilisée lors de l'accès à des données qui peuvent être mises en cache pour éviter des appels API inutiles.
     * 
     * @param {Object} context - contexte Vuex (commit, getters)
     * @param {Object} params - paramètres de la requête (url, method, postData, cacheKeys, dataKeys)
     * @returns {Promise} - résout avec la donnée demandée
     */
    cacheOrRequest: (
      { commit, getters },
      { url, method = "GET", postData = null, cacheKeys, dataKeys = [] }
    ) => {
      // Vérifie si la donnée est déjà présente dans le cache
      return new Promise((resolve, reject) => {
        cacheKeys = cacheKeys || [url];
        const cacheData = getters.getFromCache(cacheKeys);
        if (cacheData) {
          resolve(cacheData);
        }

        // Si non présente, effectue la requête API et stocke le résultat dans le cache
        apiRequest(method, url, { postData }, {commit, getters}).then(
          apiData => {
            let curData = apiData;
            // Permet d'extraire une sous-partie de la réponse API si dataKeys est renseigné
            for (const key of dataKeys) {
              curData = curData[key];
            }
            commit("setCache", cacheKeys, curData);
            resolve(curData);
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
