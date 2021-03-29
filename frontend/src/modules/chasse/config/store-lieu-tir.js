export default {
    group: "chasse",
    name: "lieuTir",
    label: "Lieu de tir",
    serverSide: true,
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
      zone_interet: {
        label: "Zone d'intérêt",
        type: 'list_form',
        list_type: "autocomplete",
        dataReloadOnSearch: true,
        returnObject: true,  
        storeName: 'chasseZoneInteret',
      }
    }
  };
  