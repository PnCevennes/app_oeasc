import { apiRequest } from "@/core/js/data/api.js";

export default {
  /** initialise un store avec getters mutation dispatch et */
  addStore(STORE, name, api, settings) {
    /** si name = 'trucs */

    /** trucs : nom pour les listes (un s à la fin) */
    const names = `${name}s`;

    /** Truc : pour les actions par ex getTruc postTruc */
    const nameCapitalized = name.charAt(0).toUpperCase() + name.slice(1);

    const nameConfig = `${name}ConfigStore`;

    const config = {
      get: `get${nameCapitalized}`,
      post: `post${nameCapitalized}`,
      patch: `patch${nameCapitalized}`,
      delete: `delete${nameCapitalized}`,
      getAll: `getAll${nameCapitalized}`,
      idFieldName: settings.idFieldName,
      displayFieldName: settings.displayFieldName,
      loaded: false,
    }

    const state = {};
    /** ou l'on stoque le tableau de d'objets */

    state[names] = [];
    state[nameConfig] = config;

    const getters = {};
    /** recupération du tableau entier */

    getters[names] = state => state[names];

    /** recuperation des config doit marcher avec tous les stores */
    getters.configStore = state => name => state[`${name}ConfigStore`] 

    /** récupération d'un objet */
    getters[name] = state => (value, fieldName = settings.idFieldName) =>
      state[names] && state[names].find(obj => obj[fieldName] == value);

    const mutations = {};

    mutations[nameConfig] = (state, config) => {
      const stateConfig = state[nameConfig];
      for (const key of Object.keys(config)) {
        stateConfig[key] = config[key];
      }
    }

    /** assignation du tableau entier */
    mutations[names] = (state, objList) => {
      state[names] = objList;
    };

    /** assignation d'un objet */
    mutations[name] = (state, obj) => {
      const index = state[names].findIndex(
        o => o[settings.idFieldName] === obj[settings.idFieldName]
      );
      if (index == -1) {
        state[names].push(obj);
      } else {
        state[names][index] = obj;
      }
    };

    /** suppression d'un objet */
    mutations[config.delete] = (state, obj) => {
      state[names] = state[names].filter( o => o[settings.idFieldName] !== obj[settings.idFieldName]);
    };

    const actions = {};
    /** requete GET pour avoir le tableau d'objets */
    actions[config.getAll] = ({ getters, commit }) => {
      return new Promise((resolve, reject) => {
        const configStore = getters.configStore(name);

        const loaded = configStore.loaded;
        const objList = getters[names];
        if (objList && objList.length && loaded) {
          resolve(objList);
          return;
        }
        apiRequest("GET", `${api}s/`).then(
          data => {
            commit(nameConfig, {loaded:true});
            commit(names, data);
            resolve(data);
          },
          error => {
            console.error(`error in request ${api} : ${error}`);
            reject(error);
          }
        );
      });
    };

    const genericAction = requestType => (
      { getters, commit },
      { id = null, postData = null }
    ) => {
      return new Promise((resolve, reject) => {
        const configStore = getters.configStore(name);
        /** verification des arguments */
        let error;
        if (["PATCH", "GET", "DELETE"].includes(requestType) && !id) {
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
          const obj = getters[name](id);
          if (obj) {
            resolve(obj);
            return;
          }
        }

        const apiUrl = requestType === "POST" ? `${api}/` : `${api}/${id}`;
        console.log(apiUrl)
        apiRequest(requestType, apiUrl, { postData }).then(
          data => {
            if(requestType === 'DELETE') {
              commit(configStore.delete, data)
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

  addStoreRestitution: (STORE, name, getDataAction, configRestitution) => {

    const nameConfig = `${name}ConfigRestitution`;

    const config = {
      getDataAction,
      ...configRestitution
    };


    const state = {};
    state[nameConfig] = config;
    const getters = {};

    getters.configRestitution = state => name => state[`${name}ConfigRestitution`]; 
    const mutations = {};
    const actions = {};    

    const store = {
      state,
      getters,
      mutations,
      actions,
    };

    for (const key of ["state", "getters", "mutations", "actions"]) {
      STORE[key] = { ...(STORE[key] || {}), ...store[key] };
    }

  }
};
