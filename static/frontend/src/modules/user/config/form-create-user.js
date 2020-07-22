import formDefsUser from './form-defs-user'

export default {
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
  formDefs: formDefsUser,
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
