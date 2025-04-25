export default {
  group: "commons",
  name: "espece",
  label: "Espèce",

  defs: {
    id_espece: {
      label: "Id",
      type: "number",
      hidden: true
    },
    nom_espece: {
      label: "Nom",
      type: "text",
      required: true,
    },
    code_espece: {
      label: "Code",
      type: "text",
      required: true
    }
  },


};
