const configLogin = {
  //   display: "table",
  title: "Connexion",
  request: {
    url: "pypn/auth/login",
    label: "Créer un compte"
  },

  forms: {
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

export { configLogin };
