export default {
  formDefs: {
    src: {
      label: "Choisir une image",
      type: "list_form",
      list_type: "autocomplete",
      url: "api/commons/files/img",
      search: true,
    },
    file: {
      label: "Ajouter une image",
      type: "file",
    },
    title: {
      label: "Texte",
      type: "text",
    },
    source: {
      label: "Auteur",
      type: "text",

    },
    position: {
      type: 'list_form',
      label: 'Position',
      items: ['left', 'center', 'right'],
      list_type: 'button'
    },
    width: {
      type: 'text',
      label: 'Largeur'
    },
    height: {
      type:'text',
      label: 'Hauteur'
    }
  },

  title: "Insérer une image dans le texte",
  action: {
    request: {
      url: "api/commons/add_file/img",
      method: 'POST'
    }
  },
  value: {
    position: "center"
  }
};
