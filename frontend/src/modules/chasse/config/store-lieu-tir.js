export default {
    group: "chasse",
    name: "lieuTir",
    label: "Lieu de tir",
    defs: {
      id_lieu_tir: {
        label: "ID",
        hidden: true
      },
      code_lieu_tir: {
        label: "Code",
        required: true
      },
      nom_lieu_tir: {
        label: "Nom",
        required: true
      },
      id_zone_interet: {
        storeName: 'chasseZoneInteret',
        displayFieldName: 'code_zone_interet'
      }
    }
  };
  