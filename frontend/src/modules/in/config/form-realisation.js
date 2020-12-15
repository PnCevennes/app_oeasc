import { copy } from "@/core/js/util/util";

export default {
  formDefs: {
    date_realisation: {
      type: "date",
      label: "Date",
      required: true
    },
    id_circuit: {
      type: "list_form",
      label: "Circuit",
      storeName: "inCircuit",
      display: "autocomplete",
      required: true
    },
    observers: {
      type: "list_form",
      display: "combobox",
      label: "Observateurs",
      maxLength: 4,
      multiple: true,
      storeName: "inObserver",
      returnObject: true
    },
    tags: {
      type: "list",
      label: "Tags",
      forms: ["id_realisation", "id_tag", "valid"]
      // default: ({ baseModel }) => ({
      //   id_realisation: baseModel.id_realisation,
      //   id_tag: null
      // })
    },
    id_realisation: {
      label: "ID realisation",
      type: "text",
      hidden: true
    },
    id_tag: {
      label: "Tag",
      type:"list_form",
      display:"select",
      required: true,
      storeName: 'inTag'
    },
    valid: {
      label: "Valide",
      type: "bool_switch"
    },
    tag: {
      type: "list_form",
      display: "select",
      label: "Tag",
      storeName: "inTag",
      returnObject: true
    },
    temperature: {
      label: "Température",
      type: "list_form",
      display: "select",
      items: ["Froid", "Frais", "Doux", "Chaud"]
    },
    temps: {
      label: "Temps",
      type: "list_form",
      display: "select",
      items: ["Sec", "Puie fine", "Brouillard", "Neige"]
    },
    vent: {
      label: "Vent",
      type: "list_form",
      display: "select",
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
      display: "select",
      label: "Espece",
      storeName: "inEspece",
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
    }
  },
  groups: [
    {
      title: "Informations",
      forms: ["date_realisation", "id_circuit", "serie", "observers"]
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
  },
  action: {
    preProcess: ({baseModel}) => {
      const out = copy(baseModel)
      out.tags = baseModel.tags.map(t => ({
        id_observation: t.id_observation,
        id_tag: t.id_tag,
        valild: t.valid
      }));
      return out;
    },
  },
  title: ({ id }) =>
    id
      ? `Modificiation de la réalisation de sortie Indice Nocturne ${id}`
      : "Création d'une réalisation de sortie Indice Nocturne",
  switchDisplay: ({ id }) => !!id,
  displayValue: ({ id }) => !!id,
  displayLabel: true,
  storeName: "inRealisation"
};
