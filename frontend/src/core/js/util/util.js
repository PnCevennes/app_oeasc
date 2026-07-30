/* Quelques fonctions simples */

// import moment from "moment";
import fastDeepEqual from 'fast-deep-equal';
/** Functions utiles */

/**
 * Fonction de comparaison d'objets en profondeur.
 * Utilise la bibliothèque fast-deep-equal pour vérifier si deux objets sont identiques,
 * en comparant récursivement toutes leurs propriétés, même imbriquées.
 * Utile pour détecter des changements dans des structures complexes (ex : états Vuex, props, etc.).
 * @param {*} obj1 - Le premier objet à comparer (peut être de n'importe quel type).
 * @param {*} obj2 - Le deuxième objet à comparer (peut être de n'importe quel type).
 * @returns {boolean} - Retourne true si les deux objets sont strictement égaux en profondeur, false sinon.
 */
const fde = (obj1, obj2) => {
  return fastDeepEqual(obj1, obj2);
};

/**
 * Fonction de copie d'objet.
 * Cette fonction permet de réaliser une copie profonde d'un objet en utilisant les méthodes
 * JSON.stringify et JSON.parse. Elle est utile pour dupliquer des objets complexes (avec des
 * propriétés imbriquées) sans conserver de référence à l'objet original.
 * Attention : cette méthode ne copie pas les fonctions, les objets Date, les Map, Set, etc.
 * Elle est adaptée pour des objets simples (données sérialisables en JSON).
 * @param {*} obj - L'objet à copier (peut être de n'importe quel type).
 * @returns {*} - Retourne une copie profonde de l'objet, ou null si l'objet est falsy (null, undefined, etc.).
 */
const jsoncopy = (obj) => {
  return obj ? JSON.parse(JSON.stringify(obj)) : null;
};

/**
 * Fonction de copie d'objet profonde, récursive.
 * Cette fonction permet de dupliquer entièrement un objet ou un tableau, sans conserver de référence à l'original.
 * Elle gère les tableaux et les objets imbriqués, mais ne copie pas les fonctions, les objets spéciaux (Date, Map, Set, etc.).
 * Utile pour cloner des structures complexes (ex : états Vuex, props, etc.) sans effet de bord.
 * @param {*} obj - L'objet ou le tableau à copier (peut être de n'importe quel type).
 * @returns {*} - Retourne une copie profonde de l'objet ou du tableau, ou la valeur elle-même si ce n'est ni un objet ni un tableau.
 */
const copy = (obj) => {
  // Si l'objet est un tableau, on crée un nouveau tableau en copiant récursivement chaque élément
  if (Array.isArray(obj)) {
    return obj.map((item) => copy(item));
    // Si c'est un objet (et non null), on crée un nouvel objet et on copie chaque propriété récursivement
  } else if (typeof obj === 'object' && obj) {
    const out = {};
    for (const key in obj) {
      // Copie profonde de chaque propriété
      out[key] = copy(obj[key]);
    }
    return out;
  } else {
    // Si ce n'est ni un objet ni un tableau (ex : nombre, chaîne, booléen), on retourne la valeur telle quelle
    return obj;
  }
};

/**
 * Fonction de tri de dates.
 * Cette fonction compare deux dates, qui peuvent être sous forme de chaînes au format "JJ/MM/AAAA"
 * ou sous une autre forme comparable (ex : timestamp, chaîne ISO, etc.).
 * Elle retourne :
 *   - 0 si les deux dates sont égales,
 *   - -1 si la première date (a) est antérieure à la seconde (b),
 *   - 1 si la première date (a) est postérieure à la seconde (b).
 *
 * @param {*} a - La première date à comparer. Peut être une chaîne "JJ/MM/AAAA" ou une autre valeur comparable.
 * @param {*} b - La deuxième date à comparer. Même format que a.
 * @returns {number} - 0 si égalité, -1 si a < b, 1 si a > b.
 */
const sortDate = (a, b) => {
  // Si l'une des deux valeurs est falsy (null, undefined, etc.), retourne 0 (égalité)
  if (!(a && b)) return 0;
  // Si a est falsy mais b est défini, a est considéré plus petit
  if (!a) return -1;
  // Si b est falsy mais a est défini, a est considéré plus grand
  if (!b) return 1;
  // Si la date est au format "JJ/MM/AAAA"
  if (a.includes('/')) {
    // On découpe les chaînes pour extraire jour, mois, année
    const date_a = a.split('/');
    const date_b = b.split('/');
    // On compare d'abord l'année, puis le mois, puis le jour
    return date_a[2] == date_b[2]
      ? date_a[1] == date_b[1]
        ? date_a[0] == date_b[0]
          ? 0 // Les dates sont identiques
          : Number(date_a[0]) - Number(date_b[0]) // Différence sur le jour
        : Number(date_a[1]) - Number(date_b[1]) // Différence sur le mois
      : Number(date_a[2]) - Number(date_b[2]); // Différence sur l'année
  } else {
    // Si ce n'est pas une chaîne au format "JJ/MM/AAAA", on compare directement les valeurs
    return a == b ? 0 : a < b ? -1 : 1;
  }
};

/**
 * Met la première lettre en majuscule pour le nommage des stores
 * @param {*} s
 * @returns
 */
const upFirstLetter = (s) => {
  return s.charAt(0).toUpperCase() + s.slice(1);
};

/**
 * Vérifie si une valeur est un objet (et non un tableau).
 * @param {*} obj - La valeur à tester.
 * @returns {boolean} - Retourne true si c'est un objet, false sinon.
 */
const isObject = (obj) => {
  return Object(obj) === obj && !Array.isArray(obj);
};

/**
 * Convertit une chaîne en snake_case.
 * @param {*} str - La chaîne à convertir.
 * @returns {string} - La chaîne convertie en snake_case.
 */
const camelToSnakeCase = (str) => str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);

/**
 * Arrondit un nombre à un certain nombre de décimales.
 * @param {number} x - Le nombre à arrondir.
 * @param {number} dec - Le nombre de décimales à conserver.
 * @returns {number} - Le nombre arrondi.
 */
const round = function (x, dec) {
  if (x == 0) return 0;
  return Math.floor(x * 10 ** dec) / 10 ** dec;
};

/**
 * Ajoute l'unité 'px' à la fin d'une valeur si elle n'est pas déjà présente.
 * Utile pour les champs de saisie de largeur/hauteur qui acceptent soit un entier (ex: '500'),
 * soit une valeur déjà suffixée par l'utilisateur (ex: '500px').
 * @param {*} value - La valeur saisie.
 * @returns {*} - La valeur suivie de 'px', ou la valeur telle quelle si vide ou déjà suffixée.
 */
const addPxSuffix = (value) => {
  if (value === null || value === undefined || value === '') return value;
  const str = String(value).trim();
  return /px$/i.test(str) ? str : `${str}px`;
};

export {
  copy,
  sortDate,
  upFirstLetter,
  camelToSnakeCase,
  round,
  isObject,
  jsoncopy,
  fde,
  addPxSuffix,
};
