export default {
  formDefs: {
    id_tag: {
      label: 'Id',
      type: "text",
      hidden: true
    },
    nom_tag: {
      label: "Nom",
      type: "text",
      required: true,
    },
    code_tag: {
      label: 'Code',
      type: "text",
      required: true
    },
  },

  title: ({ id }) =>
    id ? `Modificiation du tag ${id}` : "Création d'un tag",
  storeName: "commonsTag",
};
