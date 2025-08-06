export default {
  group: "chasse",
  name: "saison",
  label: "Saison",
  genre : "M",
  serverSide: true,


  options: {
    page: 1, // on affiche la première page par défaut 
    sortBy: ['nom_saison'], // tri par défaut
    sortDesc: [true],
    // fields: [ //les des champs des modèles à intégrer à la requête get
    //   "id_saison",
    //   "nom_saison",
    //   "date_debut",
    //   "date_fin",
    //   "current",
    //   "commentaire"     
    // ] // ici il n'est pas nécéssaire de lister les champs mais pour plus de lisibilité on les met
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
