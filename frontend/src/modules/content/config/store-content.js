export default {
  group: "commons",
  name: "content",
  label: "Content",
  serverSide: true,

  options: { // paramètres ajoutés à la requête get
    // page: 1,
    // sortBy: ["meta_create_date"],
    // sortDesc: [true],
    // les champs des modèles liés
    fields: [
      "tags.id_tag", "tags.nom_tag", "tags.code_tag"
      ]
  },



  defs: {
    id_content: {
      label: "ID",
      type: "text",
      hidden: true
    },
    code: {
      label: "Code",
      type: "text",
      required: true
    },
    md: {
      label: "Markdown",
      type: "text_area",
      required: true
    },
    meta_create_date: {
        type:'date',
        label: 'Création'
    },
    tags: {
        type:'text',
        label: 'tags'
    },



  }
};
