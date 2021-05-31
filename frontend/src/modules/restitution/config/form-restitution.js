import { copy } from "@/core/js/util/util";

const configChoix = {
  type: "list_form",
  list_type: "autocomplete",
  // returnObject: true
};

export default {
  groups: [
    {
      forms: ["display", "groupByKey"]
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
      forms: ["switch"]
    },
    {
      forms: ["typeGraph", "stacking"],
      direction: "row"
    },
    {
      forms: ["filterList"]
    }
  ],
  formDefs: {
    height: {
      type: "text",
      label: "hauteur"
    },
    display: {
      type: "list_form",
      list_type: "button",
      label: "Affichage",
      items: [
        { value: "table", text: "Tableau" },
        { value: "map", text: "Carte" },
        { value: "graph", text: "Graphique" }
      ]
    },
    typeGraph: {
      type: "list_form",
      list_type: "button",
      label: "Type de graphique",
      items: [
        { value: "pie", text: "Camenbert" },
        { value: "column", text: "Barre |" },
        { value: "bar", text: "Barre -" }
      ],
      condition: ({ baseModel }) => baseModel.display == "graph"
    },
    choix1: {
      ...configChoix,
      label: "Choix 1 (Couleur)", 
    },
    switch: {
      type: "button",
      icon: "mdi-swap-vertical-bold",
      tooltip: "Inverser choix1 et choix2",
      click: () => ({ baseModel }) => {
        const temp = { choix: baseModel.choix1, nbMax: baseModel.nbMax1 };
        baseModel.choix1 = baseModel.choix2;
        baseModel.nbMax1 = baseModel.nbMax2;
        baseModel.choix2 = temp.choix;
        baseModel.nbMax2 = temp.nbMax;
        baseModel = copy(baseModel);
      }
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
      list_type: "autocomplete",
      label: "Filtres",
      multiple: true
    },
    groupByKey: {
      type: "list_form",
      list_type: "select",
      label: "Type de donneés",
    }
  }
};
