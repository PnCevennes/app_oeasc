export default {
  watchBaseModel({ config, baseModel }) {
    if (!(config && baseModel)) {
      return;
    }
    config.forms.password_confirmation.rules = [
      v => {
        return (
          v === baseModel.password ||
          "Les mot de passe doivent être identiques"
        );
      }
    ];
  },
  preLoadData: ({ $store }) => {
    return new Promise(resolve => {
      // peut être pas utile....
      $store.dispatch("organismes").then(() => {
        resolve();
      });
    });
  },
  request: {
    method: "POST",
    url: "pypn/register/post_usershub/create_temp_user",
    label: "S'inscrire",
    preProcess: ({ baseModel, globalConfig }) => {
      baseModel.groupe = false;
      baseModel.id_application = globalConfig.ID_APPLICATION;
      baseModel.pn = true;
      baseModel.identifiant = baseModel.email;
      baseModel.remarques = "Créé depuis le site de l'OEASC";
      baseModel.champs_addi = {};
      if (baseModel.autre_organisme) {
        baseModel.champs_addi.organisme = baseModel.autre_organisme;
      }
      if (baseModel.accept_email) {
        baseModel.champs_addi.accept_email = baseModel.accept_email;
      }
      return baseModel;
    }
  },
  formDefs: {
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
      textFieldName: "nom_organisme",
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
        return !!(organisme && organisme.nom_organisme == "Autre (préciser)") || 1;
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
      counter: true
    }
  },
  groups: [
    {
      forms: ["nom_role", "prenom_role"],
      direction: "row"
    },
    {
      forms: ["email"]
    },
    {
      forms: ["id_organisme", "autre_organisme"],
      direction: "row"
    },
    {
      forms: ["desc_role", "accept_email"]
    },
    {
      forms: ["password", "password_confirmation"],
      direction: "row"
    }
  ]
};
