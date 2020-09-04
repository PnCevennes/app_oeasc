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
      url: "api/in/circuits/",
      valueFieldName: "id_circuit",
      textFieldName: "label",
      display: "autocomplete",
      required: true
    },
    observers: {
      type: "list_form",
      display: "combobox",
      label: "Observateurs",
      maxLength: 4,
      multiple: true,
      url: "api/in/observers/",
      valueFieldName: "observer",
      textFieldName: "observer"
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
      forms: ["espece", "nb", "id_observation"]
    },
    espece: {
      type: "list_form",
      display: "combobox",

      label: "Espece",
      items: ["Cerf", "Chevreuil", "Renard", "Lièvre"],
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
      min: '0',
    },
    serie: {
      type: "number",
      label: "Série",
      min: "0",
      required: true,
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
      title: "Météo",
      direction: "row",
      forms: ["temperature", "temps", "vent"]
    },
    {
      title: 'Observations',
      forms: ["groupes", "observations"]
    }
  ],
  
  title: ({ id }) =>
    id
      ? `Modificiation de la réalisation de sortie Indice Nocturne ${id}`
      : "Création d'une réalisation de sortie Indice Nocturne",
  switchDisplay: ({ id }) => !!id,
  displayValue: ({ id }) => !!id,
  displayLabel: true,
  storeName: 'inRealisation',
  idFieldName: 'id_realisation'
};
