import { formFunctions } from '@/components/form/functions.js'

const reinitAreasForet = d => () => {
  d.areas_foret_onf = null;
  d.areas_foret_dgd = null;
  d.areas_foret_sessions = [];
};

const formsForet = {
  b_statut_public: {
    label: "Statut de la forêt",
    type: "bool_radio",
    labels: ["Public", "Privée"],
    change: reinitAreasForet,
    required: true,
  },
  b_document: {
    label: ({ baseModel }) =>
    baseModel.b_statut_public
        ? "La forêt relève-t-elle du régime forestier ?"
        : "La forêt est-elle dotée d'un document de gestion durable ?",
    type: "bool_radio",
    labels: ["Oui", "Non"],
    condition: ({ baseModel }) => [true, false].includes(baseModel.b_statut_public),
    change: reinitAreasForet,
    required: true
  },
  areas_foret_onf: {
    required: true,
    type: "select_map",
    legend: "Forêts relevant du régime forestier",
    description: "la forêt concernée",
    url: "api/ref_geo/areas_simples_from_type_code/l/OEASC_ONF_FRT",
    dataFieldNames: {
      value: "id_area",
      text: "label"
    },
    condition: ({ baseModel }) => baseModel.b_statut_public === true && baseModel.b_document === true
  },
  areas_foret_dgd: {
    required: true,
    type: "select_map",
    description: "la forêt concernée",
    legend: "Forêts dotées d'un document de gestion",
    url: "api/ref_geo/areas_simples_from_type_code/l/OEASC_DGD",
    dataFieldNames: {
      value: "id_area",
      text: "label"
    },
    condition: ({ baseModel }) => baseModel.b_statut_public === false && baseModel.b_document === true
  },
  areas_foret_sessions: {
    required: true,
    multiple: true,
    type: "select_map",
    legend: "Sections cadastrales",
    url: ({ areasContainer }) =>
      `api/ref_geo/areas_simples_from_type_code_container/l/OEASC_SECTION/${formFunctions.processAreas(areasContainer)}`,
    description: "la ou les sections cadastrales concernée",
    containerLegend: "Communes",
    containerDescription: "la ou les communes concernée",
    containerUrl: "api/ref_geo/areas_simples_from_type_code/l/OEASC_COMMUNE",
    containerMultiple: true,
    dataFieldNames: {
      value: "id_area",
      text: "label"
    },
    condition: ({ baseModel }) => baseModel.b_document === false && baseModel.b_statut_public !== null
  },
  nom_foret: {
    type: "text",
    label: "Nom de la foret"
  },
  surface_renseignee: {
    type: "number",
    label: "Superficie totale de la forêt (ha)",
    required: true,
    min: 0
  },
  id_nomenclature_proprietaire_type: {
    label: "Le déclarant est-il le propriétaire de la forêt?",
    type: "nomenclature",
    display: "radio",
    nomenclatureType: "OEASC_PROPRIETAIRE_DECLARANT",
    required: true,
  },
  nom_proprietaire: {
    type: "text",
    required: true,
    label:
      "Nom (et prénom pour les personnes physiques) ou raison sociale du propriétaire"
  },
  telephone: {
    label: "Téléphone",
    type: "text",
    counter: true,
    maxlength: "10",
    required: true,
    rules: [
      formFunctions.rules.telephone
    ]
  },
  email: {
    label: "E-mail",
    type: "text",
    rules: [formFunctions.rules.email]
  },
  adresse: {
    type: "text",
    required: true,
    label: "n°, rue, hameau, lieu-dit"
  },
  s_commune_proprietaire: {
    type: "list_form",
    display: "autocomplete",
    required: true,
    label: "Commune",
    dataReloadOnSearch:true,
    placeholder: "Entrez les premières lettres de la commune et/ou le code postal séparés d'un espace",
    url: ({search}) => `api/commons/communes/${search}`,
    valueFieldName: 'nom_cp',
    textFieldName: 'nom_cp',
  }
};

export { formsForet };