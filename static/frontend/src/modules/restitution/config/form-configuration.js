const configChoix = {
  type: "list_form",
  display: "autocomplete",
  // returnObject: true
};

export default {
  groups: [
    {
      forms: ["display"]
    },
    {
      forms: ["height"]
    },
    {
      forms: ["choix1", "nbMax1"],
      direction: "row"
    },
    {
      forms: ["choix2", "nbMax2"],
      direction: "row"
    },
    {
      forms: ["typeGraph", "stacking"]
    },
    {
      forms: ["filterList"]
    }

  ],
  formDefs: {
    heigth: {
      type:"text",
      value: '400px',
    },
    display: {
      type: "list_form",
      display: "button",
      label: "Affichage",
      items: [
        { value: "table", text: "Tableau" },
        { value: "map", text: "Carte" },
        { value: "graph", text: "Graphique" }
      ]
    },
    typeGraph: {
      type: "list_form",
      display: "button",
      label: "Type de graphique",
      items: [
        { value: "pie", text: "Camenbert" },
        { value: "column", text: "Barre" }
      ],
      condition: ({ baseModel }) => baseModel.display == "graph"
    },
    choix1: {
      ...configChoix,
      label: "Choix 1 (Couleur)"
    },
    nbMax1: {
      type: "number",
      label: "Nb max 1"
    },
    choix2: {
      ...configChoix,
      label: "Choix 2 (Icône)"
    },
    nbMax2: {
      type: "number",
      label: "Nb max 2"
    },
    stacking: {
      type: "bool_switch",
      label: "Stacking",
      condition: ({ baseModel }) => baseModel.display == "graph"
    },
    filterList: {
      type: "list_form",
      display: "autocomplete",
      name: "filters",
      label: "Filtres",
      multiple: true
    },
  }
};
