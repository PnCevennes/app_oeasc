import { apiRequest } from "@/core/js/data/api.js";

/**
 *
 * Pour gérer les requêtes mulitples rapprochées
 *
 *
 */
const addPendingRequestStore = STORE => {
  for (const key of ['state', 'mutations', 'getters']) {
    STORE[key] = STORE[key] || {};
  }
  if (STORE.state.pendings == undefined) {
    STORE.state.pendings = {};
    STORE.getters.pendings = state => api => state.pendings[api];
    STORE.mutations.addPending = (state, { request, api }) => {
      state.pendings[api] = request;
      console.info('add pending', api, state.pendings)
    };
    STORE.mutations.removePending = (state, api) => {
      if (state.pendings[api]) {
      console.info('delete pending', api)

        delete state.pendings[api];
      }
    };
  }
};

export default {
  /** initialise un store avec getters mutation dispatch etc 
   * 
   * Exemple : 
  storeUtils.addStore(STORE, "inRealisation", "api/generic/in/realisation", {
    idFieldName: "id_realisation"
  });
   * 
   * name commonsContent
   * api api/generic
   * settings: {
   *  idFieldName
   *  labelFieldName
   * }
  */
  addStore(STORE, name, api, settings) {
    /** si name = 'trucs */
    addPendingRequestStore(STORE);
    /** trucs : nom pour les listes (un s à la fin)  pour les route de liste*/
    const names = `${name}s`;

    /** Truc : pour les actions par ex getTruc postTruc */
    const nameCapitalized = name.charAt(0).toUpperCase() + name.slice(1);

    /** pour stocker et recupérer la config */
    const nameConfig = `${name}ConfigStore`;

    const config = {
      name,
      names,
      count: `count${nameCapitalized}`,
      get: `get${nameCapitalized}`,
      post: `post${nameCapitalized}`,
      patch: `patch${nameCapitalized}`,
      delete: `delete${nameCapitalized}`,
      getAll: `getAll${nameCapitalized}`,
      idFieldName: settings.idFieldName,
      displayFieldName: settings.displayFieldName,
      loaded: false
    };

    /** STATE */

    const state = {};
    /** ou l'on stoque le tableau de d'objets */

    /** stockage de la liste */
    state[names] = [];
    state[nameConfig] = config;

    /** GETTER */

    const getters = {};

    /** recuperation des config doit marcher avec tous les stores */
    getters.configStore = state => name => state[`${name}ConfigStore`];

    /** recupération du tableau entier */
    getters[names] = state => state[names];

    /** nombre d'éléments */
    getters[config.count] = state => state[names].length;

    /** récupération d'un objet  par value, fieldName
     * avec idFieldName par défaut
     */
    getters[name] = state => (value, fieldName = config.idFieldName) =>
      state[names] && state[names].find(obj => obj[fieldName] == value);

    const mutations = {};

    /** MUTATIONS */

    /** config ?? */
    mutations[nameConfig] = (state, config) => {
      const stateConfig = state[nameConfig];
      for (const key of Object.keys(config)) {
        stateConfig[key] = config[key];
      }
    };

    /** assignation du tableau entier */
    mutations[names] = (state, objList) => {
      if (!state[names].length) {
        console.log('mutation', objList)
        state[names] = objList;
        return;
      }
      for (const obj of objList) {
        const elem = state[names].find(
          e => e[config.idFieldName] == obj[config.idFieldName]
        );
        if (elem) {
          for (const key of Object.keys(obj)) {
            elem[key] = obj[key];
          }
        } else {
          state[names].push(obj);
        }
      }
    };

    /** assignation / modification d'un element */
    mutations[name] = (state, obj) => {
      const index = state[names].findIndex(
        o => o[config.idFieldName] === obj[config.idFieldName]
      );
      if (index == -1) {
        state[names].push(obj);
      } else {
        for (const key of Object.keys(obj)) {
          state[names][index][key] = obj[key];
        }
      }
    };

    /** suppression d'un objet */
    mutations[config.delete] = (state, obj) => {
      state[names] = state[names].filter(
        o => o[config.idFieldName] !== obj[config.idFieldName]
      );
    };

    const actions = {};
    /** requete GET pour avoir le tableau d'objets
     * forceReload : forcer la recupération des données depuis le serveur
     * ajout de pendingState ( par url ) quand deux requete sont quasi simultanées
     */
    actions[config.getAll] = (
      { getters, commit },
      { forceReload = false } = {}
    ) => {
      return new Promise((resolve, reject) => {
        const configStore = getters.configStore(name);

        const loaded = !forceReload && configStore.loaded;
        const objList = getters[names];
        if (objList && objList.length && loaded) {
          resolve(objList);
          return;
        }

        const apis = `${api}s/`
        if (!getters.pendings(apis)) {
          commit("addPending", { api: apis, request: apiRequest("GET", `${apis}`) });
        }
        const request = getters.pendings(apis);

        request.then(
          data => {
            commit(nameConfig, { loaded: true });
            commit(names, data);
            commit("removePending", apis); // remove pending
            resolve(data);
          },
          error => {
            console.error(`error in request ${apis} : ${error}`);
            reject(error);
          }
        );
      });
    };

    /** un action = une requete pour une ligne
     * requestType : GET, PATCH, POST, DELETE
     */
    const genericAction = requestType => (
      { getters, commit },
      { value = null, fieldName = config.idFieldName, postData = null }
    ) => {
      return new Promise((resolve, reject) => {
        const configStore = getters.configStore(name);
        /** verification des arguments */
        let error;
        if (["PATCH", "GET", "DELETE"].includes(requestType) && !value) {
          error = `genericAction Error :  pas d'id fournie pour une requête ${requestType}`;
        }
        if (["PATCH", `POST`].includes(requestType) && !postData) {
          error = `genericAction Error :  pas de postData fourni pour une requête ${requestType}`;
        }
        if (error) {
          console.error(error);
          reject(error);
          return;
        }

        if (requestType == "GET") {
          const obj = getters[name](value, fieldName);
          if (obj) {
            resolve(obj);
            return;
          }
        }

        const apiUrl = requestType === "POST" ? `${api}/` : `${api}/${value}`;

        apiRequest(requestType, apiUrl, {
          postData,
          params: { field_name: fieldName }
        }).then(
          data => {
            if (requestType === "DELETE") {
              commit(configStore.delete, data);
            } else {
              commit(name, data);
            }
            resolve(data);
          },
          error => {
            console.error(`error in request ${api} : ${error}`);
            reject(error);
          }
        );
      });
    };

    /** requetes GET POST PATCH DELETE */
    for (const key of ["GET", "POST", "PATCH", "DELETE"]) {
      actions[`${key.toLowerCase()}${nameCapitalized}`] = genericAction(key);
    }

    const store = {
      state,
      getters,
      mutations,
      actions
    };

    for (const key of ["state", "getters", "mutations", "actions"]) {
      STORE[key] = { ...(STORE[key] || {}), ...store[key] };
    }
  },

  /** Besoin de clarification */
  addStoreRestitution: (STORE, name, getDataAction, configRestitution) => {
    const nameConfig = `${name}ConfigRestitution`;

    const config = {
      getDataAction,
      ...configRestitution
    };

    const state = {};
    state[nameConfig] = config;
    const getters = {};

    getters.configRestitution = state => name =>
      state[`${name}ConfigRestitution`];
    const mutations = {};
    const actions = {};

    const store = {
      state,
      getters,
      mutations,
      actions
    };

    for (const key of ["state", "getters", "mutations", "actions"]) {
      STORE[key] = { ...(STORE[key] || {}), ...store[key] };
    }
  },

  /**
   * Par exemple pour les in on a la route qui donne les résultat et qui peut servir pour plein de composants
   * les besoin sont de charger une seul fois l'api et de récupérer les donnée par les getters
   * un pending state est nécessaire pour ne pas faire deux appels quasi simultanés à l'api (cas de graphes multiples dans un content)
   * il y a aussi le besoin de recharger les vrais données à la demande
   *
   * name: inResult
   * api
   */
  addSimpleStore(STORE, name, api) {

    addPendingRequestStore(STORE);

    const state = {},
      getters = {},
      mutations = {},
      actions = {};
    /** ou l'on stoque le tableau de d'objets */

    /** STATE */
    state[name] = null;

    /** GETTER */
    getters[name] = state => state[name];

    /** MUTATION */
    mutations[name] = (state, obj) => {
      state[name] = obj;
    };

    /** ACTIONS */
    actions[name] = ({ getters, commit }, { forceReload = false } = {}) => {
      return new Promise((resolve, reject) => {
        const obj = getters[name];
        if (obj && !forceReload) {
          resolve(obj);
          return;
        }

        if (!getters.pendings(api)) {
          commit("addPending", { api, request: apiRequest("GET", `${api}`) });
        }
        const request = getters.pendings(api);

        request.then(
          data => {
            commit(name, data);
            commit("removePending", api); // remove pending
            resolve(data);
          },
          error => {
            console.error(`error in request ${api} : ${error}`);
            reject(error);
          }
        );
      });
    };

    const store = {
      state,
      getters,
      mutations,
      actions
    };

    for (const key of ["state", "getters", "mutations", "actions"]) {
      STORE[key] = { ...(STORE[key] || {}), ...store[key] };
    }
  }
};
