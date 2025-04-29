
import login from "./login";
import {config} from '@/config/config.js';
import userPage from "./user-page";
import createUser from "./create-user";
import manageUser from "./manage-user";
import changePassword from "./change-password";
import logout from "./logout";
import { apiRequest } from "@/core/js/data/api.js";


// ROUTE: intègre les routes pour la connexion, l'inscription, la déconnexion et
// la gestion du mot de passe oublié, ainsi que le profil utilisateur.
// ROUTE vers l'administration des utilisateurs.
// LE STORE stocke les informations de l'utilisateur connecté et les informations
// sur les utilisateurs de l'application.


const ROUTE = [
  {
    path: "/login",
    label: "Connexion",
    icon: "mdi-login",
    name: "user.login",
    parent: 'page.accueil',
    component: login,
    hidden: ({$store}) => !!$store.getters.isAuth
  },
  {
    path: "/logout",
    label: "Déconnexion",
    name: "user.logout",
    icon: "mdi-logout",
    component: logout,
    hidden: ({$store}) => !$store.getters.isAuth
  },
  // {
  //   path: "/user/espace_utilisateur",
  //   access: 1,
  //   name: "user.top",
  //   component: userPage,
  //   parent: 'page.accueil',
  //   icon: ({$store}) => $store.getters.isAuth ? "mdi-account-check" : "mdi-account-cancel",
  //   disabled: ({$store}) => !$store.getters.isAuth,
  // },
  {
    path: "/user/espace_utilisateur",
    label: "Espace utilisateur",
    access: 1,
    icon: "mdi-account",
    name: "user.espace_utilisateur",
    parent: 'page.accueil',
    component: userPage,
    hidden: ({$store}) => !$store.getters.isAuth
  },
  {
    path: "/user/creer_utilisateur",
    label: "Inscription",
    icon: 'mdi-account-plus',
    name: "user.creer_utilisateur",
    parent: 'page.accueil',
    component: createUser,
    hidden: ({$store}) => !!$store.getters.isAuth
  },
  {
    path: "/user/gerer_utilisateurs",
    label: "Utilisateurs - gestion",
    name: "user.admin",
    icon: 'mdi-account-group',
    parent: 'page.accueil',
    access: 4,
    component: manageUser,
    hidden: ({$store}) => !$store.getters.droitMax >= 4
  },
  {
    path: "/user/change_password",
    label: "Changement de mot de passe",
    name: "user.change_password",
    parent: 'page.accueil',
    component: changePassword
  }
];

const STORE = {
  state: {
    _user: null,
    _redirectOnLogin: null,
    _organismes: [], // juste utilisé dans le profil utilisateur
    _users: [],
    _redirect: null,
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
    organismes(state, organismes) { // peue être inutile car ne peut être modifié via l'appli
      state._organismes = organismes;
    },
    users(state, users) {
      state._users = users;
    },
    redirect(state, redirect) {
      state.redirect = redirect;
    }
  },

  getters: {

    prod: () => !window.webpackHotUpdate, // verifie si l'application est en mode production. Retourne true si c'est le cas

    mediaImgPath: () => `${config.URL_APPLICATION}/static/medias/img/`, // Génère le chemin d'accès aux images
    mediaDocPath: () => `${config.URL_APPLICATION}/static/medias/doc/`, // Génère le chemin d'accès aux documents

    users: state => state.users, // retourne la liste des utilisateurs stockée dans le state ()

    organismes: state => { // retourne les organismes. Utile dans le profil utilisateur
      return state._organismes;
    },

    redirectOnLogin(state) {
      return state._redirectOnLogin;
    },

    redirect(state) {
      return state.redirect;
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
      // const date = new Date(state._user.expires);
      // const now = new Date();
      return !!(state._user && state._user.id_role);
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
      return (STORE.getters.isAuth(state) && state._user.max_level_profil) || 0;
    }
  },
  actions: {

    // vérifie si l'utilisateur est connecté dans le backend
    // Est exécuté dans le app.vue
    testConnexion({state, commit}) { 
      state, commit;
      return new Promise((resolve, reject) => {
        apiRequest('GET', "api/user/test").then( 
          res => {
            resolve(res)
          },
          error => {
            reject(error)
          }
        );
      });
    },

    // verifie si les organismes sont déjà stockés dans le state
    // Apparemment les organismes sont vides tout le temps
    // Si non il les récupère dans le backend
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


    // récupère les informations de l'utilisateur. Utilisé dans le profil utilisateur
    userInfo({ commit }, id_role) {
      return new Promise((resolve, reject) => {
        // commit; pas utilisé
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

    // retourne la liste des utilisateurs. Fait seulement une requète GET dans le backend et stocke le résultat
    // dans le state._users
    // Utilisé dans manage-user. la page de gestion administration des utilisateurs 
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
