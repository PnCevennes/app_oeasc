import { copy } from "@/core/js/util/util.js";


/**
 * Convertit une chaîne au format "JJMM" en une date valide comprise dans un intervalle donné.
 *
 * @param {string} v - La chaîne représentant le jour et le mois au format "JJMM".
 * @param {string} dateMin - La date minimale autorisée au format "AAAA-MM-JJ".
 * @param {string} dateMax - La date maximale autorisée au format "AAAA-MM-JJ".
 * @returns {string|Object} - Retourne la date au format "AAAA-MM-JJ" si elle est valide et dans l'intervalle,
 *                            sinon un objet contenant une propriété `err` avec un message d'erreur détaillé.
 *
 * @example
 * // Pour une entrée valide
 * getDateFromMMJJ("1506", "2020-01-01", "2023-12-31"); // "2020-06-15" ou "2023-06-15" si dans l'intervalle
 *
 * @example
 * // Pour une entrée invalide
 * getDateFromMMJJ("3213", "2020-01-01", "2023-12-31"); // { err: "La valeur de JJMM : 3213 n'est pas valide" }
 *
 * @description
 * Cette fonction vérifie que la chaîne passée en paramètre correspond bien au format "JJMM" (jour et mois sur 4 caractères).
 * Elle tente ensuite de construire une date en utilisant l'année de la date minimale et maximale, puis vérifie si la date
 * obtenue est valide et comprise dans l'intervalle spécifié. Si la date n'est pas valide ou hors intervalle, un message
 * d'erreur explicite est retourné.
 */
const getDateFromMMJJ =(v, dateMin, dateMax) => {
  if (!v || (v && v.length != 4)) {
    return { err: `${v} doit être au format "JJMM" (4 caractères)`}
  }

  const jj = v.substring(0,2)
  const mm = v.substring(2,4)

  // if (new Date(`${2000}-${jj}-${mm}`))
  let condDate = false
  for (const aa of [dateMin, dateMax].map(d => d.split('-')[0])) {
    const dateCur = `${aa}-${mm}-${jj}`;
    const testDate = (new Date(dateCur)) != 'Invalid Date';
    condDate = condDate || testDate
    if(testDate && dateCur >= dateMin && dateCur <= dateMax) {
      return dateCur
    }
  }

  if (condDate) {
    return {err: `La date ne convient pas à l'intervalle ${dateMin.split('-').reverse().join('/')} - ${dateMax.split('-').reverse().join('/')}`}
  } else {
    return {err: `La valeur de JJMM : ${v} n'est pas valide`}
  }
}



/**
 * Traite et normalise le label français d'une essence pour le tri.
 * Convertit le texte en minuscules et remplace certains caractères accentués.
 *
 * @param {Object} a - Objet représentant une essence, contenant la propriété 'label_fr'.
 * @returns {string} Le label français normalisé, prêt pour le tri.
 */
const processEssenceSort = a => {
  const b = a.label_fr.toLowerCase();
  b.replace("é", "e");
  b.replace("ê", "e");
  return b;
};



/**
 * Trie deux objets selon leur propriété `label_fr` et une fonction de traitement personnalisée.
 *
 * - Si les deux objets ont "Autre" dans leur `label_fr`, ils sont triés selon la valeur retournée par `processEssenceSort`.
 * - Si seul le premier objet contient "Autre", il est placé après le second.
 * - Si seul le second objet contient "Autre", il est placé avant le premier.
 * - Sinon, le tri se fait selon la valeur retournée par `processEssenceSort` appliquée à chaque objet.
 *
 * @param {Object} a - Premier objet à comparer, doit contenir la propriété `label_fr`.
 * @param {Object} b - Second objet à comparer, doit contenir la propriété `label_fr`.
 * @returns {number} Un nombre négatif si `a` doit précéder `b`, positif si `a` doit suivre `b`, ou zéro s'ils sont équivalents.
 */
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



/**
 * Récupère les essences sélectionnées dans le modèle de base et les organise par type.
 *
 * - "all" : contient toutes les essences principales, secondaires et complémentaires.
 * - "degats" : contient les essences principales et secondaires liées aux dégâts.
 * - Pour chaque type de dégât (hors "P/C"), ajoute les essences associées sous la clé correspondant au code nomenclature du dégât.
 *
 * @param {Object} params - Objet contenant le modèle de base et le store Vuex.
 * @param {Object} params.baseModel - Modèle de base du formulaire, contenant les essences et dégâts.
 * @param {Object} params.$store - Store Vuex, utilisé pour récupérer les nomenclatures.
 * @returns {Object} Un objet dont les clés sont les types d'essence ou de dégât, et les valeurs sont des tableaux d'identifiants d'essence.
 *
 * @example
 * // Retourne un objet du type :
 * // {
 * //   all: [idEssence1, idEssence2, ...],
 * //   degats: [idEssence1, ...],
 * //   "CODE_DEGAT": [idEssenceDegat1, ...]
 * // }
 */
