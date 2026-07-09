// Remplace vue-session (abandonné, jamais porté sur Vue 3).
// Seul $session.set(key, value) est utilisé dans l'app ; persist:true dans l'ancienne config
// signifiait que les données survivent à un rafraîchissement de page mais pas à la fermeture
// de l'onglet, ce que sessionStorage reproduit nativement.
export default {
  install(app) {
    app.config.globalProperties.$session = {
      set(key, value) {
        sessionStorage.setItem(key, JSON.stringify(value));
      },
    };
  },
};
