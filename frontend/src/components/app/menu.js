// Fonctions de permettant de traiter les données du fichier `config/menu.js`

import { menus } from '@/config/menu.js';

/**
 * Traite le nom d'une route et retourne les informations associées à cette route.
 *
 * @param {string} routeName - Le nom de la route à traiter. Si la valeur est '-', la fonction retourne simplement '-'.
 * @param {Object} context - Contexte contenant le store et le router.
 * @param {Object} context.$store - L'instance du store Vuex, utilisée pour passer aux fonctions de la route.
 * @param {Object} context.$router - L'instance du router Vue, utilisée pour accéder à la définition des routes.
 * @returns {Object|string} Un objet contenant les informations de la route (sauf le composant), ou une chaîne '-' pour les séparateurs, ou un objet vide si la route n'est pas définie.
 *
 * @description
 * - Si le nom de la route est '-', la fonction retourne ce séparateur pour gérer les dividers dans le menu.
 * - Recherche la définition de la route dans la configuration du router à partir de son nom.
 * - Pour chaque propriété de la route (sauf 'component'), si la propriété est une fonction, elle est appelée avec le store en paramètre.
 * - Pour la propriété 'path', si le dernier segment est un paramètre dynamique (commence par ':'), il est remplacé par une chaîne vide.
 * - Retourne un objet contenant les propriétés traitées de la route, ou un objet vide si la route n'existe pas.
 */
const processRouteName = function (routeName, { $store, $router }) {
  // Fonction qui premet de retourner les données relatives à une route
  //    à partir de son nom

  // pour traiter les divider (barre horizontale pour faire une séparation dans le menu)
  if (routeName == '-') {
    return routeName;
  }

  // Récupération de la définition de la route à partir de son nom
  const route = $router.options.routes.find((route) => route.name == routeName);

  // Object qui condiendra les information de la route
  const processRoute = {};

  if (!route) {
    // console.error(`route ${routeName} non définie`)
    return {};
  }

  for (const key of Object.keys(route)) {
    if (key == 'component') {
      continue;
    }
    // Si c'est une fonction, passage du store à la fonction
    processRoute[key] = typeof route[key] == 'function' ? route[key]({ $store }) : route[key];
    // ? pourquoi traiter path
    if (key == 'path') {
      const paths = route[key].split('/');
      if (paths[paths.length - 1][0] == ':') {
        paths[paths.length - 1] = '';
      }
      route[key] = paths.join('/');
    }
  }

  return processRoute;
};

/**
 * Traite les données d'un menu et enrichit ses propriétés.
 *
 * @param {*} menu - L'objet menu à traiter, provenant du fichier de configuration.
 * @param {*} param1 - Un objet contenant le store et le router de l'application.
 * @returns {Object} Un nouvel objet menu enrichi avec les propriétés de la route et les valeurs calculées.
 */
const processMenu = function (menu, { $store, $router }) {
  // On crée une copie superficielle du menu pour éviter de modifier l'original
  let menuOut = { ...menu };

  // Si le menu possède une propriété 'name', cela signifie qu'il correspond à une route unique
  // On enrichit alors le menu avec les propriétés de cette route
  if (menu.name) {
    menuOut = { ...menu, ...processRouteName(menu.name, { $store, $router }) };
  }

  // On parcourt toutes les propriétés du menu enrichi
  for (const key of Object.keys(menuOut)) {
    // Si la propriété est une fonction, on l'exécute en lui passant le store
    // Cela permet d'obtenir la valeur dynamique de la propriété
    menuOut[key] = typeof menuOut[key] === 'function' ? menuOut[key]({ $store }) : menuOut[key];
  }

  // On retourne l'objet menu enrichi et prêt à être utilisé dans l'application
  return menuOut;
};

/**
 *
 * @param {*} menuName
 * @param {*} param1
 * @returns
 */
/**
 * Configure et traite une entrée de menu à partir du fichier `config/menu.js`.
 *
 * Cette fonction gère le niveau 0 de l'objet menu :
 *   - Si l'entrée est une fonction, elle l'exécute.
 *   - Si l'entrée possède une propriété `name`, elle traite la route unique correspondante.
 * Elle retourne un objet menu enrichi, incluant la liste des sous-menus traités.
 *
 * @param {string} menuName - Le nom de l'entrée de menu à traiter.
 * @param {Object} context - Le contexte d'exécution.
 * @param {Object} context.$store - L'instance du store (état global de l'application).
 * @param {Object} context.$router - L'instance du routeur (navigation de l'application).
 * @returns {Object} Un objet représentant le menu configuré, incluant ses sous-menus filtrés (non cachés).
 */
const configMenu = function (menuName, { $store, $router }) {
  const menu = processMenu(menus[menuName], { $store, $router });

  return {
    ...menu,
    menus: (menu.names || []) // Si menu à des sous éléments => traitement de ces derniers
      .map((name) => processRouteName(name, { $store, $router }))
      .filter((menu) => !menu.hidden),
  };
};

export { configMenu, menus };
