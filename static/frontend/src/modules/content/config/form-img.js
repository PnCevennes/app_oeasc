export default {
  formDefs: {
    src: {
      label: "Choisir une image",
      type: "list_form",
      display: "autocomplete",
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
    center: {
      type: 'bool_switch',
      label: 'Centré',
      value: true
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
    "center": true
  }
};
