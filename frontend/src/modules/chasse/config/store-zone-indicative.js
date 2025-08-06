export default {
    group: "chasse",
    name: "zoneIndicative",
    label: "Zone indicatives",
    labels: "Zones indicatives",
    serverSide: true,
    

    options: { // Ajoute des param à la requête get pour filtrer les données

      page: 1, // on affiche la première page par défaut 
      sortBy: ["id_zone_indicative"], 
      sortDesc: [true], // tri en ordre décroissant
      // fields: [ //les des champs des modèles à intégrer à la requête get
      //   "zone_cynegetique.id_zone_cynegetique", "zone_cynegetique.code_zone_cynegetique",
      //   "zone_cynegetique.nom_zone_cynegetique"
      // ]
    },


    defs: {
      id_zone_indicative: {
        label: "ID",
        type: 'text',
        hidden: true
      },
      code_zone_indicative: {
        label: "Code",
        type: 'text',
        required: true
      },
      nom_zone_indicative: {
        label: "Nom",
        type: 'text',
        required: true
      },
      zone_cynegetique: {
          label: "Zone cinégétique",
          type: 'list_form',
          list_type: "select",
          returnObject: true,
          displayFieldName: 'code_zone_cynegetique',
          storeName: 'chasseZoneCynegetique',
          required: true,
      },
    }
  };
