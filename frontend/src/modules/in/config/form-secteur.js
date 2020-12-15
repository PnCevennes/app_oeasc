export default {
  formDefs: {
    id_secteur: {
      label: 'Id',
      type: "text",
      hidden: "true"
    },
    nom_secteur: {
      label: "Nom",
      type: "text",
      required: true,
    },
    code_secteur: {
      label: 'Code',
      type: "text",
      required: "True"
    },
  },

  title: ({ id }) =>
    id ? `Modificiation du secteur ${id}` : "Création d'un secteur",
  switchDisplay: ({ id }) => !!id,
  displayValue: ({ id }) => !!id,
  displayLabel: true,
  storeName: "inSecteur",
};
