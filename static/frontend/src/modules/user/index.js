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
    _user: null,
    _redirectOnLogin: null
  },
  mutations: {
    /**
     * Set user
     */
    user(state, userData) {
      state._user = userData;
    },
    redirectOnLogin(state, path) {
      state._redirectOnLogin = path;
    }
  },
  getters: {
    redirectOnLogin(state) {
      return state._redirectOnLogin;
    },
    /**
     * Get user
     */
    user(state) {
      return state._user;
    },
    /**
     * Check if user is connected
     */
    isAuth(state) {
      if(! state._user) {
        return false;
      }

      // check date
      const date = new Date(state._user.expires);
      const date1 = new Date(date.toString().split('GMT')[0] + 'GMT');
      const now = new Date();
      return !!(state._user && state._user.id_role && date1 >= now);
    },
    /**
     * Nom complet
     */
    nom_complet(state) {
      return (
        STORE.getters.isAuth(state) 
          ? `${state._user.nom_role}  ${state._user.prenom_role || ''}`.trim()
          : null
      );
    },
    /**
     * User permissions
     */
    droit_max(state) {
      return (STORE.getters.isAuth(state) && state._user.id_droit_max) || 0;
    }
  },
  actions: {}
}

export { ROUTE, STORE, login };
