// import { copy } from "@/core/js/util/util";

export default {
  group: "in",
  name: "realisation",
  label: "Réalisation",
  serverSide: true,
  columns: [
    "id_realisation",
    "date_realisation",
    "circuit",
    "secteur",
    "serie",
    "tags_table",
    "observers_table",
    "cerfs",
    "chevreuils",
    "lievres",
    "renards"
  ],
  defs: {
    observers_table: {
      label: 'Observateurs',
    },
    id_realisation: {
      label: "ID",
      hidden: true
    },
    date_realisation: {
      type: "date",
      label: "Date",
      required: true
    },
    circuit: {
      label: "Circuit",
      storeName: "inCircuit",
      type: "list_form",
      list_type: "autocomplete",
      returnObject: true,
      dataReloadOnSearch: true,
      required: true,
      params: { actif: true }
    },
    secteur: {
      text: "Secteur",
      storeName: "commonsSecteur",
      displayFieldName: "code_secteur",
      type: "list_form",
      list_type: "select",
      returnObject: true
    },
    observers: {
      type: "list_form",
      list_type: "combobox",
      label: "Observateurs",
      maxLength: 4,
      multiple: true,
      storeName: "inObserver",
      returnObject: true,
      dataReloadOnSearch: true,
      display: d =>
        d && d.length ? d.map(dd => dd.nom_observer).join(", ") : ""
    },
    tags_table: {
      label: "Tags"
    },
    tags: {
      type: "list",
      label: "Tags",
      forms: ["id_realisation", "id_tag", "valid"],
    },
    id_tag: {
      label: "Tag",
      type: "list_form",
      list_type: "select",
      required: true,
      storeName: "inTag"
    },
    valid: {
      label: "Valide",
      type: "bool_switch"
    },
    tag: {
      type: "list_form",
      list_type: "select",
      label: "Tag",
      storeName: "inTag",
      returnObject: true
    },
    temperature: {
      label: "Température",
      type: "list_form",
      list_type: "select",
      items: ["Froid", "Frais", "Doux", "Chaud"]
    },
    temps: {
      label: "Temps",
      type: "list_form",
      list_type: "select",
      items: ["Sec", "Puie fine", "Brouillard", "Neige"]
    },
    vent: {
      label: "Vent",
      type: "list_form",
      list_type: "select",
      items: ["Nul", "Faible", "Moyen", "Fort"]
    },
    observations: {
      type: "list",
      label: "Comptage",
      forms: ["id_espece", "nb", "id_observation"],
      required: true
    },
    id_espece: {
      type: "list_form",
      list_type: "select",
      label: "Espece",
      storeName: "commonsEspece",
      required: true
    },
    nb: {
      type: "number",
      label: "Nombre d'individus",
      min: 0,
      required: true
    },
    groupes: {
      type: "number",
      label: "Nombre de groupes de cerfs",
      min: "0"
    },
    serie: {
      type: "number",
      label: "Série",
      min: "0",
      required: true
    },
    id_observation: {
      label: "ID observation",
      type: "text",
      hidden: true
    },
    cerfs: {
      text: "Cerfs",
      type: "number"
    },
    chevreuils: {
      text: "Chevreuils",
      type: "number"
    },
    lievres: {
      text: "Lièvres",
      type: "number"
    },
    renards: {
      text: "Renards",
      type: "number"
    }
  },
  form: {
    groups: [
      {
        title: "Informations",
        forms: ["date_realisation", "circuit", "serie", "observers"]
      },
      {
        title: "Validation",
        forms: ["tags"]
      },

      {
        title: "Météo",
        direction: "row",
        forms: ["temperature", "temps", "vent"]
      },
      {
        title: "Observations",
        forms: ["groupes", "observations"]
      }
    ],
    value: {
      tags: [{ id_tag: 1, valid: true }],
      observations: [
        { id_espece: 1, nb: 0 },
        { id_espece: 2, nb: 0 },
        { id_espece: 3, nb: 0 },
        { id_espece: 4, nb: 0 }
      ]
    }
    // action: {
    // preProcess: ({ baseModel }) => {
    //   const out = copy(baseModel);
    //   out.tags = baseModel.tags.map(t => ({
    //     id_observation: t.id_observation,
    //     id_tag: t.id_tag,
    //     valild: t.valid
    //   }));
    //   return out;
    // }
    // }
  }
};
