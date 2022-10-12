// Pour ajouter un menu il faut :
//  Créer une définition de ce menu dans la variable `menus`
//  Puis spécifier son emplacement configAppBar ou configDrawerMenus

// Définition des menus
//    - label : Nom d'affichage du menu
//    - icon : Icone précédant le label
//    - disabled : Fonction indiquant si le menu doit être désactivé
//    - hidden : Fonction indiquant si le menu doit être affiché (en fonction des droits de l'utilisateur)
//    - name : Cas des menus sans liste déroulante => nom de la route du menu
//    - names : Cas des menus avec liste déroulante =>  listes des routes composants un menu

const menus = {
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
    names: [
      "resultats.index",
      "-",
      "chasse.restitution_gd_public",
      "resultats.declarations",
      "resultats.in",
      "chasse.restitution_indices_performances",
      "icia.restitution_gd_public",
      "degats_agricoles.restitution_gd_public",
      "sylviculture.restitution_diagnostics_sylvicoles",
      "sylviculture.restitution_suivi_peuplements_sensibles"
    ]
  },

  chasse: {
    icon: "fa-cog",
    label: 'Chasse',
    names: [
      "chasse.saisie",
      "chasse.admin",
      "chasse.bilan",
      "chasse.restitution_bilan_detaille",
      "chasse.exports"
    ],
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

// Configuration de l'affichage des menus sur la bare du haut
// rightMenus => menus alignés à droite
// leftMenus => menus alignés à gauche
const configAppBar = {
  rightMenus: ["informations", "user"],
  leftMenus: [
    "accueil",
    "actualite",
    "observatoire",
    "systeme_alerte",
    "resultats",
    "chasse"
  ],
};

// Configuration de l'affichage des menus sur le paneau latéral
const configDrawerMenus = [
  "accueil",
  "actualite",
  "observatoire",
  "systeme_alerte",
  "informations",
  "admin",
  "dev"
]

export { menus, configAppBar, configDrawerMenus }