export default {
  group: "commons",
  name: "tag",
  label: "Tag",
  serverSide: true,
  defs: {
    id_tag: {
      label: "ID",
      type: "text",
      hidden: true
    },
    nom_tag: {
      label: "Nom",
      type: "text",
      required: true
    },
    code_tag: {
      label: "Code",
      type: "text",
      required: true
    }
  }
};
