const menus = {
  accueil: {
    name: "page.accueil",
    labelDrawer: "Accueil"
  },
  observatoire: {
    name: "observatoire.presentation",
    labelDrawer: "L'Observatoire",
    names: [
      "observatoire.justification",
      "observatoire.objectifs",
      "observatoire.perimetre",
      "observatoire.contenu"
    ]
  },
  systeme_alerte: {
    labelDrawer: "Le système d'alerte",
    name: "declaration.systeme_alerte_top",
    names: [
      "declaration.systeme_alerte",
      "declaration.degat_grand_gibier",
      "declaration.signaler_degat_explication",
      "declaration.liste_declarations"
    ]
  },
  user: {
    name: "user.top",
    labelDrawer: "Utilisateur",
    names: [
      "user.login",
      "user.logout",
      "user.creer_utilisateur",
      "user.espace_utilisateur",
      "user.gerer_utilisateurs"
    ]
  },
  test: {
    name: "test",
    labelDrawer: "Test",
    names: ["test.map"],
    condition: ({ $store }) => $store.getters.droitMax >= 5
  },
  indices_nocturnes: {
    name: 'in.index',
    names: ['in.test'],
    condition: ({ $store }) => $store.getters.droitMax >= 5
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

  const processRoute = {
    condition: true
  };
  for (const key of Object.keys(route)) {
    if (key == "component") {
      continue;
    }
    processRoute[key] =
      typeof route[key] == "function" ? route[key]({ $store }) : route[key];
  }
  return processRoute;
};

const configMenu = function(menuName, { $store, $router }) {
  const menu = menus[menuName];
  const condition = !menu.condition || menu.condition({$store});
  return {
    ...menu,
    ...processRouteName(menu.name, { $store, $router }),
    menus: (menu.names || [])
    .map(name => processRouteName(name, { $store, $router }))
    .filter(menu => menu.condition),
    condition,
  };
};

export { configMenu, menus };
