
export default {
  group: "chasse",
  name: "saisonDate",
  label: "Saisons (date/espèce)",
  serverSide: true, // si pagination et tri sont gérés côté serveur

  options: { // Ajoute des param à la requête get pour filtrer les données
    page: 1, // on affiche la première page par défaut 
    sortBy: ["saison", "espece", "nomenclature_type_chasse"], // tri par défaut
    sortDesc: [true, false, false], // tri en ordre décroissant
  },

  defs: {
    id_saison_date: {
      label: "ID",
      hidden: true,
    },
    saison: {
        label: 'saison',
        storeName: 'chasseSaison',
        type: 'list_form',
        list_type: 'autocomplete',
        returnObject: true, // true si ca ne retourne pas qu'une valeur mais plusieurs dans un objet
        dataReloadOnSearch: true,
    },
    espece: {
        label: 'Espèce',
        storeName: 'commonsEspece',
        type: 'list_form',
        list_type: 'select',
        returnObject: true,
    },
    nomenclature_type_chasse: {
        label: 'Type de chasse',
        storeName: 'commonsNomenclature',
        type: 'nomenclature',
        nomenclatureType: "OEASC_MOD_CHASSE",
        list_type: 'select',
        returnObject: true,
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
  }
};
