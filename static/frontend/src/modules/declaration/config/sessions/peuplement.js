const sessionsPeuplement = {
  peuplement_localisation: {
    title: "Localisation",
    groups: {
      localisation: {
        forms: [
          "areas_localisation_cadastre",
          "areas_localisation_onf_ug"
        ]
      }
    }
  },
  peuplement_description: {
    title:
      "Description",
    groups: {
      essences: {
        title: "Essence(s)",
        forms: [
          "id_nomenclature_peuplement_essence_principale",
          "nomenclatures_peuplement_essence_secondaire",
          "nomenclatures_peuplement_essence_complementaire"
        ],
        help: 'group-form-essences'

      },
      superficie: {
        title: "Superficie du peuplement (ha)",

        forms: ["peuplement_surface"]
      },
      description: {
        title: "Origine et structure",
        direction: "row",
        forms: [
          // "id_nomenclature_peuplement_origine",
          "nomenclatures_peuplement_origine2",
          "id_nomenclature_peuplement_type",
          "nomenclatures_peuplement_maturite"
        ]
      }
    }
  },
  peuplement_protection: {
    title: "Protection",
    groups: {
      protection_question: {
        forms: [
          "b_peuplement_protection_existence",
        ]
      },
      protection: {
        forms: [
          "nomenclatures_peuplement_protection_type",
          "autre_protection"
        ]
      }

    }
  },
  peuplement_paturage: {
    title: "Pâturage domestique",
    groups: {
      paturage_question: {
        forms: [
          "b_peuplement_paturage_presence",
        ]
      },
      paturage_1: {
        direction: 'row',
        forms: [
          "nomenclatures_peuplement_paturage_type",
          "id_nomenclature_peuplement_paturage_statut",
        ]
      },
      paturage_2: {
        direction: 'row',
        forms: [
          "id_nomenclature_peuplement_paturage_frequence",
          "nomenclatures_peuplement_paturage_saison"
        ]
      },
    }
  },
  peuplement_autres: {
    title: "Autres / divers",
    groups: {
      autres: {
        forms: [
          "id_nomenclature_peuplement_acces",
          "nomenclatures_peuplement_espece"
        ]
      }
    }
  }
};

export { sessionsPeuplement };
