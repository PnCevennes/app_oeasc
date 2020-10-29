import configSecteurForm from "./form-secteur";

export default {
  storeName: "inSecteur",
  dense: true,
  striped: true,
  small: true,
  configForm: configSecteurForm,
  headerDefs: {
    id_secteur: {
      text: "Id"
    },
    nom_secteur: {
      text: "Nom"
    },
    code_secteur: {
      text: "Numéro"
    },
  },
  sortBy: ["nom_secteur"],
  sortDesc: [true],
  label: 'circuit',
};
