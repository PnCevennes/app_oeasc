export default {
    group: "chasse",
    name: "zoneInteret",
    label: "Zone d'intérêt",
    labels: "Zones d'intérêt",
    serverSide: true,
    defs: {
      id_zone_interet: {
        label: "ID",
        type: 'text',
        hidden: true
        
      },
      code_zone_interet: {
        label: "Code",
        type: 'text',
        required: true
        
      },
      nom_zone_interet: {
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
  