import page from "./page";

const pagesConfig = {
  accueil: {
    path: "/",
    icon: "home",
    label: 'Accueil',
    name: 'page.accueil',
  },

  presentation: {
    path: "/observatoire/presentation",
    name: "observatoire.presentation",
    label: "Présentation",
    icon: "notes",
    parent: 'page.accueil',
  },

  justification: {
    path: "/observatoire/justification",
    name: "observatoire.justification",
    label: "Justification",
    parent: "observatoire.presentation"
  },

  objectifs: {
    path: "/observatoire/objectifs",
    name: "observatoire.objectifs",
    label: "Objectifs",
    parent: "observatoire.presentation"

  },

  perimetre: {
    path: "/observatoire/perimetre",
    name: "observatoire.perimetre",
    label: "Périmètre et zonage",
    parent: "observatoire.presentation"

  },

  contenu: {
    path: "/observatoire/contenu",
    name: "observatoire.contenu",
    label: "Contenu",
    parent: "observatoire.presentation"
  },

  degat_grand_gibier: {
    path: "/declaration/degat_grand_gibier",
    name: "declaration.degat_grand_gibier",
    label: "Les dégâts de grand gibier",
    parent: 'declaration.systeme_alerte'
  },

  systeme_alerte_top: {
    path: "/declaration/systeme_alerte",
    name: "declaration.systeme_alerte_top",
    label: "Signaler des dégâts en forêt",
    content: 'systeme_alerte',
    icon: "report_problem",
    parent: 'page.accueil'
  },

  systeme_alerte: {
    path: "/declaration/systeme_alerte",
    name: "declaration.systeme_alerte",
    label: "Le systême d'alerte",
    parent: 'page.accueil'
  },

  signaler_degat_explication: {
    path: "/declaration/signaler_degat_explication",
    name: "declaration.signaler_degat_explication",
    label: "Je signale des dégâts en forêt",
    parent: 'declaration.systeme_alerte',
    access: 1
  },

  documentation: {
    label: "Documentation",
    parent: 'page.accueil'
  },

  contact: {
    label: "Contact",
    parent: 'page.accueil'
  },

  partenaires: {
    label: "Partenaires",
    parent: 'page.accueil'
  },



};

const ROUTE = [];

for (const [key, pageConfig] of Object.entries(pagesConfig)) {
  const defaultConfig = {
    name: `page.${key}`,
    content: pageConfig.content || key,
    path: `/page/${key}`,
    component: page
  };
  ROUTE.push({
    ...defaultConfig,
    ...pageConfig
  });
}

export { ROUTE };
