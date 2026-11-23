export default {
  title: 'Connexion',
  action: {
    label: 'Se connecter',
    preProcess: ({ baseModel, globalConfig }) => ({
      ...baseModel,
      id_application: globalConfig.ID_APPLICATION,
    }),
    onSuccess: ({ data, $store, $router, $route }) => {
      const user = { ...data.user, expires: data.expires };
      // redirection interne uniquement : chemin absolu SPA, pas d'URL externe ni de '//'
      const queryRedirect = $route.query.redirect;
      const redirect =
        typeof queryRedirect === 'string' && /^\/(?![/\\])/.test(queryRedirect)
          ? queryRedirect
          : '/';
      $store.commit('user', user);
      setTimeout(() => {
        $router.push(redirect);
      }, 1000);
    },
    // Messages explicites pour la connexion (le 401 générique signifie "session expirée",
    // ce qui est trompeur ici : il s'agit d'identifiants incorrects)
    describeError: (error) => {
      const status = error && error.status;
      if (status === 401) {
        return 'Identifiant ou mot de passe incorrect. Vérifiez votre saisie puis réessayez.';
      }
      if (status === 400) {
        return "Veuillez renseigner votre identifiant et votre mot de passe.";
      }
      if (status === 403) {
        return "Votre compte n'est pas autorisé à se connecter à cette application. Contactez l'administrateur.";
      }
      return null;
    },
    request: {
      url: 'auth/login',
      method: 'POST',
    },
  },
  formDefs: {
    login: {
      type: 'text',
      required: true,
      label: 'Identifiant',
      help: true,
    },
    password: {
      type: 'password',
      required: true,
      label: 'Mot de passe',
    },
  },
};
