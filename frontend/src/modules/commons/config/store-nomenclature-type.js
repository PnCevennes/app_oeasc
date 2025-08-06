export default {
    group: "commons",
    name: "nomenclatureType",
    label: "Nomenclature type",
    idFieldName: 'id_type',
    displayFieldName: 'mnemonique',
    serverSide: true,
    options: { // Ajoute des param à la requête get pour filtrer les données
      page: 1, // on affiche la première page par défaut 
      sortBy: ['id_type'], 
      sortDesc: [true], // tri en ordre décroissant
    },
    defs: {
      id_type: {
        label: "Id",
        hidden: true,
        type: 'text',
      },
      mnemonique: {
        label: "Mnémonique",
        required: true,
        type: 'text',
      },
      label_fr: {
        label: "Label fr",
        required: true,
        type: 'text',
      },
      definition_default: {
        label: "Description",
        // required: true,
        type: 'text',
      },
    },
    
  };
  