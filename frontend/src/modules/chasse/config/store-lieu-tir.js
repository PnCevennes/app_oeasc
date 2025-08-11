export default {
    group: "chasse",
    name: "lieuTir",
    label: "Lieu de tir",
    serverSide: true,

    options: { // Ajoute des param à la requête get pour filtrer les données
      page: 1, // on affiche la première page par défaut 
      sortBy: ["id_lieu_tir"], 
      sortDesc: [true], // tri en ordre décroissant
    },



    defs: {
      id_lieu_tir: {
        label: "ID",
        type: 'text',
        hidden: true
      },
      code_lieu_tir: {
        label: "Code",
        type: 'text',
        required: true
      },
      nom_lieu_tir: {
        label: "Nom",
        type: 'text',
        required: true
      },
      zone_indicative: {
        label: "Zone indicative",
        type: 'list_form',
        list_type: "autocomplete",
        dataReloadOnSearch: true,
        returnObject: true,  
        storeName: 'chasseZoneIndicative',
      }
    }
  };
  