const configChoix = {
  type: "list_form",
  display: "autocomplete",
  returnObject: true
};

export default {
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
  bTimeline: {
    type: "bool_switch",
    label: "Timeline",
    condition: ({ baseModel }) => baseModel.display == "graph"
  },
  color: {
    ...configChoix,
    label: "Couleur",
    condition: ({ baseModel }) => ["map", "table"].includes(baseModel.display)
  },
  icon: {
    ...configChoix,
    label: "Icône",
    condition: ({ baseModel }) => ["map", "table"].includes(baseModel.display)
  },
  choix1: {
    ...configChoix,
    label: "Choix 1",
    condition: ({ baseModel }) => ["graph"].includes(baseModel.display)
  },
  choix2: {
    ...configChoix,
    label: "Choix 2",
    condition: ({ baseModel }) => ["graph"].includes(baseModel.display)
  }
};
