import login from './login';
import logout from './logout';

const ROUTE = [
  {
    path: '/login',
    label: 'login',
    access: [],
    name: 'login',
    component: login
  },
    {
    path: '/logout',
    label: 'logout',
    access: [],
    name: 'logout',
    component: logout
  },
];

const STORE = {
  state: {
    user: null
  },
  mutations: {
    /**
     * Set user
     */
    setUser(state, userData) {
      state.user = userData;
    }
  },
  getters: {
    /**
     * Get user
     */
    user(state) {
      return state.user;
    },
    /**
     * Check if user is connected
     */
    isAuth(state) {
      return !!(state.user && state.user.id_role);
    },
    /**
     * Nom complet
     */
    nom_complet(state) {
      return (
        state.user &&
        `${state.user.nom_role}  ${state.user.prenom_role || ''}`.trim()
      );
    },
    /**
     * User permissions
     */
    droit_max(state) {
      return (state.user && state.user.id_droit_max) || 0;
    }
  },
  actions: {}
}

export { ROUTE, STORE, login };
