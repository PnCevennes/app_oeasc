export default {
  group: "chasse",
  name: "attributionMassif",
  label: "Attribution Massif",
  defs: {
    id_attribution_massif: {
      label: "ID",
      hidden: true
    },
    id_saison: {
        label: 'saison',
        storeName: 'chasseSaison'
    },
    id_espece: {
        label: 'Espèce',
        storeName: 'commonsEspece'
    },
    id_zone_cynegetique: {
        label: 'Zone Cinégétique',
        storeName: 'chasseZoneCynegetique'
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
  sortBy: ['id_saison', 'id_espece', 'id_zone_cynegetique']
};
