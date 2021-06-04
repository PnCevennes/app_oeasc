export default {
    group: "chasse",
    name: "personne",
    label: "Personne",
    serverSide: "true",
    defs: {
      id_personne: {
        label: "ID",
        type:'text',
        hidden: true
      },
      nom_personne: {
        label: "Nom",
        type:'text',
        required: true
      }
    }
  };
  