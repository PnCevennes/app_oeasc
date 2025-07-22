export default {
  formDefs: {
    filename: {
      label: "nom du fichier",
      type: "text",
      rules: [
        u =>
          [".jpg", ".png"].some(v => u.toLowerCase().endsWith(v)) ||
          'Le nom du fichier doit se terminer par ".png" ou ".jpg"'
      ],
      required: true,
    },
    height: {
      label: "Hauteur",
      type: "number"
    },
    width: {
      label: "Largeur",
      type: "number"
    }
  },
  title: "Exporter la carte au format png",
};
