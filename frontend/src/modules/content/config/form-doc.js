export default {
  formDefs: {
    src: {
      label: "Choisir un document",
      type: "list_form",
      display: "autocomplete",
      url: "api/commons/files/doc",
      search: true,
    },
    file: {
      label: "Ajouter un document",
      type: "file",
    },
    txt: {
      label: 'Texte dans le lien',
      type: "text"
    }
  },

  title: "Insérer un document dans le texte",
  action: {
    request: {
      url: "api/commons/add_file/doc",
      method: 'POST'
    }
  },
};
