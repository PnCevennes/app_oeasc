import configObserverForm from "./form-observer";

export default {
  storeName: "inObserver",
  dense: true,
  striped: true,
  small: true,
  configForm: configObserverForm,
  headerDefs: {
    id_observer: {
      text: "Id"
    },
    nom_observer: {
      text: "Nom"
    },
  },
  sortBy: ["nom_observer"],
  sortDesc: [true],
  label: 'nom_observer',
};
