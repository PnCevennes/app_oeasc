export default {
  group: "chasse",
  name: "typeBracelet",
  label: "Type de bracelet",
  labels: "Types de bracelet",
  defs: {
    id_type_bracelet: {
      label: "ID",
      hidden: true,
    },
    id_espece: {
        label: 'Espèce',
        storeName: 'commonsEspece'
    },
    code_type_bracelet: {
        label: 'Code'
    },
    description_type_bracelet: {
        label: 'Description'
    }
  }
};
