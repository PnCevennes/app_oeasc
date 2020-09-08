import configCircuitForm from "./form-circuit";
// import { sessionFunctions } from "@/components/form/functions/session.js";

export default {
  storeName: "inCircuit",
  dense: true,
  striped: true,
  small: true,
  configForm: configCircuitForm,
  headerDefs: {
    nom_circuit: {
      text: "Nom"
    },
    numero_circuit: {
      text: "Numéro"
    },
    ug: {
      text: "Secteur"
    },
    ug_tags: {
      text: 'Tags',
      display: d => (d && d.length ? d.join(", ") : "")
    },
    km: {
      text: "distance (km)"
    }
  },

  sortBy: ["date_realisation"],
  sortDesc: [true],
  label: 'circuit',
};
