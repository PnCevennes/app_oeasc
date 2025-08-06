


export default {
  group: "chasse",
  name: "attribution",
  label: "Attribution",
  serverSide: true,
  displayFieldName: 'numero_bracelet',

  options: { // Ajoute des params à la requête get pour filtrer les données
    page: 1, // on affiche la première page par défaut 
    sortBy: ["saison", "id_attribution"], 
    sortDesc: [true, true], // tri en ordre décroissant
    // fields: [//les des champs des modèles à intégrer à la requête get
    //   // 'numero_bracelet', 'id_attribution',
    //   "saison.id_saison", "saison.nom_saison",
    //   "type_bracelet.id_type_bracelet", "type_bracelet.code_type_bracelet",
    //   "zone_cynegetique_affectee.id_zone_cynegetique", "zone_cynegetique_affectee.nom_zone_cynegetique",
    //   'zone_indicative_affectee.id_zone_indicative', 'zone_indicative_affectee.nom_zone_indicative',
    // ], 

  },

  defs: {
    numero_bracelet: {
      label: 'Numéro bracelet',
      type: "text",
    },
    id_attribution: {
      label: "ID",
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
        dataReloadOnSearch: true
    },
  }
};
