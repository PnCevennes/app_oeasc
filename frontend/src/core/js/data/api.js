import { config } from '@/config/config.js';
import { isObject } from '@/core/js/util/util.js';

/**
 * @constant
 * @type {Object}
 * @description
 * STORE est un objet utilisé comme espace de stockage centralisé pour l'application.
 * Il permet de conserver et de partager des données entre différents composants Vue.js.
 * Cet objet peut être enrichi avec des propriétés ou des méthodes selon les besoins de l'application.
 */
const STORE = {};
const BASE_URL = config.URL_APPLICATION;

// initialisation de l'objet STORE
for (const key of ['state', 'mutations', 'getters']) {
  STORE[key] = STORE[key] || {};
}
// si la clé 'pendings' n'existe pas
// on la crée
if (STORE.state.pendings == undefined) {
  STORE.state.pendings = {};
  // on initialise l'objet pendings
  // pour stocker les requêtes en attente
  STORE.getters.pendings = (state) => {
    return (api) => {
      return state.pendings[api];
    };
  };
  // on ajoute une mutation pour ajouter une requête en attente
  STORE.mutations.addPending = (state, { request, api }) => {
    state.pendings[api] = request;
  };
  // on ajoute une mutation pour supprimer une requête en attente
  // si elle existe
  // (utile pour éviter les doublons dans les requêtes GET)
  STORE.mutations.removePending = (state, api) => {
    if (state.pendings[api]) {
      delete state.pendings[api];
    }
  };
}

/**
 * Fonction permettant de construire une URL complète à partir d'une URL relative et de paramètres optionnels.
 * url('api/v1/users', {name: 'toto', age: 25})
 * -> http://localhost:8000/api/v1/users?name=toto&age=25
 * @param {*} urlRelative - L'URL relative à laquelle on souhaite accéder (ex: 'api/v1/users').
 * @param {*} params - Un objet contenant les paramètres à ajouter à la query string de l'URL.
 * @returns {URL} - L'objet URL construit avec les paramètres.
 */
var url = (urlRelative, params = {}) => {
  // Création de l'objet URL en utilisant l'URL de base de l'application et l'URL relative passée en paramètre
  let builtUrl = new URL(`${config.URL_APPLICATION}/${urlRelative}`);
  console.log('builtUrl', builtUrl);

  // Parcours de chaque clé des paramètres
  Object.keys(params)
    // On filtre les clés dont la valeur n'est ni null ni undefined
    .filter((key) => ![null, undefined].includes(params[key]))
    .forEach((key) =>
      isObject(params[key])
        ? // Si la valeur du paramètre est un objet (ex: un dictionnaire), on le convertit en chaîne JSON
          builtUrl.searchParams.append(key, JSON.stringify(params[key]))
        : // Sinon, on ajoute la valeur telle quelle dans la query string
          builtUrl.searchParams.append(key, params[key])
    );
  
  // si builtUrl finit par un / on le supprime pour éviter les doublons
  if (builtUrl.href.endsWith('/')) {
    builtUrl = new URL(builtUrl.href.slice(0, -1));
  }
  console.log('builtUrl after params', builtUrl);

  // On retourne l'objet URL final avec tous les paramètres ajoutés
  return builtUrl;
};

// fonction qui permet de gérer les erreurs
// lors de l'appel à une API
// elle affiche un message d'erreur dans la console
// et renvoie une erreur
var fail = (msg) => {
  console.error(`apiRequest fail : ${msg}`);
};

/**
 * Fonction asynchrone permettant de récupérer des données depuis une API via une requête GET.
 * @param {*} urlRelative - L'URL relative de l'API à interroger.
 * @param {*} options - Les options de la requête (params pour les paramètres de l'URL, headers pour les en-têtes HTTP).
 * @returns {Promise} - Une promesse résolue avec les données récupérées ou undefined en cas d'erreur.
 */
const fetchData = async (urlRelative, options = {}) => {
  // Construction de l'URL complète à partir de l'URL relative et des éventuels paramètres
  const url_ = url(urlRelative, options.params);

  // Préparation des options pour la requête fetch
  var fetchOptions = {
    method: 'GET', // Méthode HTTP utilisée : GET
    headers: {
      'Content-Type': 'application/json', // Type de contenu attendu en réponse
      ...options.headers, // Fusion des éventuels headers supplémentaires passés en option
    },
    credentials: 'include', // Permet d'envoyer les cookies avec la requête (authentification, session, etc.)
  };

  // si url_ finit par un / on le supprime pour éviter les doublons
  if (url_.href.endsWith('/')) {
    url_ = new URL(url_.href.slice(0, -1));
  }

  try {
    // Exécution de la requête fetch vers l'API
    const response = await fetch(url_, fetchOptions);

    // Conversion de la réponse en JSON
    const data = await response.json();

    // Renvoi des données récupérées
    return data;
  } catch (error) {
    // Affichage d'une erreur dans la console en cas d'échec de la requête
    console.error('Erreur lors de la récupération des données:', error);
  }
};

/**
 * Effectue une requête API.
 * @param {*} method - La méthode HTTP à utiliser (GET, POST, etc.).
 * @param {*} urlRelative - L'URL relative de l'API.
 * @param {*} options - Les options de la requête (params, headers, etc.).
 * @param {*} $store - Le store Vuex (si utilisé).
 * @returns {Promise} - Une promesse qui se résout avec la réponse de l'API.
 */
