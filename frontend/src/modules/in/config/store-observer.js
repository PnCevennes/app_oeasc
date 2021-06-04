export default {
  group: "in",
  name: "observer",
  label: "Observateur",
  serverSide: true,
  defs: {
    id_observer: {
      label: "ID",
      type: "text",
      hidden: true
    },
    nom_observer: {
      label: "Nom",
      type: "text",
      required: true
    }
  }
};
