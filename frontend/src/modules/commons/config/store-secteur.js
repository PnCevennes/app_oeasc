export default {
  group: "commons",
  name: "secteur",
  label: "Secteur",
  serverSide: true,


  
  defs: {
    id_secteur: {
      label: "ID",
      type: "number",
      hidden: true
    },
    nom_secteur: {
      label: "Nom",
      type: "text",
      required: true
    },
    code_secteur: {
      label: "Code",
      type: "text",
      required: true
    }
  }
};
