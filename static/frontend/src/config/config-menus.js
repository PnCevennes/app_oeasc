export const configMenus = {
  listLeftMenu: [
    {
      label: 'Accueil',
      icon: 'home',
      to: '/',
    },
    {
      label: "L'observatoire",
      icon: 'notes',
      subList: [
        {
          label: 'Présentation',
          to: '/observatoire/presentation'
        },
        {
          label: 'Justification',
          to: '/observatoire/justification'
        },

        {
          label: 'Objectifs',
          to: '/observatoire/objectifs'
        },
        {
          label: 'Périmètre et zonage',
          to: '/observatoire/perimetre'
        },
        {
          label: 'Contenu',
          to: '/observatoire/contenu'
        }
      ]
    },
    {
      label: "Le système d'alerte",
      icon: "report_problem",
      subList: [
        {
          label: 'Présentation',
          to: '/declaration/systeme_alerte'
        },
        {
          label: 'Les dégâts de grand gibier',
          to: '/declaration/degat_grand_gibier'
        },
        {
          label: 'Alertes déclarées',
          to: '/declaration/liste'
        },
        {
          label: 'Je signale des dégâts en forêt',
          to: '/declaration/signaler_degat_explication',
        }
      ]
    },
    {
      label: 'Résultats',
      icon: 'bar_chart',
      subList: [
        {
          label: "Dégâts forestiers (système d'alerte)"
        }
      ]
    }
  ],
  listTopMenu: [
    {
      label: '',
      icon: 'home',
      id: 'tab-home',
      to: '/'
    },
    {
      label: "L'observatoire",
      id: 'tab-presentation',
      to: '/content/presentation'
    }
  ],
  userMenu: [
    {
      name: 'login',
      label: 'Connexion',
      to: '/login'
    },
    {
      name: 'logout',
      label: 'Déconnexion',
      to: '/logout'
    },
    {
      name: 'user',
      label: 'Espace utilisateur',
      to: '/user'
    }

  ]
};
