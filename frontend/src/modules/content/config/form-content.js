export default {
  idFieldName: 'id_content',  

  options: { // paramètres ajoutés à la requête get
    // page: 1,
    // sortBy: ["meta_create_date"],
    // sortDesc: [true],
    // les champs des modèles liés
    fields: [
      "tags.id_tag", "tags.nom_tag", "tags.code_tag"
      ]
  },


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
