export default {
  title: "Connexion",
  action: {
    label: "Se connecter",
    preProcess: ({ baseModel, globalConfig }) => ({
      ...baseModel,
      id_application: globalConfig.ID_APPLICATION
    }),
    onSuccess: ({ data, $session, $store, $router, $route }) => {
      const user = { ...data.user, expires: data.expires };
      const redirect = $route.query.redirect;
      $session.set("user", user);
      $store.commit("user", user);
      console.log(redirect)
      setTimeout(() => {
        $router.push(redirect || "/");
      }, 1000);
    },
    request: {
      url: "pypn/auth/login",
      method: "POST",
    }
  },
  formDefs: {
    login: {
      type: "text",
      required: true,
      label: "Identifiant",
      help: true
    },
    password: {
      type: "password",
      required: true,
      label: "Mot de passe"
    }
  }
};
