export default {
  group: "chasse",
  name: "attribution",
  label: "Attribution",
  serverSide: true,
  displayFieldName: 'numero_bracelet',
  defs: {
    label: {  
      label: 'Attribution'
    },
    id_attribution: {
      label: "ID",
      hidden: true,
    },
    id_type_bracelet: {
        label: 'Type de bracelet',
        storeName: 'chasseTypeBracelet'
    },
    id_saison: {
        label: 'saison',
        storeName: 'chasseSaison'
    },
    id_zone_cynegetique_affectee: {
        label: 'Zone cynégétique affectée',
        storeName: 'chasseZoneCynegetique'
    },
    id_zone_interet_affectee: {
        label: 'Zone intérêt affectée',
        storeName: 'chasseZoneInteret'
    },
  }
};
