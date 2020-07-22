import formDefs from "./form-defs-user";

export default {
  formDefs,
  request: {
    url: "pypn/register/post_usershub/change_password",
    method: "POST",
    label: "Modifier votre mot de passe",
    preProcess: ({ baseModel, config }) => ({
      ...baseModel,
      token: config.token
    })
  },
  forms: ["password", "password_confirmation"]
};
