import { config } from '@/config/config.js';
import { isObject } from '@/core/js/util/util.js';

const BASE_URL = config.URL_APPLICATION;

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

  // On retourne l'objet URL final avec tous les paramètres ajoutés
  return builtUrl;
};

// Requêtes GET en cours, par URL complète : permet de partager une même requête entre plusieurs
// appelants simultanés (option `dedupe`). Retirée dès que la requête se termine (succès ou échec).
const pendingGets = new Map();

// Construit l'erreur rejetée pour une réponse HTTP non acceptée : { status, message, field_errors… }.
// On lit le corps en texte puis on tente de le parser en JSON : ainsi une réponse d'erreur non-JSON
// (page HTML 500, message texte 403…) est quand même rejetée avec un objet exploitable plutôt
// qu'avec une SyntaxError opaque. Contrat consommé par describeApiError (api-messages.js).
const errorFromResponse = async (response) => {
  let text;
  try {
    text = await response.text();
  } catch (e) {
    return { status: response.status, message: null };
  }
  let body = null;
  try {
    body = text ? JSON.parse(text) : null;
  } catch (e) {
    body = null;
  }
  if (body && typeof body === 'object') {
    return { status: response.status, ...body };
  }
  // corps non-JSON : on ne garde le texte que s'il est court et sans balise HTML
  const plain = typeof body === 'string' ? body : text;
  const usable = plain && plain.length < 300 && !/[<>]/.test(plain) ? plain.trim() : null;
  return { status: response.status, message: usable };
};

const sendRequest = async (method, url_, urlRelative, options) => {
  const fetchOptions = {
    method, // Méthode HTTP (GET, POST, PATCH, etc.)
    credentials: 'include', // Permet d'envoyer les cookies avec la requête
  };

  if (['POST', 'PATCH'].includes(method)) {
    const postData = options.postData;
    if (postData && Object.values(postData).some((d) => d instanceof File)) {
      // Données contenant un fichier : FormData
      const data = new FormData();
      for (const [key, value] of Object.entries(postData)) {
        data.append(key, value);
      }
      fetchOptions.body = data;
    } else {
      fetchOptions.body = JSON.stringify(postData || {});
      fetchOptions.headers = {
        Accept: 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
      };
    }
  }

  let response;
  try {
    response = await fetch(url_, fetchOptions);
  } catch (error) {
    // erreur réseau ou d'exécution
    console.error(`Erreur dans apiRequest ${urlRelative} ${error}`);
    throw error;
  }

  // Liste des statuts HTTP considérés comme acceptés (par défaut 200)
  const acceptedStatus = options.acceptedStatus || [200];
  if (!acceptedStatus.includes(response.status)) {
    throw await errorFromResponse(response);
  }
  return response.json();
};

/**
 * Effectue une requête API.
 * @param {*} method - La méthode HTTP à utiliser (GET, POST, etc.).
 * @param {*} urlRelative - L'URL relative de l'API.
 * @param {*} options - Les options de la requête :
 *   - params : paramètres de la query string
 *   - postData : corps pour POST / PATCH (FormData automatique si un champ est un File)
 *   - acceptedStatus : statuts HTTP considérés comme réussis (défaut [200])
 *   - dedupe : si true, un GET identique déjà en cours est réutilisé au lieu d'être renvoyé
 * @returns {Promise} - Résolue avec le JSON de la réponse ; rejetée avec { status, message, field_errors… }
 *   pour un statut non accepté, ou avec l'erreur réseau.
 */
var apiRequest = (method, urlRelative, options = {}) => {
  const url_ = url(urlRelative, options.params);

  if (method == 'GET' && options.dedupe) {
    const key = url_.href;
    let request = pendingGets.get(key);
    if (!request) {
      request = sendRequest(method, url_, urlRelative, options).finally(() =>
        pendingGets.delete(key)
      );
      pendingGets.set(key, request);
    }
    return request;
  }
  return sendRequest(method, url_, urlRelative, options);
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
  const url = `${BASE_URL}/${urlRelative}`;

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
      // Session Flask expirée : l'app est en hash history (et servie sous /front/), donc on
      // change le hash vers la route SPA /login, pas l'URL serveur
      const redirect = window.location.hash.replace(/^#/, '');
      window.location.hash = `#/login${redirect && redirect !== '/login' ? `?redirect=${encodeURIComponent(redirect)}` : ''}`;
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

export { apiRequest, url, simple_fetch };
