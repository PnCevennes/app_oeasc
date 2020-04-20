import page from "./page";

const pagesConfig = {
  accueil: {
    path: "/",
    icon: "home"
  },

  presentation: {
    path: "/observatoire/presentation",
    name: "observatoire.presentation",
    label: "Présentation",
    icon: "notes"
  },

  justification: {
    path: "/observatoire/justification",
    name: "observatoire.justification",
    label: "Justification"
  },

  objectifs: {
    path: "/observatoire/objectifs",
    name: "observatoire.objectifs",
    label: "Objectifs"
  },

  perimetre: {
    path: "/observatoire/perimetre",
    name: "observatoire.perimetre",
    label: "Périmètre et zonage"
  },

  contenu: {
    path: "/observatoire/contenu",
    name: "observatoire.contenu",
    label: "Contenu"
  },

  degat_grand_gibier: {
    path: "/declaration/degat_grand_gibier",
    name: "declaration.degat_grand_gibier",
    label: "Les dégâts de grand gibier",
  },

  systeme_alerte_top: {
    path: "/declaration/systeme_alerte",
    name: "declaration.systeme_alerte_top",
    label: "Signaler des dégâts en forêt",
    content: 'systeme_alerte',
    icon: "report_problem",
  },

  systeme_alerte: {
    path: "/declaration/systeme_alerte",
    name: "declaration.systeme_alerte",
    label: "Le systême d'alerte",
  },

  signaler_degat_explication: {
    path: "/declaration/signaler_degat_explication",
    name: "declaration.signaler_degat_explication",
    label: "Je signale des dégâts en forêt",
    access: 1
  },

  documentation: {
    label: "Documentation",
  },

  contact: {
    label: "Contact",
  },

  partenaires: {
    label: "Partenaires",
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
