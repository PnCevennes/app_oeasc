
export default {
  group: "chasse",
  name: "saisonDate",
  label: "Saisons (date/espèce)",
  serverSide: true,

  options: { // Ajoute des param à la requête get pour filtrer les données
    page: 1, // on affiche la première page par défaut 
    sortBy: ["saison", "espece", "nomenclature_type_chasse"], // tri par défaut
    sortDesc: [true, false, false], // tri en ordre décroissant
    // fields: [ //les des champs des modèles à intégrer à la requête get
    //   "saison.id_saison", "saison.nom_saison",
    //    "espece.id_espece", "espece.nom_espece", "espece.code_espece",
    //    "nomenclature_type_chasse.id_nomenclature", "nomenclature_type_chasse.label_fr", "nomenclature_type_chasse.id_type", 
    //    "nomenclature_type_chasse.definition_fr"
    // ]
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
        returnObject: true,
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
