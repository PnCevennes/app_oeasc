export default {
  formDefs: {
    id_observer: {
      label: 'Id',
      type: "text",
      hidden: true
    },
    nom_observer: {
      label: "Nom",
      type: "text",
      required: true,
    },
  },

  title: ({ id }) =>
    id ? `Modificiation du observateur ${id}` : "Création d'un observateur",
  switchDisplay: ({ id }) => !!id,
  displayValue: ({ id }) => !!id,
  displayLabel: true,
  storeName: "inObserver",
};
