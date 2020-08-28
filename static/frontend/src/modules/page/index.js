import page from "./page";

const ROUTE = [
  {
    name: "page.accueil",
    path: "/",
    icon: "home",
    label: "Accueil",
    type: "page",
    content: 'accueil',
  },

  {
    name: "observatoire.presentation",
    path: "/observatoire/presentation",
    label: "Présentation",
    content: 'presentation',
    parent: "page.accueil",
    type: "page"
  },

  {
    name: "observatoire.justification",
    path: "/observatoire/justification",
    label: "Justification",
    content: 'justification',
    parent: "observatoire.presentation",
    type: "page"
  },

  {
    name: "observatoire.objectifs",
    path: "/observatoire/objectifs",
    label: "Objectifs",
    content: 'objectifs',
    parent: "observatoire.presentation",
    type: "page"
  },

  {
    name: "observatoire.perimetre",
    path: "/observatoire/perimetre",
    content: 'perimetre',
    label: "Périmètre et zonage",
    parent: "observatoire.presentation",
    type: "page"
  },

  {
    name: "observatoire.contenu",
    path: "/observatoire/contenu",
    label: "Contenu",
    content: 'contenu',
    parent: "observatoire.presentation",
    type: "page"
  },

  {
    name: 'page.documentation',
    path: '/page/documentation',
    label: "Documentation",
    content: 'documentation',
    parent: "page.accueil",
    type: "page"
  },

  {
    name: 'page.contact',
    path: '/page/contact',
    label: "Contact",
    content: 'contact',
    parent: "page.accueil",
    type: "page"
  },

  {
    path: '/page/partenaires',
    name: 'page.partenaires',
    label: "Partenaires",
    content: 'partenaires',
    parent: "page.accueil",
    type: "page"
  },

  {
    name: 'resultats.index',
    path: '/resultats',
    label: 'Résultats des alertes',
    content: 'resultats',
    parent: 'resultats.resultats',
    type: 'page'
  }

];

export { ROUTE, page };
