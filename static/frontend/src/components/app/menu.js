const menus = {
  accueil: {
    name: "page.accueil"
  },
  observatoire: {
    label: "L'Observatoire",
    icon: "not_listed_location",
    labelDrawer: "L'Observatoire",
    names: [
      "observatoire.presentation",
      "observatoire.justification",
      "observatoire.objectifs",
      "observatoire.perimetre",
      "observatoire.contenu"
    ]
  },
  systeme_alerte: {
    label: "Le système d'alerte",
    icon: "report_problem",
    names: [
      "declaration.systeme_alerte",
      "declaration.degat_grand_gibier",
      "declaration.signaler_degat_explication",
      "declaration.liste_declarations"
    ]
  },
  
  user: {
    label: ({ $store }) => $store.getters.isAuth ? $store.getters.nomComplet : 'Utilisateur',
    icon: ({ $store }) =>
      $store.getters.isAuth ? "mdi-account-check" : "mdi-account-cancel",
    disabled: ({ $store }) => !$store.getters.isAuth,
    names: [
      "user.login",
      "user.logout",
      "user.creer_utilisateur",
      "user.espace_utilisateur",
    ]
  },


  admin: {
    label: 'Administration',
    icon: 'fa-cog',
    hidden: ({$store}) => ($store.getters.droitMax <= 5),
    names: ["in.tableau", "in.realisation","in.realisations",  "user.gerer_utilisateurs"]
  },

  dev: {
    icon: 'engineering',
    label: 'DEV',
    names: ["restitution.test"],
    hidden: ({$store}) => ($store.getters.droitMax <= 5)
  },

  resultats: {
    icon: 'show_chart',
    label: 'Résultats des suivis',
    names: ["resultats.declarations", "resultats.in"]
  },

  documentation: {
    name: "page.documentation"
  },
  contact: {
    name: "page.contact"
  },
  partenaires: {
    name: "page.partenaires"
  }

};

const processRouteName = function(routeName, { $store, $router }) {
  const route = $router.options.routes.find(route => route.name == routeName);

  const processRoute = {};

  for (const key of Object.keys(route)) {
    if (key == "component") {
      continue;
    }
    processRoute[key] =
      typeof route[key] == "function" ? route[key]({ $store }) : route[key];

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
  let menuOut = {...menu};
  if (menu.name) {
    menuOut = { ...menu, ...processRouteName(menu.name, { $store, $router }) };
  }
  for (const key of Object.keys(menuOut)) {
    menuOut[key] =
      typeof menuOut[key] === "function" ? menuOut[key]({ $store }) : menuOut[key];
  }
  return menuOut;
};

const configMenu = function(menuName, { $store, $router }) {
  const menu = processMenu(menus[menuName], { $store, $router });

  return {
    ...menu,
    menus: (menu.names || [])
      .map(name => processRouteName(name, { $store, $router }))
      .filter(menu => !menu.hidden)
  };
};

export { configMenu, menus };
