export default {
  group: "chasse",
  name: "typeBracelet",
  label: "Type de bracelet",
  labels: "Types de bracelet",
  displayFieldName: "code_type_bracelet",
  defs: {
    id_type_bracelet: {
      label: "ID",
      type: "text",
      hidden: true,
    },
    espece: {
        label: 'Espèce',
        storeName: 'commonsEspece',
        type: 'list_form',
        list_type: 'select',
        returnObject: true,
    },
    code_type_bracelet: {
        label: 'Code',
        type: "text",
    },
    description_type_bracelet: {
        label: 'Description',
        type: "text",
    }
  }
};
