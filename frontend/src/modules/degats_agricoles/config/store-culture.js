export default {
  group: 'agricole',
  name: 'culture',
  label: 'Culture',
  labels: 'Cultures',
  genre: 'F',
  idFieldName: 'id_culture',
  displayFieldName: 'nom_culture',
  serverSide: true, // si pagination et tri sont gérés côté serveur

  options: {
    page: 1, // on affiche la première page par défaut
    sortBy: ['nom_culture'], // tri par défaut
    sortDesc: [false],
  },

  defs: {
    id_culture: {
      label: 'ID',
      type: 'text',
      hidden: true,
    },
    nom_culture: {
      label: 'Nom',
      type: 'text',
      required: true,
    },
    type_culture: {
      label: 'Type de culture',
      storeName: 'agricoleTypeCulture',
      type: 'list_form',
      list_type: 'select',
      returnObject: true, // true si ca ne retourne pas qu'une valeur mais plusieurs dans un objet
    },
  },
};
