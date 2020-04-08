const sessionsPeuplement = {
  peuplement_localisation: {
    title: "Localisation du peuplement",
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
      "Description du peuplement: essence(s), origine, structure, maturité",
    groups: {
      essences: {
        title: "Essence(s) caractérisant le peuplement",
        forms: [
          "id_nomenclature_peuplement_essence_principale",
          "nomenclatures_peuplement_essence_secondaire",
          "nomenclatures_peuplement_essence_complementaire"
        ]
      },
      superficie: {
        title: "Superficie",

        forms: ["peuplement_surface"]
      },
      description: {
        title: "Informations sur le peuplement",
        direction: "row",
        forms: [
          "id_nomenclature_peuplement_origine",
          "id_nomenclature_peuplement_type",
          "nomenclatures_peuplement_maturite"
        ]
      }
    }
  },
  peuplement_protection: {
    title: "Protection du peupement",
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
    title: "Pâturage domenstique",
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
    title: "Autres renseignements",
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
