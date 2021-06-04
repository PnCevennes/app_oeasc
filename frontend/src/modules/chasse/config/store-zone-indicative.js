export default {
    group: "chasse",
    name: "zoneIndicative",
    label: "Zone indicatives",
    labels: "Zones indicatives",
    serverSide: true,
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
  