const processEssenceSort = a => {
  const b = a.label_fr.toLowerCase();
  b.replace("é", "e");
  b.replace("ê", "e");
  return b;
};

const sortEssence = (a, b) => {
  if (a.label_fr.includes("Autre") && b.label_fr.includes("Autre")) {
    return 1 - 2 * (aa - bb);
  }
  if (a.label_fr.includes("Autre")) {
    return 1;
  }
  if (b.label_fr.includes("Autre")) {
    return -1;
  }

  const aa = processEssenceSort(a);
  const bb = processEssenceSort(b);
  return 1 - 2 * (aa - bb);
};

const getEssencesSelected = ({ baseModel, $store }) => {
  const essencesSelected = {};

  essencesSelected["all"] = [
    ...baseModel.nomenclatures_peuplement_essence_secondaire,
    ...baseModel.nomenclatures_peuplement_essence_complementaire
  ];
  if (baseModel.id_nomenclature_peuplement_essence_principale) {
    essencesSelected["all"].push(
      baseModel.id_nomenclature_peuplement_essence_principale
    );
  }
  essencesSelected["degats"] = [
    ...baseModel.nomenclatures_peuplement_essence_secondaire
  ];
  if (baseModel.id_nomenclature_peuplement_essence_principale) {
    essencesSelected["degats"].push(
      baseModel.id_nomenclature_peuplement_essence_principale
    );
  }

  for (const degat of baseModel.degats || []) {
    const nomenclature = $store.getters.nomenclature(
      degat.id_nomenclature_degat_type
    );
    const cd = nomenclature.cd_nomenclature;
    if (cd !== "P/C") {
      essencesSelected[cd] = [];
      for (const degat_essence of degat.degat_essences || []) {
        essencesSelected[cd].push(degat_essence.id_nomenclature_degat_essence);
      }
    }
  }
  return essencesSelected;
};

const processAreas = function(areas) {
  return (Array.isArray(areas) ? areas : [areas]).join("-");
};

const processItems = {
  essence: ({ config, dataItems, baseModel }) => {
    const items = dataItems.filter(item => {
      const modelArray = Array.isArray(baseModel[config.name])
        ? baseModel[config.name]
        : [baseModel[config.name]];

      const selected = config.essencesSelected[config.essenceType] || [];

      const condData =
        config.essenceType === "all" ||
        !!config.essencesSelected["degats"].find(
          i => i === item.id_nomenclature
        );
      const condAlreadySelected = !!selected.find(
        i => i === item.id_nomenclature
      );
      const condCurrentFormSelected = !!modelArray.find(
        i => i === item.id_nomenclature
      );

      return (condData && !condAlreadySelected) || condCurrentFormSelected;
    });
    items.sort(sortEssence);

    return items;
  }
};

const change = {};
const rules = {
  requiredBool: v => [true, false].includes(v) || "Ce champs est obligatoire.",
  required: v => !!v || "Ce champs est obligatoire.",
  requiredListSimple: v => !!v || "Veuillez choisir un élément dans la liste.",
  requiredListMultiple: v =>
    v.length > 0 || "Veuillez choisir un ou plusieurs éléments dans la liste.",
  number: v => {
    return (
      "" == v || Number(v) == 0 || !!Number(v) || "Veuillez entrer un nombre"
    );
  },
  telephone: v =>
    !v ||
    /^0[1-9]([ -]?[0-9][0-9]){4}$/.test(v) ||
    "Le numéro de téléphone doit être valide (10 chiffres).",
  email: v => !v || /.+@.+\..+/.test(v) || "L'e-mail doit être valide.",
  maxLength: max => v =>
    v.length <= max || `Choisir un maximum de ${max} éléments.`,
  maxLengthEssence: max => v =>
    v.length <= max || `${max} essence${max > 1 ? "s" : ""} maximum.`,
  min: min => v =>
    v >= min || `La valeur doit être supérieure ou égale à ${min}.`,
  max: max => v =>
    v >= max || `La valeur doit être inférieure ou égale à ${max}.`,

  processRules: function(config) {
    config.rules = config.rules || [];

    if (config.required) {
      let ruleRequired = rules.required;
      if (["list-form", "nomenclature", "select_map"].includes(config.type)) {
        ruleRequired = config.multiple
          ? rules.requiredListMultiple
          : rules.requiredListSimple;
      } else if (["bool_radio", "bool_switch"].includes(config.type)) {
        ruleRequired = rules.requiredBool;
      }
      config.rules.push(ruleRequired);
    }

    if (config.type == "number") {
      config.rules.push(rules.number);
    }

    for (const key of ["maxLength", "maxLengthEssence", "min", "max"]) {
      if (key in config) {
        config.rules.push(rules[key](config[key]));
      }
    }
  }
};

const formFunctions = {
  processItems,
  change,
  rules,
  getEssencesSelected,
  processAreas
};

export { formFunctions };
