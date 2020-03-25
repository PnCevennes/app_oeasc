export const configMenus = {
  listLeftMenu: [
    {
      label: "L'observatoire",
      icon: 'notes',
      subList: [
        {
          label: 'Présentation',
          to: '/content/presentation'
        },
        {
          label: 'Justification',
          to: '/content/justification'
        },

        {
          label: 'Objectifs',
          to: '/content/objectifs'
        },
        {
          label: 'Périmètre et zonage',
          to: '/content/perimetre'
        },
        {
          label: 'Contenu',
          to: '/content/contenu'
        }
      ]
    },
    {
      label: "Le système d'alerte",
      subList: [
        {
          label: 'Les dégâts de gronad gibier',
          to: '/content/degat_grand_gibier'
        },
        {
          label: 'Alertes déclarées'
        },
        {
          label: 'Je signales des dégâts en forêt'
        }
      ]
    },
    {
      label: 'Résultats',
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
