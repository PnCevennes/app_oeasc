export default {
    group: "commons",
    name: "nomenclature",
    label: "Nomenclature",
    displayFieldName: 'label_fr',
    serverSide: true,
    options: { // Ajoute des param à la requête get pour filtrer les données
      page: 1, // on affiche la première page par défaut 
      sortBy: ['id_nomenclature'], 
      sortDesc: [true], // tri en ordre décroissant
    },
    defs: {
      id_nomenclature: {
        label: "Id",
        hidden: true,
        type: 'text',
      },
     type: {
        label: "Type",
        type: 'text',
        required: true,
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
        label: "Description",
        type: 'text',
        required: true
      },
    },
    // sortBy: ['meta_create_date', 'id_nomenclature']
    
  };
  