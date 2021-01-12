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
    id_secteur: {
      text: "Secteur",
      displayFieldName: "nom_secteur",
      storeName: "inSecteur",
    },
    km: {
      text: "distance (km)"
    },
    actif: {
      text: "Actif"
    }
  },

  sortBy: ["date_realisation"],
  sortDesc: [true],
  label: 'circuit',
};
