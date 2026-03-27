import { apiRequest } from '@/core/js/data/api.js';
import { upFirstLetter, camelToSnakeCase } from '@/core/js/util/util.js';

/**;
 * Configuration pour generic-table
 */

// fonction uniquement utilée dans addStore
// Créé un objet de type configTable à partir de configStore et le stocke dans configStore
const processTableConfig = (configStore) => {
  // initialisation de la config de la table
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
  // transformation des defintion de configStore.defs en tableau de valeurs
  for (const [keyCol, col] of Object.entries(configStore.defs)
    // On ne garde que les colonnes qui sont dans configStore.columns si elles existent
    // et trie les colonnes dans l'ordre de configStore.columns
    .filter(([keyCol]) => !configStore.columns || configStore.columns.includes(keyCol))
    // trie les colonnes dans l'ordre de configStore.columns
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
      type: col.type || 'text',
    };
  }

  configTable.headerDefs = headerDefs;
  configTable.configForm = configStore.configForm;
  configStore.configTable = configTable;
};

// fonction uniquement utilée dans ce fichier
// Supprime les accents d'une chaine de caractères
const unaccent = (s) => {
  return s.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
};

// uniquement utilisé dans ce fichier
// Détermine l'article à utiliser pour un nom de store
// Exemple : "de l'objet" ou "du truc"
const articleDef = (configStore) => {
  const voyelle = 'aeiouy'.includes(unaccent(configStore.label[0]).toLowerCase());
  const M = ['M', undefined].includes(configStore.genre);
  return voyelle ? "de l'" : M ? 'du ' : 'de la ';
};

// uniquement utilisé dans ce fichier
// Détermine l'article à utiliser pour un nom de store
// Exemple : "d'un nouvel objet" ou "d'une nouvelle truc"
const articleUndefNew = (configStore) => {
  const voyelle = 'aeiouy'.includes(unaccent(configStore.label[0]).toLowerCase());
  const M = ['M', undefined].includes(configStore.genre);
  return voyelle && M ? "d'un nouvel" : M ? "d'un nouveau " : "d'une nouvelle ";
};

// fonction uniquement utilée dans addStore
// Créé un objet de type configForm à partir de configStore et le stocke dans configStore

const processFormConfig = (configStore) => {
  const configForm = {
    ...(configStore.form || {}),
    storeName: configStore.storeName,
    idFieldName: configStore.idFieldName,
    title: ({ id }) =>
      id
        ? `Modificiation ${articleDef(configStore)}${configStore.label.toLowerCase()} (id=${id})`
        : `Création ${articleUndefNew(configStore)}${configStore.label.toLowerCase()}`,
    switchDisplay: ({ id }) => !!id,
    displayValue: ({ id }) => !!id,
    displayLabel: true,
  };

  const formDefs = {};
  for (const [keyCol, col] of Object.entries(configStore.defs)) {
    formDefs[keyCol] = {
      ...col,
    };
  }

  configForm.formDefs = formDefs;
  configStore.configForm = configForm;
};

// fonction uniquement utilisée dans addStore
// Définit les valeurs par défaut pour les champs idFieldName et displayFieldName
const processDefaults = (configStore) => {
  /**
   * Fonction magique qui définit des paramètres par défaut basé sur snakeName pour le store
   * idFieldName et displayFieldName
   * @TODO => A SUPPRIMER : specifier les valeurs en dur dans les stores
   */
  configStore.idFieldName = configStore.idFieldName || `id_${configStore.snakeName}`;
  configStore.displayFieldName = configStore.displayFieldName || `nom_${configStore.snakeName}`;
};

