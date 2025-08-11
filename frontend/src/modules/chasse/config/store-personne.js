export default {
    group: "chasse",
    name: "personne",
    label: "Personne",
    serverSide: true,

    options: { // Ajoute des param à la requête get pour filtrer les données
      page: 1, // on affiche la première page par défaut 
      sortBy: ["id_personne"], 
      sortDesc: [true], // tri en ordre décroissant
    },

    defs: {
      id_personne: {
        label: "ID",
        type:'text',
        hidden: true
      },
      nom_personne: {
        label: "Nom",
        type:'text',
        required: true
      }
    }
  };
  