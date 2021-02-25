export default {
  formDefs: {
    id_content: {
      label: "Id",
      type: "text",
      hidden: true
    },
    code: {
      label: "Code",
      type: "text",
      required: true
    },
    tags: {
      label: "Tags",
      type: "list_form",
      list_type: "select",
      multiple: true,
      storeName: "commonsTag"
    },

    md: {
      label: "Texte",
      type: "text_area",
      required: true,
      rows: 15
    }
  },

  title: ({ id }) =>
    id ? `Modificiation du contenu ${id}` : "Création d'un contenu",
  storeName: "commonsContent"
};
