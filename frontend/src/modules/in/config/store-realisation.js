import { copy } from "@/core/js/util/util";

export default {
  group: "in",
  name: "realisation",
  label: "Réalisation",
  columns: [
    "id_realisation",
    "date_realisation",
    "id_circuit",
    "secteur",
    "serie",
    "tags",
    "cerf",
    "chevreuil",
    "lievre",
    "renard"
  ],
  defs: {
    id_realisation: {
      label: "ID",
      hidden: true
    },
    date_realisation: {
      type: "date",
      label: "Date",
      required: true
    },
    id_circuit: {
      type: "list_form",
      label: "Circuit",
      storeName: "inCircuit",
      list_type: "autocomplete",
      required: true,
      filters: { actif: [true] }
    },
    secteur: {
      text: "Secteur",
      storeName: "commonsSecteur",
      displayFieldName: "code_secteur",
      preProcess: d => d.circuit.id_secteur
    },
    observers: {
      type: "list_form",
      list_type: "combobox",
      label: "Observateurs",
      maxLength: 4,
      multiple: true,
      storeName: "inObserver",
      returnObject: true,
      display: d =>
        d && d.length ? d.map(dd => dd.nom_observer).join(", ") : ""
    },
    tags: {
      type: "list",
      label: "Tags",
      forms: ["id_realisation", "id_tag", "valid"],
      display: d => {
        return d && d.length
          ? d.map(dd => `${dd.tag.nom_tag}: ${dd.valid ? "o" : "x"}`).join(", ")
          : "";
      }
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
    cerf: {
      text: "Cerf",
      preProcess: d =>
        (d &&
          (d.observations.find(o => o.espece.nom_espece == "Cerf") || {}).nb) ||
        0
    },
    chevreuil: {
      text: "Chevreuil",
      preProcess: d =>
        (d &&
          (d.observations.find(o => o.espece.nom_espece == "Chevreuil") || {})
            .nb) ||
        0
    },
    lievre: {
      text: "Lièvre",
      preProcess: d =>
        (d &&
          (d.observations.find(o => o.espece.nom_espece == "Lièvre") || {})
            .nb) ||
        0
    },
    renard: {
      text: "Renard",
      preProcess: d =>
        (d &&
          (d.observations.find(o => o.espece.nom_espece == "Renard") || {})
            .nb) ||
        0
    }
  },
  form: {
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
      preProcess: ({ baseModel }) => {
        const out = copy(baseModel);
        out.tags = baseModel.tags.map(t => ({
          id_observation: t.id_observation,
          id_tag: t.id_tag,
          valild: t.valid
        }));
        return out;
      }
    }
  }
};
