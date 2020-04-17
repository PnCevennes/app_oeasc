import page from "./page";

const pagesConfig = {
  accueil: {
    path: "/"
  },

  presentation: {
    path: "/observatoire/presentation"
  },

  justification: {
    path: "/observatoire/justification"
  },

  objectifs: {
    path: "/observatoire/objectifs"
  },

  perimetre: {
    path: "/observatoire/perimetre"
  },

  contenu: {
    path: "/observatoire/contenu"
  },

  degat_grand_gibier: {
    path: "/declaration/degat_grand_gibier"
  },

  systeme_alerte: {
    path: "/declaration/systeme_alerte"
  },

  signaler_degat_explication: {
    path: "/declaration/signaler_degat_explication",
    access: 1,
  }

};

const ROUTE = [];

for (const [key, pageConfig] of Object.entries(pagesConfig)) {
  ROUTE.push({
    name: key,
    meta: {
      content: pageConfig.content || key,
      access: pageConfig.access,
    },
    path: pageConfig.path || `/page/${key}`,
    component: page
  });
}

export { ROUTE };
