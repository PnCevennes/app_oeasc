import { formFunctions } from "@/components/form/functions.js";

const reinitAreasLocalition = d => {
  d.areas_localisation_cadastre = [];
  d.areas_localisation_onf_prf = [];
  d.areas_localisation_onf_ug = [];
};

const reinitForetProprietaire = d => {
  d.label_foret = null;
  d.surface_renseignee = null;
  d.id_nomenclature_proprietaire_declarant = null;
  d.id_nomenclature_proprietaire_type = null;
  d.email = null;
  d.adresse = null;
  d.s_commune_proprietaire = null;
  d.telephone = null;
  d.nom_proprietaire = null;
};

const reinitAreasForet = ({ config, baseModel }) => {
  if (config.name != "areas_foret_onf") {
    baseModel.areas_foret_onf = null;
  }
  if (config.name != "areas_foret_dgd") {
    baseModel.areas_foret_dgd = null;
  }
  if (config.name != "areas_foret_sections") {
    baseModel.areas_foret_sections = [];
    baseModel.areas_foret_communes = [];
  }
  reinitAreasLocalition(baseModel);
  reinitForetProprietaire(baseModel);
};

const changeForetStatut = ({ config, baseModel }) => {
  baseModel.b_document = null;
  reinitAreasForet({ config, baseModel });
};

const changeForetDocument = ({ config, baseModel, $store }) => {
  if (baseModel.b_document == false) {
    const nomenclature = $store.getters.nomenclatureFromCdNomenclature(
      "OEASC_PROPRIETAIRE_TYPE",
      "PT_PRI"
    );
    this.baseModel.id_nomenclature_proprietaire_type =
      nomenclature.id_nomenclature;
    console.log(this.baseModel.id_nomenclature_proprietaire_type);
  }

  reinitAreasForet({ config, baseModel });
};

const changeAreaForet = ({ config, baseModel, $store }) => {
  reinitAreasForet({ config, baseModel });

  const id_area = baseModel[config.name];

  if (!(baseModel.b_document && id_area)) {
    return;
  }

  const mapService = $store.getters.mapService(config.name);
  const layer = mapService.findLayer("id_area", id_area);
  const code_foret = layer.feature.properties.area_code;
  $store.dispatch("foretFromCode", code_foret).then(foret => {
    for (const key of Object.keys(foret)) {
      if (key == "id_declarant") {
        continue;
      }
      baseModel[key] = foret[key];
    }
  });
};

const changeProprietaireDeclarant = ({ baseModel, $store }) => {
  if (baseModel.nom_proprietaire) {
    console.log("deja");
    // return;
  }
  setTimeout(() => {
    const nomenclature = $store.getters.nomenclature(
      baseModel.id_nomenclature_proprietaire_declarant
    );
    if (!(nomenclature && nomenclature.cd_nomenclature === "P_D_O_NP")) {
      return;
    }
    const user = $store.getters.user;
    baseModel.nom_proprietaire = `${user.nom_role} ${user.prenom_role}`;

    $store
      .dispatch("proprietaireFromIdDeclarant", user.id_role)
      .then(apiData => {
        if (!apiData.id_declarant) {
          return;
        }
        for (const key of Object.keys(apiData)) {
          baseModel[key] = apiData[key];
        }
      });
  }, 10);
};

const formsForet = {
  b_statut_public: {
    label: "Statut de la forêt",
    type: "bool_radio",
    labels: ["Public", "Privée"],
    change: changeForetStatut,
    required: true,
    help: true,
  },

  b_document: {
    label: ({ baseModel }) =>
      baseModel.b_statut_public
        ? "La forêt relève-t-elle du régime forestier ?"
        : "La forêt est-elle dotée d'un document de gestion durable ?",
    type: "bool_radio",
    labels: ["Oui", "Non"],
    condition: ({ baseModel }) =>
      [true, false].includes(baseModel.b_statut_public),
    change: changeForetDocument,
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
    condition: ({ baseModel }) =>
      baseModel.b_statut_public === true && baseModel.b_document === true,
    change: changeAreaForet
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
    condition: ({ baseModel }) =>
      baseModel.b_statut_public === false && baseModel.b_document === true,
    change: changeAreaForet
  },

  areas_foret_sections: {
    required: true,
    multiple: true,
    type: "select_map",
    legend: "Sections cadastrales",
    url: ({ areasContainer }) =>
      `api/ref_geo/areas_simples_from_type_code_container/l/OEASC_SECTION/${formFunctions.processAreas(
        areasContainer
      )}`,
    description: "la ou les sections cadastrales concernée",
    containerLegend: "Communes",
    containerDescription: "la ou les communes concernée",
    containerUrl: "api/ref_geo/areas_simples_from_type_code/l/OEASC_COMMUNE",
    containerMultiple: true,
    containerName: "areas_foret_communes",
    dataFieldNames: {
      value: "id_area",
      text: "label"
    },
    condition: ({ baseModel }) =>
      baseModel.b_document === false && baseModel.b_statut_public !== null,
    change: changeAreaForet
  },

  label_foret: {
    type: "text",
    label: "Nom de la foret",
    disabled: ({ baseModel }) => baseModel.b_document == true
  },

  surface_renseignee: {
    type: "number",
    label: "Superficie totale de la forêt (ha)",
    required: true,
    min: 0,
    disabled: ({ baseModel }) => baseModel.b_document == true
  },

  id_nomenclature_proprietaire_declarant: {
    label: "Le déclarant est-il le propriétaire de la forêt?",
    type: "nomenclature",
    display: "radio",
    nomenclatureType: "OEASC_PROPRIETAIRE_DECLARANT",
    required: true,
    condition: ({ baseModel }) => baseModel.b_document != true,
    change: changeProprietaireDeclarant
  },

  nom_proprietaire: {
    type: "text",
    required: true,
    label:
      "Nom (et prénom pour les personnes physiques) ou raison sociale du propriétaire",
    disabled: ({ baseModel }) => baseModel.b_document == true
  },

  telephone: {
    label: "Téléphone",
    type: "text",
    counter: true,
    // maxlength: "10",
    rules: [formFunctions.rules.telephone],
    required: ({ baseModel }) => baseModel.b_document != true,
    disabled: ({ baseModel }) => baseModel.b_document == true
  },

  email: {
    label: "E-mail",
    type: "text",
    rules: [formFunctions.rules.email],
    disabled: ({ baseModel }) => baseModel.b_document == true
  },

  adresse: {
    type: "text",
    label: "n°, rue, hameau, lieu-dit",
    required: ({ baseModel }) => baseModel.b_document != true,
    disabled: ({ baseModel }) => baseModel.b_document == true
  },

  s_commune_proprietaire: {
    type: "list_form",
    display: "autocomplete",
    label: "Commune",
    dataReloadOnSearch: true,
    placeholder:
      "Entrez les premières lettres de la commune et/ou le code postal séparés d'un espace",
    url: ({ search }) => `api/commons/communes/${search}`,
    valueFieldName: "nom_cp",
    textFieldName: "nom_cp",
    required: ({ baseModel }) => baseModel.b_document != true,
    disabled: ({ baseModel }) => baseModel.b_document == true
  }
};

export { formsForet };
