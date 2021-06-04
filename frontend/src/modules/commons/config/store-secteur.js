export default {
  group: "commons",
  name: "secteur",
  label: "Secteur",
  serverSide: true,
  defs: {
    id_secteur: {
      label: "ID",
      hidden: true
    },
    nom_secteur: {
      label: "Nom",
      required: true
    },
    code_secteur: {
      label: "Code",
      required: true
    }
  }
};
