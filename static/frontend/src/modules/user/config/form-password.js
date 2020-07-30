import formDefs from "./form-defs-user";

export default {
  formDefs,
  action: {
    label: "Modifier votre mot de passe",
    request: {
      url: "pypn/register/post_usershub/change_password",
      method: "POST",
      preProcess: ({ baseModel, config }) => ({
        ...baseModel,
        token: config.token
      })
    }
  },
  forms: ["password", "password_confirmation"]
};
