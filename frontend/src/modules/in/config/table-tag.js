import configTagForm from "./form-tag";

export default {
  storeName: "inTag",
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
  },
  sortBy: ["nom_tag"],
  sortDesc: [true],
  label: 'nom_tag',
};
