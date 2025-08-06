export default {
  group: "commons",
  name: "espece",
  label: "Espèce",
  options: { // Ajoute des param à la requête get pour filtrer les données
      page: 1, // on affiche la première page par défaut 
      sortBy: ['nom_espece'], 
      sortDesc: [false], // tri en ordre décroissant
    },
  defs: {
    id_espece: {
      label: "Id",
      type: "number",
      hidden: true
    },
    nom_espece: {
      label: "Nom",
      type: "text",
      required: true,
    },
    code_espece: {
      label: "Code",
      type: "text",
      required: true
    }
  },


};
