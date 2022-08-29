import { apiRequest } from "@/core/js/data/api.js";
import { upFirstLetter, camelToSnakeCase } from "@/core/js/util/util.js";

/**;
 * Configuration pour generic-table
 */
// const addPendingRequestStore = STORE => {
//   for (const key of ['state', 'mutations', 'getters']) {
//     STORE[key] = STORE[key] || {};
//   }
//   if (STORE.state.pendings === undefined) {
//     STORE.state.pendings = {};
//     STORE.getters.pendings = state => api => state.pendings[api];
//     STORE.mutations.addPending = (state, { request, api }) => {
//       state.pendings[api] = request;
//       console.info('add pending', api, state.pendings)
//     }
//   }
// }

const processTableConfig = configStore => {
  const configTable = {
    storeName: configStore.storeName,
    options: configStore.options,
    labelFieldName: configStore.labelFieldName,
    idFieldName: configStore.idFieldName,
    dense: true,
    striped: true,
    small: true,
    configForm: configStore.form,
  };

  const headerDefs = {};
  for (const [keyCol, col] of Object.entries(configStore.defs)
    .filter(
      ([keyCol]) => (!configStore.columns) || configStore.columns.includes(keyCol)
    )
    .sort((a, b) =>
      configStore.columns
        ? configStore.columns.indexOf(b[0]) - configStore.columns.indexOf(a[0]) < 0
          ? 1
          : -1
        : 0
    )) {
    headerDefs[keyCol] = {
      ...col,
      text: col.text || col.label,
      type: col.type || "text"
    };
  }

  configTable.headerDefs = headerDefs;
  configTable.configForm = configStore.configForm;
  configStore.configTable = configTable;
};

const unaccent = s => {
  return s.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
};

const articleDef = configStore => {
  const voyelle = "aeiouy".includes(
    unaccent(configStore.label[0]).toLowerCase()
  );
  const M = ["M", undefined].includes(configStore.genre);
  return voyelle ? "de l'" : M ? "du " : "de la ";
};

const articleUndefNew = configStore => {
  const voyelle = "aeiouy".includes(
    unaccent(configStore.label[0]).toLowerCase()
  );
  const M = ["M", undefined].includes(configStore.genre);
  return voyelle && M ? "d'un nouvel" : M ? "d'un nouveau " : "d'une nouvelle ";
};

const processFormConfig = configStore => {
  const configForm = {
    ...(configStore.form || {}),
    storeName: configStore.storeName,
    idFieldName: configStore.idFieldName,
    title: ({ id }) =>
      id
        ? `Modificiation ${articleDef(
            configStore
          )}${configStore.label.toLowerCase()} (id=${id})`
        : `Création ${articleUndefNew(
            configStore
          )}${configStore.label.toLowerCase()}`,
    switchDisplay: ({ id }) => !!id,
    displayValue: ({ id }) => !!id,
    displayLabel: true
  };

  const formDefs = {};
  for (const [keyCol, col] of Object.entries(configStore.defs)) {
    formDefs[keyCol] = {
      ...col
    };
  }

  configForm.formDefs = formDefs;
  configStore.configForm = configForm;
};

