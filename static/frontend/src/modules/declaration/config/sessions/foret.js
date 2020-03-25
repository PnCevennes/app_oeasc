const sessionsForet = {
  foret_statut: {
    title: "Statut de la forêt",
    groups: {
      statut: {
        forms: ["b_statut_public", "b_document"]
      }
    }
  },
  foret_localisation: {
    title: "Localisation de la forêt",
    groups: {
      localisation_foret: {
        forms: [
          "areas_foret_onf",
          "areas_foret_dgd",
          "areas_foret_sessions",
        ]
      }
    }
  },
  foret_informations: {
    title: "Informations sur la forêt",
    groups: {
      informations: {
        forms: ["nom_foret", "surface_renseignee"]
      }
    }
  },
  foret_proprietaire: {
    title: "Coordonnées du propriétaire",
    groups: {
      proprietaire_declarant: {
        title: 'statut du propriétaire',
        forms: ["id_nomenclature_proprietaire_type"]
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
