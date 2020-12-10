import { config as globalConfig } from "@/config/config";

export default {
    idFieldName: "id_role",
    labelFieldName: "nom_complet",
    title: "Liste des utilisateurs",
    sortBy: ["create_date"],
    sortDesc: [true],
    dense: true,
    striped: true,
    headerDefs: {
      org_mnemo: {
        text: "Organisme",
      },
      nom_complet: {
        text: "Nom, prénom",
      },
      email: {
        text: "E-mail",
      },
      desc_role: {
        text: "Rôle",
        display: (val) => {
          return val.split(" ")[0].split(",")[0];
        },
      },
      id_droit_max: {
        text: "Droits",
        edit: {
          condition: ({ $store, baseModel }) => {
            return $store.getters.droitMax > baseModel.id_droit_max;
          },
          action: {
            preProcess: ({ baseModel }) => {
              return {
                id_role: baseModel.id_role,
                id_droit: baseModel.id_droit_max,
                id_application: globalConfig.ID_APPLICATION,
              };
            },
            request: {
              url: "pypn/register/post_usershub/change_application_right",
              method: "POST",
            },
            onSuccess: ( { data }) => { data.id_droit_max = data.id_droit;}
          },
          formDefs: {
            id_droit_max: {
              type: "list_form",
              display: "select",
              items: ({ $store }) =>
                [1, 2, 3, 4, 5, 6].filter(
                  (droit) => $store.getters.droitMax > droit
                ),
              required: true,
            },
          },
        },
      },
      nb_declarations: {
        text: "Nb déclarations",
      },
      create_date: {
        text: "Date inscription",
        type: "date",
      },
      accept_email: {
        text: "Accepte Email",
      },

    },

}
