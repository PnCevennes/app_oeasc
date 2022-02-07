export default {
  accueil: {
    name: "page.accueil"
  },
  actualite: {
    name: "actualite.index"
  },
  observatoire: {
    label: "L'Observatoire",
    icon: "fa-tree",
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
  informations: {
    icon: "not_listed_location",
    label: "En savoir plus ...",
    names: ["page.documentation", "page.contact", "page.partenaires"]
  },

  user: {
    label: ({ $store }) =>
      $store.getters.isAuth ? $store.getters.nomComplet : "Utilisateur",
    icon: ({ $store }) =>
      $store.getters.isAuth ? "mdi-account-check" : "mdi-account-cancel",
    disabled: ({ $store }) => !$store.getters.isAuth,
    names: [
      "user.login",
      "user.logout",
      "user.creer_utilisateur",
      "user.espace_utilisateur"
    ]
  },

  admin: {
    label: "Administration",
    icon: "fa-cog",
    hidden: ({ $store }) => $store.getters.droitMax < 5,
    names: ["user.admin", "commons.admin", "in.admin", "chasse.admin"]
  },

  dev: {
    icon: "engineering",
    label: "DEV",
    names: ["restitution.test", "restitution2.test"],
    hidden: ({ $store }) => $store.getters.droitMax < 5
  },

  resultats: {
    icon: "show_chart",
    label: "Résultats des suivis",
    names: ["resultats.declarations", "resultats.in"]
  },

  chasse: {
    icon: "fa-cog",
    label: 'Chasse',
    names: ['chasse.saisie', 'chasse.admin', 'chasse.bilan', 'chasse.exports'],
    hidden: ({ $store }) => $store.getters.droitMax < 5

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
