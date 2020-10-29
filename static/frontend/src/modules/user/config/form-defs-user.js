export default {
  nom_role: {
    type: "text",
    required: true,
    label: "Nom"
  },
  prenom_role: {
    type: "text",
    required: true,
    label: "Prenom"
  },
  email: {
    required: true,
    type: "email",
    label: "E-mail"
  },
  id_organisme: {
    type: "list_form",
    required: true,
    label: "Organisme",
    display: "select",
    url: "api/user/organismes",
    displayFieldName: "nom_organisme",
    valueFieldName: "id_organisme"
  },
  autre_organisme: {
    type: "text",
    required: true,
    label: "Préciser organisme",
    condition: ({ baseModel, $store }) => {
      const organisme = $store.getters.organismes.find(
        o => o.id_organisme == baseModel.id_organisme
      );
      return !!(organisme && organisme.nom_organisme == "Autre (préciser)");
    }
  },
  desc_role: {
    type: "list_form",
    required: true,
    label: "Rôle",
    display: "select",
    items: [
      "Propriétaire forestier privé",
      "Salarié, agent, fonctionnaire",
      "Expert forestier indépendant"
    ]
  },
  accept_email: {
    type: "bool_switch",
    label:
      "Rester informé des principales évolutions du dispositif (envoi ponctuel d’e-mails)",
    required: true
  },
  password: {
    type: "password",
    label: "Mot de passe",
    required: true,
    counter: true
  },
  password_confirmation: {
    type: "password",
    label: "Mot de passe (confirmation)",
    required: true,
    counter: true,
    rules: ({ baseModel }) => [
      v => v == baseModel.password || "Les mots de passe doivent être identique"
    ]
  }
};
