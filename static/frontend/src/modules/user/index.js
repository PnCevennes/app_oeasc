import login from "./login";
import userPage from "./user-page";
import createUser from "./create-user";
import manageUser from "./manage-user";
import changePassword from "./change-password";
import logout from "./logout";
import { apiRequest } from "@/core/js/data/api.js";

const ROUTE = [
  {
    path: "/login",
    label: "login",
    name: "login",
    component: login
  },
  {
    path: "/logout",
    label: "logout",
    name: "logout",
    component: logout
  },
  {
    path: "/user/espace_utilisateur",
    label: "user",
    meta: {
      access: 1
    },
    name: "user",
    component: userPage
  },
  {
    path: "/user/creer_utilisateur",
    label: "user",
    name: "create_user",
    component: createUser
  },
  {
    path: "/user/gerer_utilisateurs",
    label: "user",
    name: "manage_user",
    meta: {
      access: 4 
    },
    component: manageUser
  },

  {
    path: "/user/change_password",
    label: "user",
    name: "user",
    component: changePassword
  }
];

const STORE = {
  state: {
    _user: null,
    _redirectOnLogin: null,
    _organismes: [],
    _users: [],
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
    },
    organismes(state, organismes) {
      state._organismes = organismes;
    },
    users(state, users) {
      state._users = users;
    }
  },

  getters: {
    users: state => state.users,

    organismes: state => {
      return state._organismes;
    },

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
      if (!state._user) {
        return false;
      }

      // check date
      const date = new Date(state._user.expires);
      const date1 = new Date(date.toString().split("GMT")[0] + "GMT");
      const now = new Date();
      return !!(state._user && state._user.id_role && date1 >= now);
    },
    /**
     * Nom complet
     */
    nomComplet(state) {
      return STORE.getters.isAuth(state)
        ? `${state._user.nom_role}  ${state._user.prenom_role || ""}`.trim()
        : null;
    },
    /**
     * User permissions
     */
    droitMax(state) {
      return (STORE.getters.isAuth(state) && state._user.id_droit_max) || 0;
    }
  },
  actions: {
    organismes({ commit, state }) {
      return new Promise((resolve, reject) => {
        const organismes = STORE.getters.organismes(state); 
        if (organismes && organismes.length) {
          resolve(organismes);
        }
        apiRequest("GET", "api/user/organismes").then(
          apiData => {
            commit("organismes", apiData);
            resolve(apiData);
          },
          error => {
            reject(error);
          }
        );
      });
    },
    userInfo({ commit }, id_role) {
      return new Promise((resolve, reject) => {
        commit;
        apiRequest("GET", `api/user/user_information/${id_role}`).then(
          apiData => {
            resolve(apiData);
          },
          error => {
            reject(error);
          }
        );
      });
    },
    users({commit}) {
      return new Promise((resolve, reject) => {
        apiRequest("GET", `api/user/users`).then(
          apiData => {
            commit('users', apiData);
            resolve(apiData);
          },
          error => {
            reject(error);
          }
        );
      });
    }
  }
};

export { ROUTE, STORE, login };
