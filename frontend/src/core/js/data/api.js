import { config } from "@/config/config.js";
import { isObject } from "@/core/js/util/util";

const STORE = {};


// initialisation de l'objet STORE
// si les clés 'state', 'mutations' et 'getters' n'existent pas
// on les crée
for (const key of ["state", "mutations", "getters"]) {
  STORE[key] = STORE[key] || {};
}
// si la clé 'pendings' n'existe pas
// on la crée
if (STORE.state.pendings == undefined) {
  STORE.state.pendings = {};
  STORE.getters.pendings = state => api => state.pendings[api];
  STORE.mutations.addPending = (state, { request, api }) => {
    state.pendings[api] = request;
  };


  STORE.mutations.removePending = (state, api) => {
    if (state.pendings[api]) {
      delete state.pendings[api];
    }
  };
}

// fonction qui permet de construire une URL
// à partir d'une URL relative et de paramètres
// optionnels
// les paramètres sont ajoutés à l'URL sous forme de query string
// si le paramètre est un objet, il est converti en chaine de caractère
// en utilisant JSON.stringify
// exemple :
// url('api/v1/users', {name: 'toto', age: 25})
// -> http://localhost:8000/api/v1/users?name=toto&age=25
var url = (urlRelative, params = {}) => {
  const url = new URL(`${config.URL_APPLICATION}/${urlRelative}`);
  Object.keys(params)
    .filter((key) => ![null, undefined].includes(params[key]))
    .forEach(
      key => isObject(params[key])
        // si la clé est un 'objet' ou dictionnaire
        // -> on le renvoie sous forme de chaine de caractère
        ? url.searchParams.append(key, JSON.stringify(params[key]))
        // sinon on le traite de manière 'classique'
        : url.searchParams.append(key, params[key]));
  return url;
};

// fonction qui permet de gérer les erreurs
// lors de l'appel à une API
// elle affiche un message d'erreur dans la console
// et renvoie une erreur
var fail = msg => {
  console.error(`apiRequest fail : ${msg}`);
};

// fonction qui permet de faire une requête à une API
// elle prend en paramètre la méthode HTTP (GET, POST, PATCH, DELETE)
// l'URL relative de l'API ex : 'api/v1/users'
// les options de la requête (paramètres, données à envoyer)
// et le store (pour gérer les requêtes en cours) 
// elle renvoie une promesse qui sera résolue en cas de succès ou rejetée en cas d'erreur 
// elle gère également les requêtes en cours pour éviter de faire
// plusieurs requêtes identiques en même temps
// elle gère également les requêtes POST qui envoient des fichiers
// dans ce cas, les données sont envoyées sous forme de FormData
// sinon elles sont envoyées sous forme de JSON


var apiRequest = (method, urlRelative, options = {}, $store = null) => {

  // on construit l'URL complète de l'API
  const url_ = url(urlRelative, options.params);

  
  let request = null;
  // on initialise commit à false
  let commit;
  // on vérifie si la requête est en cours
  if (method == "GET" && $store) {
    // on récupère la requête en cours
    request = $store.getters.pendings(url_.href);
    // si la requête est en cours, on ne la refait pas
    if (!request) {
      commit = true;
    }
  }

  // on crée une nouvelle promesse
  request =
    request ||
    new Promise((resolve, reject = fail) => {
      var fetchOptions = {
        method,
        credentials: "include"
      };

      // on ajoute les headers
      if (["POST", "PATCH"].includes(method)) {
        const postOptions = {};
        // si les données contiennent un fichier
        if (Object.values(options.postData).some(d => d instanceof File)) {
          var data = new FormData();
          // on ajoute les données
          for (const [key, value] of Object.entries(options.postData || {})) {
            data.append(key, value);
          }
          postOptions.body = data;
        } else { // si les données ne contiennent pas de fichier
          postOptions.body = JSON.stringify(options.postData || {});
          postOptions.headers = {
            Accept: "application/json, text/plain, */*",
            "Content-Type": "application/json"
          };
        }
        // on ajoute les options de la requête POST
        fetchOptions = { ...fetchOptions, ...postOptions };
      }

      // on fait la requête, 
      fetch(url_, fetchOptions).then(
        response => {
          if (method == "GET" && $store) {
            $store.commit("removePending", url_.href);
          } // remove pending

          const acceptedStatus = options.accpetedStatus || [200];
          if (acceptedStatus.includes(response.status)) { // si la requête a réussi
            // on renvoie la réponse
            response.json().then(
              json => {
                resolve(json);
              },
              error => {
                reject(error);
              }
            );
          } else { // si la requête a échoué
            if (response.json) {
              response.json().then(
                json => {
                  reject(json);
                },
                error => {
                  reject(error);
                }
              );
            } else {
              reject(response);
            }
          }
        },

        // en cas d'erreur
        msg_fail => {
          if (method == "GET" && $store) {
            // on supprime la requête en cours
            $store.commit("removePending", url_.href);
          } 
          // on affiche un message d'erreur
          console.error(`Erreur dans apiRequest ${urlRelative} ${msg_fail}`);
          reject(msg_fail);
        }
      );
    });

  if (commit) {
    $store.commit("addPending", {
      api: url_.href,
      request
    });
  }

  return request;
};

export { apiRequest, url,  STORE };
