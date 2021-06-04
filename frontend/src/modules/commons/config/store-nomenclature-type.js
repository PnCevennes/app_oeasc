export default {
    group: "commons",
    name: "nomenclatureType",
    label: "Nomenclature type",
    serverSide: true,
    defs: {
      id_type: {
        label: "Id",
        hidden: true,
        type: 'text',
      },
      mnemonique: {
        label: "Mnémonique",
        required: true,
        type: 'text',
      },
      label_fr: {
        label: "Label fr",
        required: true,
        type: 'text',
      },
      description_fr: {
        label: "Description",
        required: true,
        type: 'text',
      },
    },
    sortBy: ["cd_nomenclature"],
    idFieldName: 'id_type',
    displayFieldName: 'mnemonique',
  };
  