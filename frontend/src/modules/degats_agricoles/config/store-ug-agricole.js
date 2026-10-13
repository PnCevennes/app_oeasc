export default {
  group: 'agricole',
  name: 'ugAgricole',
  label: 'Unité de gestion agricole',
  labels: 'Unités de gestion agricoles',
  genre: 'F',
  idFieldName: 'id_ug_agricole',
  displayFieldName: 'nom_ug_agricole',
  serverSide: true, // si pagination et tri sont gérés côté serveur

  options: {
    page: 1, // on affiche la première page par défaut
    sortBy: ['nom_ug_agricole'], // tri par défaut
    sortDesc: [false],
  },

  defs: {
    id_ug_agricole: {
      label: 'ID',
      type: 'text',
      hidden: true,
    },
    nom_ug_agricole: {
      label: 'Nom',
      type: 'text',
      required: true,
    },
    in_oeasc: {
      label: "Dans l'OEASC",
      type: 'bool_switch',
    },
  },
};