const getEssencesSelected = ({ baseModel, $store }) => {
  const essencesSelected = {};

  // Ajoute toutes les essences secondaires et complémentaires dans "all"
  essencesSelected["all"] = [
    ...baseModel.nomenclatures_peuplement_essence_secondaire,
    ...baseModel.nomenclatures_peuplement_essence_complementaire
  ];
  // Ajoute l'essence principale si elle existe
  if (baseModel.id_nomenclature_peuplement_essence_principale) {
    essencesSelected["all"].push(
      baseModel.id_nomenclature_peuplement_essence_principale
    );
  }

  // Ajoute les essences secondaires et principale dans "degats"
  essencesSelected["degats"] = [
    ...baseModel.nomenclatures_peuplement_essence_secondaire
  ];
  if (baseModel.id_nomenclature_peuplement_essence_principale) {
    essencesSelected["degats"].push(
      baseModel.id_nomenclature_peuplement_essence_principale
    );
  }

  // Pour chaque dégât, ajoute les essences associées sous la clé du code nomenclature du dégât (sauf "P/C")
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



/**
 * Traite une ou plusieurs zones et les convertit en une chaîne de caractères séparée par des tirets.
 *
 * @param {(string|string[])} areas - Une zone ou un tableau de zones à traiter.
 * @returns {string} Une chaîne contenant toutes les zones, séparées par des tirets.
 *
 * @example
 * // Pour une seule zone
 * processAreas("zone1"); // Retourne "zone1"
 *
 * @example
 * // Pour plusieurs zones
 * processAreas(["zone1", "zone2"]); // Retourne "zone1-zone2"
 */
const processAreas = function(areas) {
  return (Array.isArray(areas) ? areas : [areas]).join("-");
};


/**
 * Filtre et trie les éléments selon la configuration et le modèle de base pour le type "essence".
 *
 * @function essence
 * @memberof processItems
 * @param {Object} params - Les paramètres de la fonction.
 * @param {Object} params.config - La configuration du formulaire, incluant le nom du champ, le type d'essence et les essences sélectionnées.
 * @param {Array<Object>} params.dataItems - La liste des éléments à traiter.
 * @param {Object} params.baseModel - Le modèle de base du formulaire, contenant les valeurs sélectionnées.
 * @returns {Array<Object>} Les éléments filtrés et triés selon les critères définis.
 *
 * @description
 * Cette fonction effectue les opérations suivantes :
 * - Filtre les éléments selon le type d'essence sélectionné et les éléments déjà sélectionnés.
 * - Prend en compte les éléments déjà présents dans le formulaire courant.
 * - Trie les éléments filtrés à l'aide de la fonction `sortEssence`.
 */
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


/**
 * Ensemble de règles de validation pour les champs de formulaire.
 * Chaque règle retourne true si la valeur est valide, sinon un message d'erreur en français.
 */
const rules = {
  /**
   * Vérifie que la valeur est un booléen (true ou false).
   * @param {*} v - Valeur à tester.
   * @returns {true|string} - true si valide, sinon message d'erreur.
   */
  requiredBool: v => [true, false].includes(v) || "Ce champs est obligatoire.",

  /**
   * Vérifie que la valeur n'est pas nulle, indéfinie ou vide.
   * @param {*} v - Valeur à tester.
   * @returns {true|string} - true si valide, sinon message d'erreur.
   */
  required: v => ![null, undefined, ''].includes(v) || "Ce champs est obligatoire.",

  /**
   * Vérifie qu'une valeur (simple) a été sélectionnée dans une liste.
   * @param {*} v - Valeur à tester.
   * @returns {true|string} - true si valide, sinon message d'erreur.
   */
  requiredListSimple: v => !!v || "Veuillez choisir un élément dans la liste.",

  /**
   * Vérifie qu'au moins une valeur a été sélectionnée dans une liste multiple.
   * @param {Array} v - Valeur à tester.
   * @returns {true|string} - true si valide, sinon message d'erreur.
   */
  requiredListMultiple: v =>
    v && v.length > 0 || "Veuillez choisir un ou plusieurs éléments dans la liste.",

  /**
   * Vérifie que la valeur est un nombre valide.
   * Accepte la chaîne vide ou zéro.
   * @param {*} v - Valeur à tester.
   * @returns {true|string} - true si valide, sinon message d'erreur.
   */
  number: v => { 
    return (
      "" == v || Number(v) == 0 || !!Number(v) || `Veuillez entrer un nombre ${v && v.includes(',') ? "(utiliser un point à la place de la virgule pour les décimales)" : ''}`
    );
  },

  /**
   * Vérifie que le numéro de téléphone est valide (format français, 10 chiffres).
   * @param {string} v - Valeur à tester.
   * @returns {true|string} - true si valide, sinon message d'erreur.
   */
  telephone: v => !v ||
    /^0[1-9]([ -]?[0-9][0-9]){4}$/.test(v) ||
    "Le numéro de téléphone doit être valide (10 chiffres)."
  ,

  /**
   * Vérifie que l'adresse e-mail est valide.
   * @param {string} v - Valeur à tester.
   * @returns {true|string} - true si valide, sinon message d'erreur.
   */
  email: v => !v || /.+@.+\..+/.test(v) || "L'e-mail doit être valide.",

  /**
   * Vérifie que la longueur de la valeur ne dépasse pas un maximum.
   * @param {number} max - Longueur maximale autorisée.
   * @returns {function} - Fonction de validation.
   */
  maxLength: max => v =>
    v.length <= max || `Choisir un maximum de ${max} éléments.`,

  /**
   * Vérifie que le nombre d'essences sélectionnées ne dépasse pas un maximum.
   * @param {number} max - Nombre maximum d'essences.
   * @returns {function} - Fonction de validation.
   */
  maxLengthEssence: max => v =>
    v && ( v.length <= max ) || `${max} essence${max > 1 ? "s" : ""} maximum.`,

  /**
   * Vérifie que la valeur est supérieure ou égale à un minimum.
   * @param {number} min - Valeur minimale.
   * @returns {function} - Fonction de validation.
   */
  min: min => v =>
    v >= min || `La valeur doit être supérieure ou égale à ${min}.`,

  /**
   * Vérifie que la valeur est inférieure ou égale à un maximum.
   * @param {number} max - Valeur maximale.
   * @returns {function} - Fonction de validation.
   */
  max: max => v =>
    v >= max || `La valeur doit être inférieure ou égale à ${max}.`,

  /**
   * Vérifie que la date saisie est supérieure ou égale à la date minimale.
   * @param {string} dateMin - Date minimale au format AAAA-MM-JJ.
   * @returns {function} - Fonction de validation.
   */
  dateMin: dateMin => v => {
    const dateMinFr = dateMin.split('-').reverse().join('/');
    return v >= dateMin || `La date saisie est inférieure à la date minimale : ${dateMinFr}`;
  },

  /**
   * Vérifie que la date saisie est inférieure ou égale à la date maximale.
   * @param {string} dateMax - Date maximale au format AAAA-MM-JJ.
   * @returns {function} - Fonction de validation.
   */
  dateMax: dateMax => v => {
    const dateMaxFr = dateMax.split('-').reverse().join('/');
    return v <= dateMax || `La date saisie est supérieure à la date maximale : ${dateMaxFr}`;
  },

  /**
   * Applique les règles de validation à la configuration d'un champ de formulaire.
   * Ajoute dynamiquement les règles selon le type et les propriétés du champ.
   * @param {Object} config - Configuration du champ de formulaire.
   */
  processRules: function(config) {
    config.rules = config.rules || [];

    // Ajout de la règle "required" selon le type de champ
    if (config.required) {
      let ruleRequired = rules.required;
      if (["list-form", "nomenclature", "select_map", 'essence'].includes(config.type)) {
        ruleRequired = config.multiple
          ? rules.requiredListMultiple
          : rules.requiredListSimple;
      } else if (["bool_radio", "bool_switch"].includes(config.type)) {
        ruleRequired = rules.requiredBool;
      }
      config.rules.push(ruleRequired);
    }

    // Ajout de la règle "number" pour les champs numériques
    if (config.type == "number") {
      config.rules.push(rules.number);
    }

    // Ajout de la règle "email" pour les champs email
    if(config.type == 'email') {
      config.rules.push(rules.email)
    }

    // Ajout des règles de longueur et de valeur minimale/maximale si présentes dans la config
    for (const key of ["maxLength", "maxLengthEssence", "min", "max"]) {
      if (key in config) {
        config.rules.push(rules[key](config[key]));
      }
    }
  },

};




/**
 * Vérifie si un formulaire est valide selon sa définition et les règles associées.
 *
 * @function
 * @param {Object} context - Contexte d'exécution du formulaire.
 * @param {Object} context.$store - Instance du store (état global de l'application).
 * @param {Object} context.baseModel - Modèle de données du formulaire.
 * @param {Object} context.config - Configuration contenant les définitions de formulaire.
 * @param {string} keyForm - Clé identifiant le formulaire à valider.
 * @returns {boolean} Retourne true si le formulaire est valide ou si la condition du formulaire n'est pas remplie, sinon false.
 *
 * @description
 * Cette fonction récupère la définition du formulaire à partir de la configuration, évalue les champs requis,
 * applique les règles de validation, puis vérifie la condition associée au formulaire.
 * La validation est considérée comme réussie si toutes les règles sont respectées ou si la condition du formulaire n'est pas remplie.
 */
const isValidForm = function({ $store, baseModel, config }, keyForm) {
  const formDef = copy(config.formDefs[keyForm]);

  let condRules = true;

  formDef.required =
    typeof formDef.required === "function"
      ? formDef.required({ $store, baseModel })
      : formDef.required;

  formFunctions.rules.processRules(formDef);

  for (const rule of formDef.rules) {
    condRules = condRules && rule(baseModel[keyForm]) === true;
  }

  let condCondition =
    !formDef.condition ||
    formDef.condition({ baseModel, $store });

  return condRules || !condCondition;
}



const formFunctions = {
  processItems,
  change,
  rules,
  getEssencesSelected,
  processAreas,
  isValidForm,
  getDateFromMMJJ
  // processFormGroupConfig
};

export { formFunctions };