const processDefaults = configStore => {
  /**
   * Fonction magique qui définit des paramètres par défaut basé sur snakeName pour le store
   * idFieldName et displayFieldName
   * @TODO => A SUPPRIMER : specifier les valeurs en dur dans les stores
   */
  configStore.idFieldName =
    configStore.idFieldName || `id_${configStore.snakeName}`;
  configStore.displayFieldName =
    configStore.displayFieldName || `nom_${configStore.snakeName}`;
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
  addStore(STORE, configIn) {
    // depuis la config
    const snakeName = camelToSnakeCase(configIn.name);
    const api = configIn.api || `api/generic/${configIn.group}/${snakeName}`;
    const apis = `${api}s/`;

    const storeName = configIn.group + upFirstLetter(configIn.name);

    /** si name = 'trucs */
    /** trucs : nom pour les listes (un s à la fin)  pour les route de liste*/
    const storeNames = `${storeName}s`;

    /** Truc : pour les actions par ex getTruc postTruc */
    const storeNameCapitalized = upFirstLetter(storeName);

    /** pour stocker et recupérer la config */
    const storeNameConfig = `${storeName}ConfigStore`;

    const configStore = {
      ...configIn,
      storeName,
      storeNames,
      snakeName,
      apis,
      api,
      labels: configIn.labels || `${configIn.label}s`,
      get: `get${storeNameCapitalized}`,
      post: `post${storeNameCapitalized}`,
      patch: `patch${storeNameCapitalized}`,
      delete: `delete${storeNameCapitalized}`,
      getAll: `getAll${storeNameCapitalized}`,
      count: `count${storeNameCapitalized}`,
      find: `find${storeNameCapitalized}`,
      idFieldName: configIn.idFieldName,
      displayFieldName: configIn.displayFieldName,
      loaded: false,
      options: configIn.options
    };
    processDefaults(configStore);
    processFormConfig(configStore);
    processTableConfig(configStore);

    /** STATE */

    const state = {};
    /** ou l'on stoque le tableau de d'objets */

    /** stockage de la liste */
    state[storeNames] = [];
    state[storeNameConfig] = configStore;

    /** GETTER */

    const getters = {};

    /** recuperation des config doit marcher avec tous les stores */
    getters.configStore = state => storeName => state[`${storeName}ConfigStore`];

    getters.findConfigStore = state => params => {
      const key = Object.keys(state).find(key => {
        if (!key.includes('ConfigStore')) {
          return false;
        }
        return Object.entries(params).every(([k,v]) => {
          return state[key][k] == v
        } )
      });
      return key && state[key];
    }


    /** recupération du tableau entier */
    getters[storeNames] = state => state[storeNames];

    /** nombre d'éléments */
    getters[configStore.count] = state => state[configStore.count];


    getters[configStore.find] = state => (params) => {
      return state[storeNames].filter(v =>
        {
          return Object.keys(params).length == 0
          || Object.entries(params).every(([pk,pv]) => {
            return (!Object.keys(v).includes(pk)) ||
              ( Array.isArray(pv)
                ? ((!pv.length) || pv.includes(v[pk]))
                : v[pk] == pv
              )
          })
        })
    }
    /** récupération d'un objet  par value, fieldName
     * avec idFieldName par défaut
     */
    getters[storeName] = state => (
      value,
      fieldName = configStore.idFieldName
    ) => {
      return state[storeNames] &&
      state[storeNames].find(obj => obj[fieldName] == value);
    }

    const mutations = {};

    /** MUTATIONS */

    /** config ?? */
    mutations[storeNameConfig] = (state, config) => {
      const stateConfig = state[storeNameConfig];
      for (const key of Object.keys(config)) {
        stateConfig[key] = config[key];
      }
    };

    /** assignation du tableau entier */
    mutations[storeNames] = (state, objList) => {

      if (!state[storeNames].length) {
        state[storeNames] = objList;
        return;
      }
      for (const obj of objList) {
        const elem = state[storeNames].find(
          e => e[configStore.idFieldName] == obj[configStore.idFieldName]
        );
        if (elem) {
          for (const key of Object.keys(obj)) {
            elem[key] = obj[key];
          }
        } else {
          state[storeNames].push(obj);
        }
      }
    };

    /** assignation / modification d'un element */
    mutations[storeName] = (state, obj) => {
      const index = state[storeNames].findIndex(
        o => o[configStore.idFieldName] === obj[configStore.idFieldName]
      );
      if (index == -1) {
        state[storeNames].push(obj);
      } else {
        for (const key of Object.keys(obj)) {
          state[storeNames][index][key] = obj[key];
        }
      }
    };

    /** suppression d'un objet */
    mutations[configStore.delete] = (state, obj) => {
      state[storeNames] = state[storeNames].filter(
        o => o[configStore.idFieldName] !== obj[configStore.idFieldName]
      );
    };

    mutations[configStore.count] = (state, count) => {
      state[configStore.count] = count;
    }

    const actions = {};

    actions[configStore.count] = ({getters, commit}) => {
      return new Promise((resolve) => {
        getters;
        apiRequest("GET", `${api}s/`, {params: {count:true}}).then((count) => {
          commit(configStore.count, count);
          resolve(count);
        });
      });
    }


    /** requete GET pour avoir le tableau d'objets
     * forceReload : forcer la recupération des données depuis le serveur
     */
    actions[configStore.getAll] = (
      { getters, commit },
       options = {}
    ) => {
      return new Promise((resolve, reject) => {
        const loaded = !options.forceReload && configStore.loaded;
        const objList = getters[storeNames];
        if (objList && objList.length && loaded && !options.notCommit) {
          if(options) {
            resolve(getters[configStore.find](options))
          }
          resolve(objList);
          return;
        }
        apiRequest("GET", `${apis}`, {params:options}, {commit, getters}).then(
          data => {

            const items = data.items || data;

            if(!options.notCommit) {
              commit(storeNameConfig, { loaded: true });
              commit(storeNames, items);
            }

            if(options.serverSide) {
              resolve(data);
              return;
            }

            resolve(items);
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
      { value = null, fieldName = configStore.idFieldName, postData = null }
    ) => {
      return new Promise((resolve, reject) => {
        // const configStore = getters.configStore(storeName);
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
          const obj = getters[storeName](value, fieldName);
          if (obj) {
            resolve(obj);
            return;
          }
        }

        const apiUrl = requestType === "POST" ? `${api}/` : `${api}/${value}`;

        apiRequest(requestType, apiUrl, {
          postData,
          params: { field_name: fieldName },
        }).then(
          data => {
            if (requestType === "DELETE") {
              commit(configStore.delete, data);
            } else {
              commit(storeName, data);
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
      actions[`${key.toLowerCase()}${storeNameCapitalized}`] = genericAction(
        key
      );
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
  addStoreRestitution: (STORE, storeName, getDataAction, configRestitution) => {
    const storeNameConfig = `${storeName}ConfigRestitution`;

    const config = {
      getDataAction,
      ...configRestitution
    };

    const state = {};
    state[storeNameConfig] = config;
    const getters = {};

    getters.configRestitution = state => storeName =>
      state[`${storeName}ConfigRestitution`];
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
  addSimpleStore(STORE, storeNames, api) {

    const state = {},
      getters = {},
      mutations = {},
      actions = {};
    /** ou l'on stoque le tableau de d'objets */

    /** STATE */
    state[storeNames] = null;

    /** GETTER */
    getters[storeNames] = state => state[storeNames];

    /** MUTATION */
    mutations[storeNames] = (state, obj) => {
      state[storeNames] = obj;
    };

    /** ACTIONS */
    actions[storeNames] = (
      { getters, commit },
      { forceReload = false } = {}
    ) => {
      return new Promise((resolve, reject) => {
        const obj = getters[storeNames];
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
            commit(storeNames, data);
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
