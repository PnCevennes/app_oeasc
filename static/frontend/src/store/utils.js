import { apiRequest } from "@/core/js/data/api.js";

export default {
  /** initialise un store avec getters mutation dispatch et */
  addStore(STORE, name, api, idFieldName) {
    /** si name = 'trucs */

    /** trucs : nom pour les listes (un s à la fin) */
    const names = `${name}s`;

    /** Truc : pour les actions par ex getTruc postTruc */
    const nameCapitalized = name.charAt(0).toUpperCase() + name.slice(1);

    /** trucIdFiledName : pour stocker le nom du champs de l'id */
    const nameIdFieldName = `${name}IdFieldName`;

    /** trucIdLoaded : pour savoir si on à récupéré la liste des truc
     *    (si par exemple on à recupérer un truc isolé et qu'on veut avoir la liste ensuite...) */
    const nameLoaded = `${nameCapitalized}Loaded`;

    const nameConfig = `${name}Config`;

    const config = {
      get: `get${nameCapitalized}`,
      post: `post${nameCapitalized}`,
      patch: `patch${nameCapitalized}`,
      delete: `delete${nameCapitalized}`,
      getAll: `getAll${nameCapitalized}`,
      idFieldName,
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
    getters.configStore = state => name => state[`${name}Config`] 

    /** récupération d'un objet */
    getters[name] = state => (value, fieldName = idFieldName) =>
      state[names] && state[names].find(obj => obj[fieldName] == value);

    const mutations = {};
    mutations[nameLoaded] = (state, recupAll) => {
      state[nameLoaded] = recupAll;
    };

    mutations[nameIdFieldName] = (state, idFieldName) => {
      state[nameIdFieldName] = idFieldName;
    };

    /** assignation du tableau entier */
    mutations[names] = (state, objList) => {
      state[names] = objList;
    };

    /** assignation d'un objet */
    mutations[name] = (state, obj) => {
      const index = state[names].findIndex(
        o => o[idFieldName] === obj[idFieldName]
      );
      if (index == -1) {
        state[names].push(obj);
      } else {
        state[names][index] = obj;
      }
    };

    /** suppression d'un objet */
    mutations[config.delete] = (state, obj) => {
      const index = state[names].findIndex(
        o => o[idFieldName] === obj[idFieldName]
      );
      if (index == -1) {
        state[names].splice(index, 1);
      }
    };

    const actions = {};
    /** requete GET pour avoir le tableau d'objets */
    actions[config.getAll] = ({ getters, commit }) => {
      return new Promise((resolve, reject) => {
        const recupAll = getters[nameLoaded];
        const objList = getters[names];
        if (objList && objList.length && recupAll) {
          resolve(objList);
          return;
        }
        apiRequest("GET", `${api}s`).then(
          data => {
            commit(nameLoaded, true);
            commit(names, data);
            resolve(data);
          },
          error => {
            console.log(`error in request ${api} : ${error}`);
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
        /** verification des arguments */
        let error;
        if (["PATCH", "GET", "DELETE"].includes(requestType) && !id) {
          error = `genericAction Error :  pas d'id fournie pour une requête ${requestType}`;
        }
        if (["PATCH", `POST`].includes(requestType) && !postData) {
          error = `genericAction Error :  pas de postData fourni pour une requête ${requestType}`;
        }
        if (error) {
          console.log(error);
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

        const apiUrl = requestType === "POST" ? `${api}` : `${api}/${id}`;
        apiRequest(requestType, apiUrl, { postData }).then(
          data => {
            if(requestType === 'DELETE') {
              commit(config.delete, data)
            } else {
              commit(name, data);
            }
            resolve(data);
          },
          error => {
            console.log(`error in request ${api} : ${error}`);
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
  }
};
