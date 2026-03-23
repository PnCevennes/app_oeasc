export default {
  group: 'chasse',
  name: 'zoneIndicative',
  label: 'Zone indicatives',
  labels: 'Zones indicatives',
  serverSide: true, // si pagination et tri sont gérés côté serveur

  options: {
    // Ajoute des param à la requête get pour filtrer les données

    page: 1, // on affiche la première page par défaut
    sortBy: ['id_zone_indicative'],
    sortDesc: [true], // tri en ordre décroissant
  },

  defs: {
    id_zone_indicative: {
      label: 'ID',
      type: 'text',
      hidden: true,
    },
    code_zone_indicative: {
      label: 'Code',
      type: 'text',
      required: true,
    },
    nom_zone_indicative: {
      label: 'Nom',
      type: 'text',
      required: true,
    },
    zone_cynegetique: {
      label: 'Zone cinégétique',
      type: 'list_form',
      list_type: 'select',
      returnObject: true, // true si ca ne retourne pas qu'une valeur mais plusieurs dans un objet
      displayFieldName: 'code_zone_cynegetique',
      storeName: 'chasseZoneCynegetique',
      required: true,
    },
  },
};
