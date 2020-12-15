export default {
  formDefs: {
    id_espece: {
      label: 'Id',
      type: "text",
      hidden: true
    },
    nom_espece: {
      label: "Nom",
      type: "text",
      required: true,
    },
    code_espece: {
      label: 'Code',
      type: "text",
      required: true
    },
  },

  title: ({ id }) =>
    id ? `Modificiation de l'espece ${id}` : "Création d'une espece",
  switchDisplay: ({ id }) => !!id,
  displayValue: ({ id }) => !!id,
  displayLabel: true,
  storeName: "inEspece",
};
