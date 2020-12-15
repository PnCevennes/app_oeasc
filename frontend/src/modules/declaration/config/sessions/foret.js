export default {
  foret_statut: {
    title: "Statut",
    groups: [{ forms: ["b_statut_public", "b_document"] }]
  },

  foret_localisation: {
    title: "Localisation",
    groups: [
      {
        forms: ["areas_foret_onf", "areas_foret_dgd", "areas_foret_sections"]
      }
    ]
  },

  foret_informations: {
    title: "Nom et superficie",
    groups: [
      {
        forms: ["content_foret_onf", "content_foret_dgd"]
      },
      {
        forms: ["label_foret", "surface_renseignee"]
      }
    ]
  },

  foret_proprietaire: {
    title: "Propriétaire",
    groups: [
      {
        forms: ["content_foret_onf", "content_foret_dgd"]
      },
      {
        title: "Statut du propriétaire",
        forms: ["id_nomenclature_proprietaire_declarant"]
      },
      {
        direction: "row",
        groups: [
          {
            title: "Informations",
            forms: [
              "nom_proprietaire",
              "telephone",
              "email"
            ]
          },
          {
            title: "Adresse",
            forms: [
              "adresse",
              "s_commune_proprietaire"
            ]
          }
        ]
      }
    ]
  }
};
