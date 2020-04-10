const sessionsForet = {

  foret_statut: {
    title: "Statut",
    groups: {
      statut: {
        forms: ["b_statut_public", "b_document"]
      }
    }
  },

  foret_localisation: {
    title: "Localisation",
    groups: {
      localisation_foret: {
        forms: [
          "areas_foret_onf",
          "areas_foret_dgd",
          "areas_foret_sections",
        ]
      }
    }
  },

  foret_informations: {
    title: "Nom et superficie",
    groups: {
      content: {
        forms: ["content_foret_onf", "content_foret_dgd"],
      },
      informations: {
        forms: ["label_foret", "surface_renseignee"]
      }
    }
  },

  foret_proprietaire: {
    title: "Propriétaire",
    groups: {
      content: {
        forms: ["content_foret_onf", "content_foret_dgd"],
      },
      proprietaire_declarant: {
        title: 'statut du propriétaire',
        forms: ["id_nomenclature_proprietaire_declarant"]
      },
      coordonnées: {
        direction: "row",
        groups: {
          informations: {
            title: "Informations",
            forms: ["nom_proprietaire", "telephone", "email"]
          },
          adresse: {
            title: "Adresse",
            forms: ["adresse", "s_commune_proprietaire"]
          }
        }
      }
    }
  }
};

export { sessionsForet };
