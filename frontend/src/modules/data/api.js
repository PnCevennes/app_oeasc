import { apiRequest } from '@/core/js/data/api.js';

// Définition de l'objet STORE utilisé comme module Vuex pour la gestion du cache des données API
const STORE = {
  state: {
    // _cache : objet utilisé pour stocker les données mises en cache
    _cache: {},
  },
  mutations: {
    /**
     * setCache
     * Mutation utilisée pour enregistrer des données dans le cache.
     * cacheKeys : tableau de clés pour accéder à la bonne profondeur dans l'objet _cache (ex: ["nomenclature", "TYPE_SITE"])
     * data : données à stocker
     * Utilisée lors de la réception de nouvelles données depuis l'API, généralement appelée dans l'action cacheOrRequest.
     */
  },
  getters: {
    /**
     * getFromCache
     * Getter permettant de récupérer une donnée depuis le cache à partir d'un tableau de clés.
     * cacheKeys : tableau de clés pour accéder à la donnée
     * Utilisé pour vérifier si une donnée est déjà présente dans le cache avant de faire une requête API.
     */
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
    // cacheOrRequest: (
    //   { commit, getters },
    //   { url, method = 'GET', postData = null, cacheKeys, dataKeys = [] }

    //     // Si non présente, effectue la requête API et stocke le résultat dans le cache

    
  },
};

export { STORE };
