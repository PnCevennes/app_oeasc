export default {
  group: 'in',
  name: 'observer',
  label: 'Observateur',
  serverSide: true,
  options: {
    // Ajoute des param à la requête get pour filtrer les données
    page: 1, // on affiche la première page par défaut
    sortBy: ['id_observer'], // tri par défaut
    sortDesc: [true], // tri en ordre décroissant
  },
  defs: {
    id_observer: {
      label: 'ID',
      type: 'text',
      hidden: true,
    },
    nom_observer: {
      label: 'Nom',
      type: 'text',
      required: true,
    },
  },
};
