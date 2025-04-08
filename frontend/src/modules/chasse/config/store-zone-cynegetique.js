export default {
  group: "chasse",
  name: "zoneCynegetique",
  label: "Zone Cynegetique",
  labels: "Zones Cynegetiques",
  serverSide: true,

  options: { // Ajoute des param à la requête get pour filtrer les données
    page: 1, // on affiche la première page par défaut 
    sortBy: ["id_zone_cynegetique"], 
    sortDesc: [false], // tri en ordre décroissant
    fields: [ //les des champs des modèles à intégrer à la requête get
      "id_zone_cynegetique", "code_zone_cynegetique",
      "nom_zone_cynegetique",
      "secteur.id_secteur", "secteur.code_secteur",
      "secteur.nom_secteur"
    ]
  },



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
