export default {
    group: "chasse",
    name: "zoneCynegetique",
    label: "Zone Cynegetique",
    labels: "Zones Cynegetiques",
    defs: {
      id_zone_cynegetique: {
        label: "ID",
        hidden: true
      },
      code_zone_cynegetique: {
        label: "Code",
        required: true
      },
      nom_zone_cynegetique: {
        label: "Nom",
        required: true
      },
      id_secteur: {
          label: "Secteur",
          required: true,
          displayFieldName: 'code_secteur',
          storeName: 'commonsSecteur'
      }
    }
  };
  