import { copy } from "@/core/js/util/util";
import formDefsUser from "./form-defs-user";

const formDefsUserCopy = copy(formDefsUser);
formDefsUserCopy.email.disabled = true;
formDefsUserCopy.id_organisme.disabled = true;

export default {
  formDefs: formDefsUserCopy,
  forms: [
    "nom_role",
    "prenom_role",
    "email",
    "id_organisme",
    "desc_role",
    "accept_email"
  ],
  preLoadData: ({ $store, config }) => {
    return new Promise(resolve => {
      Promise.all([
        $store.dispatch("userInfo", $store.getters.user.id_role),
        $store.dispatch("organismes")
      ]).then(data => {
        const value = data[0];
        config.value = value;
        resolve();
      });
    });
  },
  switchDisplay: true,
  displayValue: true,
  displayLabel: true,
  title: "Informations",
  action: {
    request: {
      url: "pypn/register/post_usershub/update_user",
      method: "POST",
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
        if ([true, false].includes(baseModel.accept_email)) {
          baseModel.champs_addi.accept_email = baseModel.accept_email;
        }

        return baseModel;
      }
    }
  }
};
