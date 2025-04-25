export default {
    group: "commons",
    name: "nomenclature",
    label: "Nomenclature",
    serverSide: true,

    options: { // Ajoute des param à la requête get pour filtrer les données
      // page: 1, // on affiche la première page par défaut 
      // sortBy: ["idl_nomenclature"], // tri par défaut
      // sortDesc: [false], // tri en ordre décroissant
      fields: [ //les des champs des modèles à intégrer à la requête get
        "nomenclature_type.id_type", "nomenclature_type.mnemonique"
      ]
    },
  

    defs: {
      id_nomenclature: {
        label: "Id",
        hidden: true,
        type: 'text',
      },
      nomenclature_type: {
        storeName: 'commonsNomenclatureType',
        displayFieldName: 'mnemonique',
        type: 'list_form',
        list_type: 'autocomplete',
        // returnObject: true,
        label: "Type",
        // type: 'text',
        // required: true,
      },
      cd_nomenclature: {
        label: "Code",
        type: 'text',
        required: true
      },
      label_fr: {
        label: "Label fr",
        type: 'text',
        required: true
      },
      mnemonique: {
        label: "Mnemonique",
        type: 'text',
        required: true
      },
      definition_fr: {
        label: "Definition",
        type: 'text',
        required: false
      },
    },
    displayFieldName: 'label_fr',
    sortBy: ['type', 'cd_nomenclature']
  };
  