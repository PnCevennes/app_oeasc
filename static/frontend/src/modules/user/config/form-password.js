import formDefs from "./form-defs-user";

export default {
  formDefs,
  action: {
    label: "Modifier votre mot de passe",
    preProcess: ({ baseModel, config }) => ({
      ...baseModel,
      token: config.token
    }),
    request: {
      url: "pypn/register/post_usershub/change_password",
      method: "POST",
    }
  },
  forms: ["password", "password_confirmation"]
};
