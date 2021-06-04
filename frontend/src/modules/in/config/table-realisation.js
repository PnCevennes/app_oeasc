import configRealisationForm from "./form-realisation";
// import { sessionFunctions } from "@/components/form/functions/session.js";


export default {
  storeName: "inRealisation",
  dense: true,
  striped: true,
  small: true,
  configForm: configRealisationForm,
  headerDefs: {
    id_realisation: {
      type: "number",
      text: "ID"
    },

    date_realisation: {
      type: "date",
      text: "Date"
    },
    id_circuit: {
      text: "Circuit",
      storeName: "inCircuit",
      displayFieldName: "nom_circuit"
    },
    secteur: {
      text: "Secteur",
      storeName: "commonsSecteur",
      displayFieldName: "code_secteur",
      preProcess: d => d.circuit.id_secteur
    },
    serie: {
      text: "Série"
    },
    tags: {
      text: "Tags",
      display: d => {
        return (d && d.length) ? d.map(dd => `${dd.tag.nom_tag}: ${dd.valid ? 'o' : 'x'}`  ).join(', ') : '';
      }
    },
    observers: {
      text: "Observateurs",
      display: d => (d && d.length) ? d.map(dd => dd.nom_observer).join(', ') : '',
    },
    temperature: {
      text: "Température"
    },
    temps: {
      text: "Temps"
    },
    vent: {
      text: "Vent"
    },
    groupes: {
      text: "Nombre de groupe de cerf"
    },
    cerf: {
      text: "Cerf",
      preProcess: d =>
        (d && (d.observations.find(o => o.espece.nom_espece == "Cerf") || {}).nb) || 0
    },
    chevreuil: {
      text: "Chevreuil",
      preProcess: d =>
        (d && (d.observations.find(o => o.espece.nom_espece == "Chevreuil") || {}).nb) || 0
    },
    lievre: {
      text: "Lièvre",
      preProcess: d =>
        (d && (d.observations.find(o => o.espece.nom_espece == "Lièvre") || {}).nb) || 0
    },
    renard: {
      text: "Renard",
      preProcess: d =>
        (d && (d.observations.find(o => o.espece.nom_espece == "Renard") || {}).nb) || 0
    }
  },

  sortBy: ["id_realisation"],
  sortDesc: [false],
  label: 'réalisation'
};
