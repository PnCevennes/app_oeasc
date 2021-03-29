export default {
  group: "chasse",
  name: "attributionMassif",
  label: "Attribution Massif",
  serverSide: true,
  defs: {
    id_attribution_massif: {
      label: "ID",
      hidden: true
    },
    saison: {
        label: 'saison',
        storeName: 'chasseSaison',
        type: 'list_form',
        list_type: 'select',
        returnObject: true,
    },
    espece: {
        label: 'Espèce',
        storeName: 'commonsEspece',
        type: 'list_form',
        list_type: 'select',
        returnObject: true,
    },
    zone_cynegetique: {
        label: 'Zone Cinégétique',
        storeName: 'chasseZoneCynegetique',
        type: 'list_form',
        list_type: 'select',
        returnObject: true,
    },
    nb_affecte_min: {
        label: 'nb affecté min',
        type: 'number',
        min: 0
    },
    nb_affecte_max: {
        label: 'nb affecté max',
        type: 'number',
        min: 0
    }
  },
};