export default {
  // utilisé dans les index.js des modules pour traiter leurs stores de données
  // construit des éléments comme des getters, mutations, actions, state et les ajoute à STORE
  // configIn est le fichier de config du store dans chaque module
  // group: "chasse",
  // name: "typeBracelet",
  // label: "Type de bracelet",
  // labels: "Types de bracelet",
  // displayFieldName: "code_type_bracelet",
  // defs: {
  //   id_type_bracelet: {
  //     label: "ID",
  //     type: "text",
  //     hidden: true,
  //   },

  /**
   * Ajoute un store au store Vuex basé sur un objet de configuration.
   *
   * Cette fonction crée un module Vuex complet avec state, getters, mutations et actions
   * pour une ressource générique. Elle gère les opérations CRUD (Création, Lecture, Mise à jour, Suppression)
   * et configure automatiquement les points de terminaison API selon des conventions de nommage.
   *
   * @param {Object} STORE - L'objet store Vuex auquel le module sera ajouté
   * @param {Object} configIn - Objet de configuration qui définit le comportement du store
   * @param {string} configIn.name - Nom de la ressource en camelCase (ex: 'typeBracelet')
   * @param {string} configIn.group - Préfixe de groupe pour le nom du store (ex: 'chasse')
   * @param {string} [configIn.api] - Point de terminaison API personnalisé, par défaut '/api/generic/{group}/{snake_name}'
   * @param {string} configIn.label - Libellé singulier pour la ressource
   * @param {string} [configIn.labels] - Libellés pluriels pour la ressource, par défaut label + 's'
   * @param {string} configIn.idFieldName - Nom du champ utilisé comme identifiant
   * @param {string} configIn.displayFieldName - Nom du champ utilisé pour l'affichage
   * @param {Object} [configIn.options] - Options supplémentaires pour le store
   * @param {boolean} [configIn.loaded=false] - Indique si le store a été chargé
   *
   * @returns {void} - Modifie le paramètre STORE en ajoutant state, getters, mutations et actions
   */

  addStore(STORE, configIn) {
    // depuis la config

    //créé un url pour la requête api à partir du nom typeBracelet => type_bracelet
    const snakeName = camelToSnakeCase(configIn.name);

    // si configIn.api finit par un / on le supprime
    if (configIn.api && configIn.api.endsWith('/')) {
      configIn.api = configIn.api.slice(0, -1);
    }

    // console.log(`Adding store ${configIn.group}/${configIn.name} with api ${configIn.api || `api/generic/${configIn.group}/${snakeName}`}`);
    const api = configIn.api || `api/generic/${configIn.group}/${snakeName}`;
    const apis = `${api}s`;

    // Créé un nom de store à partir de la config : typeBracelet => chasseTypeBracelet
    const storeName = configIn.group + upFirstLetter(configIn.name);

    /** si name = 'trucs */
    /** trucs : nom pour les listes (un s à la fin)  pour les route de liste*/
    const storeNames = `${storeName}s`;

    // met la première lettre en majuscule pour ensuite créer des noms de fonctions getTypeBracelet
    const storeNameCapitalized = upFirstLetter(storeName);

    // creation d'un objet config pour l'enregistrer ensuite dans le store
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
      options: configIn.options,
    };
    processDefaults(configStore);
    processFormConfig(configStore);
    processTableConfig(configStore);

    /** STATE */

    const state = {};
    /** ou l'on stoque le tableau de d'objets */

    /** stockage de la liste */
    state[storeNames] = [];
    /** pour stocker et recupérer la config */
    const storeNameConfig = `${storeName}ConfigStore`;
    state[storeNameConfig] = configStore;

    /** ******************************************************************************** */
    /***************************** CREATION DES GETTERS *********************************/
    /*********************************************************************************** */
    const getters = {};

    /** recuperation des config doit marcher avec tous les stores */
    getters.configStore = (state) => (storeName) => state[`${storeName}ConfigStore`];

    getters.findConfigStore = (state) => (params) => {
      // on cherche la config qui correspond aux paramètres
      const key = Object.keys(state).find((key) => {
        // on cherche la clé qui correspond
        if (!key.includes('ConfigStore')) {
          // si la clé ne contient pas ConfigStore, on retourne faux
          return false;
        }
        return Object.entries(params).every(([k, v]) => {
          // on vérifie que chaque paramètre est respecté
          return state[key][k] == v; // on vérifie que la valeur est égale
        });
      });
      return key && state[key]; // on retourne la config si elle existe
    };

    /** recupération du tableau entier */
    getters[storeNames] = (state) => state[storeNames];

    /** nombre d'éléments */
    getters[configStore.count] = (state) => state[configStore.count];

    getters[configStore.find] = (state) => (params) => {
      return state[storeNames].filter((v) => {
        return (
          Object.keys(params).length == 0 || // si params est vide, on retourne tout
          Object.entries(params).every(([pk, pv]) => {
            // on vérifie que chaque paramètre est respecté pour chaque objet
            return (
              !Object.keys(v).includes(pk) || // si la clé n'existe pas, on retourne faux
              (Array.isArray(pv) // si la valeur est un tableau, on vérifie que la valeur est dans le tableau
                ? !pv.length || pv.includes(v[pk]) // si le tableau est vide, on retourne vrai
                : v[pk] == pv) // sinon on vérifie que la valeur est égale à la valeur du paramètre
            ); // on retourne vrai si la valeur est égale
          })
        ); // on retourne vrai si tous les paramètres sont respectés pour un objet
      }); // on retourne les objets qui respectent les paramètres
    };

    /** récupération d'un objet  par value, fieldName
     * avec idFieldName par défaut
     */
    getters[storeName] =
      (state) =>
      (value, fieldName = configStore.idFieldName) => {
        return state[storeNames] && state[storeNames].find((obj) => obj[fieldName] == value);
      }; // on retourne l'objet qui correspond à la valeur du champ fieldName

    /** ******************************************************************************** */
    /***************************** CREATION DES MUTATIONS *********************************/
    /*********************************************************************************** */

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
          (e) => e[configStore.idFieldName] == obj[configStore.idFieldName]
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
        (o) => o[configStore.idFieldName] === obj[configStore.idFieldName]
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
        (o) => o[configStore.idFieldName] !== obj[configStore.idFieldName]
      );
    };

    mutations[configStore.count] = (state, count) => {
      state[configStore.count] = count;
    };

    /** ******************************************************************************** */
    /***************************** CREATION DES ACTIONS *********************************/
    /*********************************************************************************** */

    const actions = {};

    actions[configStore.count] = ({ getters, commit }) => {
      return new Promise((resolve) => {
        getters;
        apiRequest('GET', `${api}s`, { params: { count: true } }).then((count) => {
          commit(configStore.count, count);
          resolve(count);
        });
      });
    };

    /** Cette partie gère les données en cache pour optimiser les requêtes
     * Si les données existent dans le cache, elles sont retournées directement
     * Sinon, une requête est envoyée au serveur pour les récupérer
     * Les données peuvent être filtrées par des options directement dans le cache
     * Si ForceReload est activé, les données sont toujours récupérées depuis le serveur
     * si serverSide est activé, les données sont retournées directement depuis le serveur. peut être utilise pour l'autocompletion
     */
    actions[configStore.getAll] = ({ getters, commit }, options = {}) => {
      return new Promise((resolve, reject) => {
        const loaded = !options.forceReload && configStore.loaded;
        const objList = getters[storeNames];
        // on vérifie si les données sont déjà chargées
        if (objList && objList.length && loaded && !options.notCommit) {
          if (options) {
            // on vérifie si les options sont définies
            resolve(getters[configStore.find](options));
          }
          resolve(objList); // on retourne les données du cache
          return;
        }
        // si apis finit par un / on le supprime pour éviter les doublons
        let apis_final = apis;
        if (apis_final.endsWith('/')) {
          apis_final = apis_final.slice(0, -1);
        }
        apiRequest('GET', `${apis_final}`, { params: options }, { commit, getters }).then(
          (data) => {
            const items = data.items || data;

            if (!options.notCommit) {
              commit(storeNameConfig, { loaded: true });
              commit(storeNames, items);
            }

            if (options.serverSide) {
              resolve(data);
              return;
            }

            resolve(items);
          },
          (error) => {
            console.error(`error in request ${apis} : ${error}`);
            reject(error);
          }
        );
      });
    };

    /**
     * Crée une fonction d'action générique pour gérer les requêtes HTTP vers une API RESTful.
     *
     * @param {string} requestType - La méthode HTTP à utiliser (GET, POST, PATCH, DELETE).
     * @returns {Function} Une fonction d'action du store qui prend un contexte ({ getters, commit }) et des options.
     * @param {Object} options - Les options pour la requête.
     * @param {*} [options.value=null] - La valeur d'identifiant pour la requête, requise pour GET, PATCH et DELETE.
     * @param {string} [options.fieldName=configStore.idFieldName] - Le nom du champ à utiliser comme identifiant.
     * @param {Object} [options.postData=null] - Les données à envoyer dans le corps de la requête, requis pour POST et PATCH.
     * @returns {Promise<Object>} Une promesse qui se résout avec les données de réponse ou rejette avec une erreur.
     *
     * Retourne une erreur Lorsque des paramètres requis sont manquants selon le type de requête.
     *
     * @example
     * // Définir une action GET
     * const getItem = genericAction('GET');
     * // Utilisation dans le store
     * dispatch('getItem', { value: 123 });
     *
     * @example
     * // Créer un nouvel élément
     * dispatch('postChasseBracelet', {
     *   postData: { code_bracelet: 'BR001', description: 'Bracelet chevreuil' }
     * });
     *
     * @example
     * // Mettre à jour un élément existant
     * dispatch('patchChasseBracelet', {
     *   value: 42,
     *   postData: { description: 'Bracelet chevreuil modifié' }
     * });
     *
     * @example
     * // Supprimer un élément
     * dispatch('deleteChasseBracelet', { value: 42 });
     *
     * @example
     * // Récupérer un élément avec un champ personnalisé
     * dispatch('getChasseBracelet', {
     *   value: 'BR001',
     *   fieldName: 'code_bracelet'
     * });
     */
    const genericAction =
      (requestType) =>
      (
        { getters, commit },
        { value = null, fieldName = configStore.idFieldName, postData = null }
      ) => {
        return new Promise((resolve, reject) => {
          // const configStore = getters.configStore(storeName);
          /** verification des arguments */
          let error;
          if (['PATCH', 'GET', 'DELETE'].includes(requestType) && !value) {
            error = `genericAction Error :  pas d'id fournie pour une requête ${requestType}`;
          }
          if (['PATCH', `POST`].includes(requestType) && !postData) {
            error = `genericAction Error :  pas de postData fourni pour une requête ${requestType}`;
          }
          if (error) {
            console.error(error);
            reject(error);
            return;
          }

          if (requestType == 'GET') {
            const obj = getters[storeName](value, fieldName);
            if (obj) {
              resolve(obj);
              return;
            }
          }

          const apiUrl = requestType === 'POST' ? `${api}` : `${api}/${value}`;
          // si apiUrl finit par un / on le supprime
          const finalApiUrl = apiUrl.endsWith('/') ? apiUrl.slice(0, -1) : apiUrl;
          apiRequest(requestType, finalApiUrl, {
            postData,
            params: { field_name: fieldName },
          }).then(
            (data) => {
              if (requestType === 'DELETE') {
                commit(configStore.delete, data);
              } else {
                commit(storeName, data);
              }
              resolve(data);
            },
            (error) => {
              console.error(`error in request ${api} : ${error}`);
              reject(error);
            }
          );
        });
      };

    /** requetes GET POST PATCH DELETE */
    for (const key of ['GET', 'POST', 'PATCH', 'DELETE']) {
      actions[`${key.toLowerCase()}${storeNameCapitalized}`] = genericAction(key);
    }

    /************************************************************************** */
    /******************* ENREGISTREMENT DES CONFIG  *****************************/
    /************************************************************************** */

    const store = {
      state,
      getters,
      mutations,
      actions,
    };

    for (const key of ['state', 'getters', 'mutations', 'actions']) {
      STORE[key] = { ...(STORE[key] || {}), ...store[key] };
    }
  },

  /**
   Utilisé dans lo module déclaration
   Ajoute des spécificité au store restitution
  */

  addStoreRestitution: (STORE, storeName, getDataAction, configRestitution) => {
    const storeNameConfig = `${storeName}ConfigRestitution`;

    const config = {
      getDataAction,
      ...configRestitution,
    };

    const state = {};
    state[storeNameConfig] = config;
    const getters = {};

    getters.configRestitution = (state) => (storeName) => state[`${storeName}ConfigRestitution`];
    const mutations = {};
    const actions = {};

    const store = {
      state,
      getters,
      mutations,
      actions,
    };

    for (const key of ['state', 'getters', 'mutations', 'actions']) {
      STORE[key] = { ...(STORE[key] || {}), ...store[key] };
    }
  },

  /**
   * Pour l'instant utilisé uniquement dans le module IN
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
    getters[storeNames] = (state) => state[storeNames];

    /** MUTATION */
    mutations[storeNames] = (state, obj) => {
      state[storeNames] = obj;
    };

    /** ACTIONS */
    actions[storeNames] = ({ getters, commit }, { forceReload = false } = {}) => {
      return new Promise((resolve, reject) => {
        const obj = getters[storeNames];
        if (obj && !forceReload) {
          resolve(obj);
          return;
        }

        if (!getters.pendings(api)) {
          // id api finie par / on la supprime pour éviter les doublons
          if (api.endsWith('/')) {
            api = api.slice(0, -1);
          }
          commit('addPending', { api, request: apiRequest('GET', `${api}`) });
        }
        const request = getters.pendings(api);

        request.then(
          (data) => {
            commit(storeNames, data);
            commit('removePending', api); // remove pending
            resolve(data);
          },
          (error) => {
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
      actions,
    };

    for (const key of ['state', 'getters', 'mutations', 'actions']) {
      STORE[key] = { ...(STORE[key] || {}), ...store[key] };
    }
  },
};