var apiRequest = (method, urlRelative, options = {}, $store = null) => {
  // On construit l'URL complète de l'API à partir de l'URL relative et des paramètres éventuels
  const url_ = url(urlRelative, options.params);

  console.log('url_ after params', url_);
  let request = null; // Variable qui va contenir la promesse de la requête
  let commit; // Variable pour savoir si on doit enregistrer la requête dans le store

  // Gestion des requêtes GET pour éviter les doublons si une requête identique est déjà en cours
  if (method == 'GET' && $store) {
    // On récupère la requête en cours depuis le store (si elle existe)
    request = $store.getters.pendings(url_.href);
    // Si aucune requête n'est en cours, on indique qu'il faudra l'enregistrer
    if (!request) {
      commit = true;
    }
  }

  // Si aucune requête n'est en cours, on crée une nouvelle promesse pour la requête
  request =
    request ||
    new Promise((resolve, reject) => {
      var fetchOptions = {
        method, // Méthode HTTP (GET, POST, PATCH, etc.)
        credentials: 'include', // Permet d'envoyer les cookies avec la requête
      };

      // Gestion des requêtes POST et PATCH
      if (['POST', 'PATCH'].includes(method)) {
        const postOptions = {};
        // Si les données à envoyer contiennent un fichier
        if (options.postData && Object.values(options.postData).some((d) => d instanceof File)) {
          var data = new FormData();
          // On ajoute chaque donnée dans le FormData (pour l'envoi de fichiers)
          for (const [key, value] of Object.entries(options.postData || {})) {
            data.append(key, value);
          }
          postOptions.body = data;
        } else {
          // Si les données ne contiennent pas de fichier
          postOptions.body = JSON.stringify(options.postData || {});
          postOptions.headers = {
            Accept: 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
          };
        }
        // On fusionne les options spécifiques POST/PATCH avec les options de base
        fetchOptions = { ...fetchOptions, ...postOptions };
      }

      // Exécution de la requête fetch
      fetch(url_, fetchOptions).then(
        (response) => {
          // Pour les requêtes GET, on retire la requête du store une fois terminée
          if (method == 'GET' && $store) {
            $store.commit('removePending', url_.href);
          }

          // Liste des statuts HTTP considérés comme acceptés (par défaut 200)
          const acceptedStatus = options.acceptedStatus || [200];
          if (acceptedStatus.includes(response.status)) {
            // Si la requête a réussi
            // On récupère la réponse au format JSON et on résout la promesse
            response.json().then(
              (json) => {
                resolve(json);
              },
              (error) => {
                reject(error);
              }
            );
          } else {
            // Si la requête a échoué (statut non accepté)
            if (response.json) {
              // On tente de récupérer le message d'erreur au format JSON
              response.json().then(
                (json) => {
                  reject(json);
                },
                (error) => {
                  reject(error);
                }
              );
            } else {
              // Si pas de JSON, on rejette la réponse brute
              reject(response);
            }
          }
        },

        // Gestion des erreurs réseau ou d'exécution
        (msg_fail) => {
          // Pour les requêtes GET, on retire la requête du store en cas d'échec
          if (method == 'GET' && $store) {
            $store.commit('removePending', url_.href);
          }
          // Affichage d'un message d'erreur dans la console
          console.error(`Erreur dans apiRequest ${urlRelative} ${msg_fail}`);
          // On rejette la promesse avec l'erreur
          reject(msg_fail);
        }
      );
    });

  // Si commit est vrai, on enregistre la requête en cours dans le store (pour éviter les doublons)
  if (commit) {
    $store.commit('addPending', {
      api: url_.href,
      request,
    });
  }
  // On retourne la promesse de la requête
  return request;
};





/**
 *
 * @param {*} method => "GET", "POST", "PATCH", etc.
 * @param {*} urlRelative => "api/v1/users", etc.
 * @param {*} body => Données à envoyer dans le corps de la requête (JSON ou FormData)
 * @param {*} options => Options supplémentaires pour fetch (headers, etc.): ex: { headers: { Authorization: 'Bearer token' } }
 * @returns => Promesse résolue avec les données JSON de la réponse
 */

const simple_fetch = async (method, urlRelative, body = null, options = {}) => {
  const url = `${BASE_URL}${urlRelative}`;

  const configRequest = {
    method: method.toUpperCase(),
    // Indispensable pour que Flask puisse lire/écrire le cookie de session
    credentials: 'include',
    ...options,
    headers: {
      Accept: 'application/json',
      ...options.headers,
    },
  };

  if (body) {
    if (body instanceof FormData) {
      configRequest.body = body;
    } else {
      configRequest.body = JSON.stringify(body);
      configRequest.headers['Content-Type'] = 'application/json';
    }
  }

  try {
    const response = await fetch(url, configRequest);

    if (response.status === 401) {
      // Rediriger vers login si la session Flask a expiré
      window.location.href = '/login';
      return;
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Erreur: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Erreur API:', error.message);
    throw error;
  }
};

export { apiRequest, url, fetchData, STORE, simple_fetch };
