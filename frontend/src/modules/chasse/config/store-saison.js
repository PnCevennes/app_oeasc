export default {
  group: "chasse",
  name: "saison",
  label: "Saison",
  serverSide: true,
  options: {
    sortBy: ['nom_saison'],
    sortDesc: [true]
  },
  defs: {
    id_saison: {
      label: "ID",
      type: "text",
      hidden: true
    },
    nom_saison: {
      label: "Nom",
      type: "text",
      required: true
    },
    date_debut: {
      label: "Date début",
      type: "date",
      required: true
    },
    date_fin: {
      label: "Date fin",
      type: "date",
      required: true
    },
    current: {
        label: 'En cours',
        type: "bool_switch",
    },
    commentaire: {
        label: 'Commentaires',
        type: "text_area",
    }
  }
};
