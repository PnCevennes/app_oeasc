import { displayParcelles } from "../declaration.js";

export default {
    idFieldName: "id_declaration",
    dense: true,
    striped: true,
    small: true,
    headerDefs: {
      actions: {
        noSearch: true,
        width: "90px",
        text: "Actions",
        list: [
          {
            title: "Voir la déclaration",
            icon: "mdi-eye",
            to: ({ item }) =>
              `/declaration/voir_declaration/${item.id_declaration}`,
          },
          {
            title: "Éditer la déclaration",
            icon: "mdi-pencil",
            to: ({ item }) =>
              `/declaration/declarer_en_ligne/${item.id_declaration}?keySession=all`,
            condition: ({ item, $store }) => {
              return (
                $store.getters.droitMax > item.id_droit_max ||
                $store.getters.user.id_role == item.id_declarant
              );
            },
          },
        ],
        sortable: false,
      },
      id_declaration: {
        text: "Id",
      },
      declarant: {
        text: "Déclarant",
      },
      org_mnemo: {
        text: "Organisme",
      },
      // organisme: {
      //   text: "Organisme"
      // },
      secteur: {
        text: "Secteur",
      },
      declaration_date: {
        text: "Date",
        type: "date",
      },
      label_foret: {
        text: "Nom forêt",
      },
      peuplement_ess_1_mnemo: {
        text: "Ess. objectif",
      },
      parcelles: {
        text: "Parcelle(s)",
        display: (val) => displayParcelles(val),
      },
      peuplement_type_mnemo: {
        text: "Type peupl.",
      },
      peuplement_origine2_mnemo: {
        text: "Origine plants touchés",
      },
      degat_type_mnemos: {
        text: "Type dégâts",
      },
      b_valid: {
        display: (val) =>
          val === true ? "Oui" : val === false ? "Non" : "?",
        width: "100px",
        text: "Validé",
        condition: ({ $store }) => $store.getters.droitMax >= 5,
        edit: {
          preloadData: ({ config, $store, id }) => {
             return new Promise((resolve) => {
              
              $store
                .dispatch("declarationForm", id)
                .then((declaration) => {
                  
                  config.value = declaration;
                  resolve(declaration);
                });
            });
          },
          action: {
            request: {
              url: "api/degat_foret/declaration",
              method: "POST",
            },
          },
          formDefs: {
            b_valid: {
              label: "Valider cette déclaration (admin seulement)",
              type: "bool_radio",
              labels: ["Oui", "Non"],
            },
          },
        },
      },
    },
  };
