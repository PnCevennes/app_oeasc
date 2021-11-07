export default {
  group: "chasse",
  name: "zoneCynegetique",
  label: "Zone Cynegetique",
  labels: "Zones Cynegetiques",
  serverSide: true,

  defs: {
    id_zone_cynegetique: {
      label: "ID",
      type: "text",
      hidden: true
    },
    code_zone_cynegetique: {
      label: "Code",
      type: "text",
      required: true
    },
    nom_zone_cynegetique: {
      label: "Nom",
      type: "text",
      required: true
    },
    secteur: {
      label: "Secteur",
      required: true,
      type: 'list_form',
      list_type: "select",
      returnObject: true,
      storeName: "commonsSecteur",
      displayFieldName: 'code_secteur',
    }
  }
};
