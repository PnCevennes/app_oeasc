import configTagForm from "./form-tag";

export default {
  storeName: "commonsTag",
  dense: true,
  striped: true,
  small: true,
  configForm: configTagForm,
  headerDefs: {
    id_tag: {
      text: "Id"
    },
    nom_tag: {
      text: "Nom"
    },
    code_tag: {
      text: "Code"
    },
  },
  sortBy: ["nom_tag"],
  sortDesc: [true],
  label: 'nom_tag',
};
