export default {
  group: "chasse",
  name: "typeBracelet",
  label: "Type de bracelet",
  labels: "Types de bracelet",
  displayFieldName: "code_type_bracelet",
  serverSide: true,


  options: { // Ajoute des param à la requête get pour filtrer les données
    page: 1, // on affiche la première page par défaut 
    sortBy: ["espece", "code_type_bracelet"], // tri par défaut
    sortDesc: [false, false], // tri en ordre décroissant
    // fields: [ //les des champs des modèles à intégrer à la requête get
    //   "espece.id_espece", "espece.nom_espece", "espece.code_espece"
    // ]
  },


  defs: {
    id_type_bracelet: {
      label: "ID",
      type: "text",
      hidden: true,
    },

    espece: {
        label: 'Espèce',
        storeName: 'commonsEspece',
        type: 'list_form',
        list_type: 'select',
        returnObject: true,
    },


    code_type_bracelet: {
        label: 'Code',
        type: "text",
    },


    description_type_bracelet: {
        label: 'Description',
        type: "text",
    }
  }
};
