import configEspeceForm from "./form-espece";

export default {
  storeName: "inEspece",
  dense: true,
  striped: true,
  small: true,
  configForm: configEspeceForm,
  headerDefs: {
    id_espece: {
      text: "Id"
    },
    nom_espece: {
      text: "Nom"
    },
    code_espece: {
      text: "Code"
    },
  },
  sortBy: ["nom_espece"],
  sortDesc: [true],
  label: 'nom_espece',
};
