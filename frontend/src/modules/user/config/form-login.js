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
