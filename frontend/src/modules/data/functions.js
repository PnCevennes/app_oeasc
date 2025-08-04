/**
 * Construit une chaîne de caractères à partir des données récupérées via un getter du STORE.
 *
 * @param {Object} STORE - L'objet STORE contenant les getters pour accéder aux données.
 * @param {Object} state - L'état actuel utilisé par le getter pour récupérer les données.
 * @param {string} getterKey - La clé du getter à utiliser dans STORE.getters.
 * @param {number|string|Array} n - Identifiant(s) des éléments à récupérer. Peut être un nombre, une chaîne ou un tableau d'identifiants.
 * @param {string} dataKey - La clé de la donnée à extraire de chaque élément récupéré.
 * @returns {string} Une chaîne de caractères composée des valeurs extraites, séparées par des virgules. Retourne une chaîne vide si aucun identifiant n'est fourni.
 *
 * @description
 * Cette fonction est généralement utilisée pour afficher une liste de valeurs (par exemple, des noms ou des titres)
 * à partir d'une collection d'objets stockés dans le STORE, en fonction d'un ou plusieurs identifiants.
 * Elle est utile dans les cas où l'on souhaite présenter une synthèse textuelle de plusieurs éléments sélectionnés.
 */
const dataString = function(STORE, state, getterKey, n, dataKey) {
  if (!n || (Array.isArray(n) && !n.length)) {
    return "";
  }

  let nArray = Array.isArray(n) ? n : [n];
  return nArray
    .map(id => {
      const data = STORE.getters[getterKey](state)(id);
      return ((data && data[dataKey]) || "");
      // return ((data && data[dataKey]) || "").toLowerCase();
    })
    .join(", ");
};

export { dataString };
