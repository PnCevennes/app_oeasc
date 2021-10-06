/**
 * Configuration du formulaire permettant de choisir les paramètre de restitution
 *   pour le tableau de bord
 *
 * TODO faire le ménage
 */

import { copy } from "@/core/js/util/util";

const configChoix = {
  type: "list_form",
  list_type: "autocomplete",
};

export default {
  groups: [
    {
      forms: ["dataType"]
    },
    {
      forms: ["typeGraph"]
    },
    {
      forms: ["width", "height"]
    },
    {
      forms: ["fieldName"],
    },
    {
      forms: ["fieldName2"],
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
    width: {
      type: "text",
      label: "largeur"
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
    dataType: {
      type: "list_form",
      list_type: "button",
      label: "Type de donnée",
      items: [
        { value: "chasse", text: "Chasse" },
      ],
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
    fieldName: {
      ...configChoix,
      label: "Choix 1",
    },
    switch: {
      type: "button",
      icon: "mdi-swap-vertical-bold",
      tooltip: "Inverser fieldName et choix2",
      click: () => ({ baseModel }) => {
        const temp = { choix: baseModel.fieldName, nbMax: baseModel.nbMax1 };
        baseModel.fieldName = baseModel.choix2;
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
    fieldName2: {
      ...configChoix,
      label: "Choix 2"
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
