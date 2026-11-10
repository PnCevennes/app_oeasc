export default {
  idFieldName: 'id_content',

  options: {
    // paramètres ajoutés à la requête get
    // les champs des modèles liés
    fields: ['tags.id_tag', 'tags.nom_tag', 'tags.code_tag'],
  },

  formDefs: {
    id_content: {
      label: 'Id',
      type: 'text',
      hidden: true,
    },
    code: {
      label: 'Code',
      type: 'text',
      required: true,
    },
    tags: {
      label: 'Tags',
      type: 'list_form',
      list_type: 'select',
      multiple: true,
      storeName: 'commonsTag',
      // le backend (TContentsSchema.tags = Nested many) attend des objets {id_tag, …}, pas des ids
      returnObject: true,
    },
    md: {
      label: 'Texte',
      type: 'wysiwyg',
      required: true,
    },
  },

  title: ({ id }) => (id ? `Modificiation du contenu ${id}` : "Création d'un contenu"),
  storeName: 'commonsContent',
};
