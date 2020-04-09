// import { rules } from "@/components/form/functions.js";
import { formFunctions } from "@/components/form/functions.js";

const formsPeuplement = {
  areas_localisation_cadastre: {
    required: true,
    multiple: true,
    type: "select_map",
    legend: "Parcelles cadastrales",
    description:
      "la ou les parcelles forestières cadastrales sur lesquelles est située le peuplement concerné par les dégâts",
    dataFieldNames: {
      value: "id_area",
      text: "label"
    },
    condition: ({ baseModel }) =>
      (!(baseModel.b_statut_public == true && baseModel.b_document == true)) &&
        (baseModel.areas_foret_dgd ||
      baseModel.areas_foret_sections.length),
    url: ({ baseModel }) =>
      `api/ref_geo/areas_simples_from_type_code_container/l/OEASC_CADASTRE/${formFunctions.processAreas(
        baseModel.areas_foret_dgd || baseModel.areas_foret_sections
      )}`,
      help: true
  },

  areas_localisation_onf_ug: {
    required: true,
    multiple: true,
    type: "select_map",
    legend: "Unités de gestion",
    description:
      " la ou les unités de gestion forestières sur lesquelles est située le peuplement concerné par les dégâts",
    dataFieldNames: {
      value: "id_area",
      text: "label"
    },
    condition: ({ baseModel }) => baseModel.areas_foret_onf,
    url: ({ areasContainer }) =>
      `api/ref_geo/areas_simples_from_type_code_container/l/OEASC_ONF_UG/${formFunctions.processAreas(
        areasContainer
      )}`,
    containerName: "areas_localisation_onf_prf",
    containerLegend: "Parcelles forestières",
    containerDescription:
      "la ou les parcelles forestières sur lesquelles est située le peuplement concerné",
    containerUrl: ({ baseModel }) =>
      `api/ref_geo/areas_simples_from_type_code_container/l/OEASC_ONF_PRF/${formFunctions.processAreas(
        baseModel.areas_foret_onf
      )}`,
    containerMultiple: true,
    help: true

  },

  id_nomenclature_peuplement_essence_principale: {
    required: true,
    label: "Essence principale",
    type: "essence",
    essenceType: "all",
  },

  nomenclatures_peuplement_essence_secondaire: {
    multiple: true,
    label: "Essence(s) secondaire(s)",
    type: "essence",
    essenceType: "all",
    maxLength: 3,
  },

  nomenclatures_peuplement_essence_complementaire: {
    multiple: true,
    label: "Essence(s) complémentaire(s)",
    type: "essence",
    essenceType: "all",
    maxLength: 3,
  },

  peuplement_surface: {
    label: "Superficie du Peuplement (ha)",
    type: "number",
    min: 0
  },

  id_nomenclature_peuplement_origine: {
    label: "Origine du peuplement",
    type: "nomenclature",
    display: "radio",
    nomenclatureType: "OEASC_PEUPLEMENT_ORIGINE",
    required: true,
    help: true
  },

  id_nomenclature_peuplement_type: {
    label: "Type de peuplement",
    type: "nomenclature",
    display: "radio",
    nomenclatureType: "OEASC_PEUPLEMENT_TYPE",
    required: true,
    help: true,
    helps: {
      except: ['NSP']
    }
  },

  nomenclatures_peuplement_maturite: {
    label: "Maturité du peuplement",
    type: "nomenclature",
    display: "radio",
    nomenclatureType: "OEASC_PEUPLEMENT_MATURITE",
    multiple: true,
    required: true,
    condition: ({ baseModel, $store }) => {
      const nomenclature = $store.getters.nomenclature(
        baseModel.id_nomenclature_peuplement_type
      );
      return nomenclature && nomenclature.cd_nomenclature !== "FIRR";
    },
    help: true
  },

  b_peuplement_protection_existence: {
    label: "Existence de dispositifs de protection contre le grand gibier ?",
    type: "bool_radio",
    labels: ["Oui", "Non"],
    required: true
  },

  b_peuplement_paturage_presence: {
    label: "Présence de pâturage domestique ?",
    type: "bool_radio",
    labels: ["Oui", "Non"],
    required: true,
    help: true
  },

  nomenclatures_peuplement_protection_type: {
    label: "Type de protection",
    type: "nomenclature",
    display: "radio",
    nomenclatureType: "OEASC_PEUPLEMENT_PROTECTION_TYPE",
    multiple: true,
    required: true,
    condition: ({ baseModel }) => baseModel.b_peuplement_protection_existence
  },

  autre_protection: {
    type: "text",
    required: true,
    label: "Autre protection (préciser)",
    condition: ({ baseModel, $store }) =>
      baseModel.b_peuplement_protection_existence &&
      baseModel.nomenclatures_peuplement_protection_type.find(
        id_nomenclature => {
          const nomenclature = $store.getters.nomenclature(id_nomenclature);
          return nomenclature && nomenclature.cd_nomenclature == "PPRT_AUT";
        }
      )
  },

  nomenclatures_peuplement_paturage_type: {
    label: "Type de pâturage",
    type: "nomenclature",
    display: "radio",
    nomenclatureType: "OEASC_PEUPLEMENT_PATURAGE_TYPE",
    multiple: true,
    required: true,
    condition: ({ baseModel }) => baseModel.b_peuplement_paturage_presence
  },
  id_nomenclature_peuplement_paturage_statut: {
    label: "Statut du pâturage",
    type: "nomenclature",
    display: "radio",
    nomenclatureType: "OEASC_PEUPLEMENT_PATURAGE_STATUT",
    required: true,
    condition: ({ baseModel }) => baseModel.b_peuplement_paturage_presence
  },
  id_nomenclature_peuplement_paturage_frequence: {
    label: "Fréquence du pâturage",
    type: "nomenclature",
    display: "radio",
    nomenclatureType: "OEASC_PEUPLEMENT_PATURAGE_FREQUENCE",
    required: true,
    condition: ({ baseModel }) => baseModel.b_peuplement_paturage_presence
  },
  nomenclatures_peuplement_paturage_saison: {
    label: "Saisonalité du pâturage",
    type: "nomenclature",
    display: "radio",
    nomenclatureType: "OEASC_PEUPLEMENT_PATURAGE_SAISON",
    multiple: true,
    required: true,
    condition: ({ baseModel, $store }) => {
      const nomenclature = $store.getters.nomenclature(
        baseModel.id_nomenclature_peuplement_paturage_frequence
      );
      return (
        baseModel.b_peuplement_paturage_presence &&
        nomenclature &&
        nomenclature.cd_nomenclature == "PPAF_PER"
      );
    }
  },
  id_nomenclature_peuplement_acces: {
    label: "Accessibilité du peuplement",
    type: "nomenclature",
    display: "radio",
    nomenclatureType: "OEASC_PEUPLEMENT_ACCES",
    required: true,
    help: true
  },
  nomenclatures_peuplement_espece: {
    label:
      "Espèces de grand gibier dont la présence est avérée sur le peuplement (observations directes ou indices de présence)",
    type: "nomenclature",
    display: "radio",
    nomenclatureType: "OEASC_PEUPLEMENT_ESPECE",
    multiple: true,
    required: true
  }
};

export { formsPeuplement };
