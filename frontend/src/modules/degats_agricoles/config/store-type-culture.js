export default {
  group: 'agricole',
  name: 'typeCulture',
  label: 'Type de culture',
  labels: 'Types de culture',
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
  },
};
