export default {
  idFieldName: 'id_content',

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
    // 'actualite' ou 'page' : posé automatiquement à la création (non saisissable)
    type_page: {
      label: 'Type',
      type: 'text',
      hidden: true,
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
