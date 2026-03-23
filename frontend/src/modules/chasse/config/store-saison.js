export default {
  group: 'chasse',
  name: 'saison',
  label: 'Saison',
  genre: 'M',
  serverSide: true, // si pagination et tri sont gérés côté serveur

  options: {
    page: 1, // on affiche la première page par défaut
    sortBy: ['nom_saison'], // tri par défaut
    sortDesc: [true],
  },

  defs: {
    id_saison: {
      label: 'ID',
      type: 'text',
      hidden: true,
    },
    nom_saison: {
      label: 'Nom',
      type: 'text',
      required: true,
    },
    date_debut: {
      label: 'Date début',
      type: 'date',
      required: true,
    },
    date_fin: {
      label: 'Date fin',
      type: 'date',
      required: true,
    },
    current: {
      label: 'En cours',
      type: 'bool_switch',
    },
    commentaire: {
      label: 'Commentaires',
      type: 'text_area',
    },
  },
};
