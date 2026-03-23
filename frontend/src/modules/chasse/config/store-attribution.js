export default {
  group: 'chasse',
  name: 'attribution',
  label: 'Attribution',
  serverSide: true,
  displayFieldName: 'numero_bracelet',

  options: {
    // Ajoute des params à la requête get pour filtrer les données
    page: 1, // on affiche la première page par défaut
    sortBy: ['saison', 'id_attribution'],
    sortDesc: [true, true], // tri en ordre décroissant
  },

  defs: {
    numero_bracelet: {
      label: 'Numéro bracelet',
      type: 'text',
    },
    id_attribution: {
      label: 'ID',
      hidden: true,
      type: 'text',
    },
    type_bracelet: {
      label: 'Type de bracelet',
      storeName: 'chasseTypeBracelet',
      type: 'list_form',
      list_type: 'select',
      returnObject: true,
    },
    saison: {
      label: 'saison',
      storeName: 'chasseSaison',
      type: 'list_form',
      list_type: 'autocomplete',
      returnObject: true,
      dataReloadOnSearch: true,
    },
    zone_cynegetique_affectee: {
      label: 'Zone cynégétique affectée',
      storeName: 'chasseZoneCynegetique',
      type: 'list_form',
      list_type: 'select',
      returnObject: true,
    },
    zone_indicative_affectee: {
      label: 'Zone indicative affectée',
      storeName: 'chasseZoneIndicative',
      type: 'list_form',
      list_type: 'autocomplete',
      returnObject: true,
      dataReloadOnSearch: true,
    },
  },
};
