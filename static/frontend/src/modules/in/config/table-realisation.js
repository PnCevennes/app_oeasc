import configRealisationForm from "./form-realisation";
// import { sessionFunctions } from "@/components/form/functions/session.js";


export default {
  storeName: "inRealisation",
  dense: true,
  striped: true,
  small: true,
  configForm: configRealisationForm,
  headerDefs: {
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
      storeName: "inCircuit",
      displayFieldName: "ug",
      preProcess: d => d.id_circuit
    },
    serie: {
      text: "Série"
    },
    observers: {
      text: "Observateurs",
      display: d => (d && d.length) ? d.join(', ') : '',
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
        (d && (d.observations.find(o => o.espece == "Cerf") || {}).nb) || 0
    },
    chevreuil: {
      text: "Chevreuil",
      preProcess: d =>
        (d && (d.observations.find(o => o.espece == "Chevreuil") || {}).nb) || 0
    },
    lievre: {
      text: "Lièvre",
      preProcess: d =>
        (d && (d.observations.find(o => o.espece == "Lièvre") || {}).nb) || 0
    },
    renard: {
      text: "Renard",
      preProcess: d =>
        (d && (d.observations.find(o => o.espece == "Renard") || {}).nb) || 0
    }
  },

  sortBy: ["date_realisation"],
  sortDesc: [true],
  label: 'réalisation'
};
