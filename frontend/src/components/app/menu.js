// Fonctions de permettant de traiter les données du fichier `config/menu.js`

import { menus } from '@/config/menu.js'


const processRouteName = function(routeName, { $store, $router }) {
  // Fonction qui premet de retourner les données relatives à une route
  //    à partir de son nom

  // Récupération de la définition de la route à partir de son nom
  const route = $router.options.routes.find(route => route.name == routeName);

  // Object qui condiendra les information de la route
  const processRoute = {};

  if (!route) {
    // console.error(`route ${routeName} non définie`)
    return {}
  }

  for (const key of Object.keys(route)) {
    if (key == "component") {
      continue;
    }
    // Si c'est une fonction, passage du store à la fonction
    processRoute[key] =
      typeof route[key] == "function" ? route[key]({ $store }) : route[key];
    // ? pourquoi traiter path
    if (key == 'path') {
      const paths = route[key].split('/');
      if (paths[paths.length -1 ][0]==':') {
        paths[paths.length -1 ] = "";

      }
      route[key] = paths.join('/');
    }
  }



  return processRoute;
};

const processMenu = function(menu, { $store, $router }) {
  // Fonction qui traite les données contenu dans un menu
  let menuOut = {...menu};
  // Si le menu n'a qu'une seule route => traitement
  if (menu.name) {
    menuOut = { ...menu, ...processRouteName(menu.name, { $store, $router }) };
  }
  for (const key of Object.keys(menuOut)) {
    // Si c'est une fonction, passage du store à la fonction
    menuOut[key] =
      typeof menuOut[key] === "function" ? menuOut[key]({ $store }) : menuOut[key];
  }
  return menuOut;
};

const configMenu = function(menuName, { $store, $router }) {
  // Fonction qui traite une entré de menu du fichier  `config/menu.js`

  // Traitement du niveau 0 de l'objet
  //    - si fonction
  //    - si name (route unique)
  const menu = processMenu(menus[menuName], { $store, $router });


  return {
    ...menu,
    menus: (menu.names || []) // Si menu à des sous éléments => traitement de ces derniers
      .map(name => processRouteName(name, { $store, $router }))
      .filter(menu => !menu.hidden)
  };
};

export { configMenu, menus };
