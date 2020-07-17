import formDefs from "./form-defs-user";

export default {
  formDefs,
  request: {
    url: "pypn/register/post_usershub/create_cor_role_token",
    method: "POST",
    label: "Modifier votre mot de passe"
  },
  forms: ["email"]
};
