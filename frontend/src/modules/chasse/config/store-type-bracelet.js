export default {
  group: "chasse",
  name: "typeBracelet",
  label: "Type de bracelet",
  labels: "Types de bracelet",
  displayFieldName: "code_type_bracelet",
  serverSide: true, // si pagination et tri sont gérés côté serveur


  options: { // Ajoute des param à la requête get pour filtrer les données
    page: 1, // on affiche la première page par défaut 
    sortBy: ["espece", "code_type_bracelet"], // tri par défaut
    sortDesc: [false, false], // tri en ordre décroissant

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
        returnObject: true, // true si ca ne retourne pas qu'une valeur mais plusieurs dans un objet
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
