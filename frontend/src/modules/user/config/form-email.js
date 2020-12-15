import formDefs from "./form-defs-user";

export default {
  formDefs,
  action: {
    label: "Modifier votre mot de passe",
    request: {
      url: "pypn/register/post_usershub/create_cor_role_token",
      method: "POST",
    },
  },
  forms: ["email"]
};
