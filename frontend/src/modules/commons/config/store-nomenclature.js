export default {
    group: "commons",
    name: "nomenclature",
    label: "Nomenclature",
    serverSide: true,
    defs: {
      id_nomenclature: {
        label: "Id",
        hidden: true,
        type: 'text',
      },
     type: {
        label: "Type",
        type: 'text',
        required: true,
      },
      cd_nomenclature: {
        label: "Code",
        type: 'text',
        required: true
      },
      label_fr: {
        label: "Label fr",
        type: 'text',
        required: true
      },
      mnemonique: {
        label: "Mnemonique",
        type: 'text',
        required: true
      },
      description_fr: {
        label: "Description",
        type: 'text',
        required: true
      },
    },
    displayFieldName: 'label_fr',
    sortBy: ['type', 'cd_nomenclature']
  };
  