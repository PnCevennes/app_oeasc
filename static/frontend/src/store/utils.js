import { apiRequest } from "@/core/js/data/api.js";

export default {
  /** initialise un store avec getters mutation dispatch et */
  addStore(STORE, name, api, idFieldName) {
    const names = `${name}s`;
    const nameCapitalized = name.charAt(0).toUpperCase() + name.slice(1);
    const nameIdFieldName = `${name}idFieldName`

    const state = {};
    /** ou l'on stoque le tableau de d'objets */
    state[names] = [];
    state[nameIdFieldName] = idFieldName

    const getters = {};
    /** recupération du tableau entier */
    getters[names] = state => state[names];
    getters[nameIdFieldName] = state => state[nameIdFieldName]

    /** récupération d'un objet */
    getters[name] = (value, fieldName = idFieldName) => state =>
      state[names] && state[names].find(obj => obj[fieldName] == value);

    const mutations = {};
    /** assignation du tableau entier */
    mutations[names] = (state, objList) => {
      state[name] = objList;
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

    const actions = {};
    /** requete GET pour avoir le tableau d'objets */
    actions[`get_${names}`] = ({ getters, commit }) => {
      return new Promise((resolve, reject) => {
        const objList = getters[names];
        if (objList && objList.length) {
          resolve(objList);
          return;
        }
        apiRequest("GET", `${api}s`).then(
          data => {
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

    const genericAction = (requestType) => ({getters, commit}, {id=null, postData=null}) => {
      return new Promise((resolve, reject) => {
        /** verification des arguments */
        let error;
        if( ['PATCH', 'GET', 'DELETE'].includes(requestType) && !id) {
            error = `genericAction Error :  pas d'id fournie pour une requête ${requestType}`;
        }
        if( ['PATCH', `POST`].includes(requestType) && !postData) {
            error =`genericAction Error :  pas de postData fourni pour une requête ${requestType}`;
        }
        if (error) {
            console.log(error);
            reject(error);
            return;
        }

        if ( requestType == 'GET') {
            const obj = getters[name](id);
            if (obj) {
              resolve(obj);
              return;
            } 
        }

        const apiUrl = requestType === 'POST' ? `${api}` : `${api}/${id}`;
        apiRequest(requestType, apiUrl, {postData}).then(
            data => {
              commit(name, data);
              resolve(data);
            },
            error => {
              console.log(`error in request ${api} : ${error}`);
              reject(error);
            }
          );
      });
    }

    /** requetes GET POST PATCH DELETE */
    for( const key of ['GET', 'POST', 'PATCH', 'DELETE']) {
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
