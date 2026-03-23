export default {
  group: 'chasse',
  name: 'zoneCynegetique',
  label: 'Zone Cynegetique',
  labels: 'Zones Cynegetiques',
  serverSide: true, // si pagination et tri sont gérés côté serveur

  options: {
    // Ajoute des param à la requête get pour filtrer les données
    page: 1, // on affiche la première page par défaut
    sortBy: ['nom_zone_cynegetique'],
    sortDesc: [false], // tri en ordre décroissant
  },

  defs: {
    id_zone_cynegetique: {
      label: 'ID',
      type: 'text',
      hidden: true,
    },
    code_zone_cynegetique: {
      label: 'Code',
      type: 'text',
      required: true,
    },
    nom_zone_cynegetique: {
      label: 'Nom',
      type: 'text',
      required: true,
    },
    secteur: {
      label: 'Secteur',
      required: true,
      type: 'list_form',
      list_type: 'select',
      returnObject: true, // true si ca ne retourne pas qu'une valeur mais plusieurs dans un objet
      storeName: 'commonsSecteur',
      displayFieldName: 'code_secteur',
    },
  },
};
