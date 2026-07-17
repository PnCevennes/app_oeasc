const ROUTE = [
  {
    path: '/restitution/test',
    label: 'Restitution - tableau de bord',
    name: 'restitution.test',
    parent: 'restitution',
    access: 1,
    hideTitle: true,
    component: () => import('./restitution-dashboard.vue'),
  },
  {
    path: '/restitution',
    content: 'restitution',
    name: 'restitution',
    label: 'Restitution',
    parent: 'page.accueil',
    type: 'page',
  },
];

const STORE = {
  state: {
    _restitutionDataCount: {},
  },
  getters: {
    restitutionDataCount: (state) => (dataType) => {
      return state._restitutionDataCount[dataType];
    },
  },
  mutations: {
    restitutionDataCount: (state, { dataType, count }) => {
      // Vue 3 : la réactivité Proxy gère nativement l'ajout de propriétés, plus besoin de Vue.set
      state._restitutionDataCount[dataType] = count;
    },
  },
};

export { ROUTE, STORE };
