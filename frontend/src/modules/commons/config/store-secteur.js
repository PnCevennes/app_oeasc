export default {
  group: 'commons',
  name: 'secteur',
  label: 'Secteur',
  serverSide: true,

  options: {
    // Ajoute des param à la requête get pour filtrer les données
    page: 1, // on affiche la première page par défaut
    sortBy: ['nom_secteur'],
    sortDesc: [false], // tri en ordre décroissant
  },

  defs: {
    id_secteur: {
      label: 'ID',
      type: 'number',
      hidden: true,
    },
    nom_secteur: {
      label: 'Nom',
      type: 'text',
      required: true,
    },
    code_secteur: {
      label: 'Code',
      type: 'text',
      required: true,
    },
  },
};
