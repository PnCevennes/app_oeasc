export default {
    group: "chasse",
    name: "zoneInteret",
    label: "Zone d'intérêt",
    labels: "Zones d'intérêt",
    defs: {
      id_zone_interet: {
        label: "ID",
        hidden: true
      },
      code_zone_interet: {
        label: "Code",
        required: true
      },
      nom_zone_interet: {
        label: "Nom",
        required: true
      },
      id_zone_cynegetique: {
          label: "Zone cinégétique",
          required: true,
          displayFieldName: 'code_zone_cynegetique',
          storeName: 'chasseZoneCynegetique'
      },
    }
  };
  