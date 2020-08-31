export default {
  title: "Connexion",
  action: {
    label: "Se connecter",
    preProcess: ({ baseModel, globalConfig }) => ({
      ...baseModel,
      id_application: globalConfig.ID_APPLICATION
    }),
    onSuccess: ({ data, $session, $store, $router, redirect }) => {
      const user = { ...data.user, expires: data.expires };
      $session.set("user", user);
      $store.commit("user", user);
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
