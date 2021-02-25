export default {
    group: "commons",
    name: "nomenclatureType",
    label: "Nomenclature type",
    defs: {
      id_type: {
        label: "Id",
        hidden: true
      },
      mnemonique: {
        label: "Mnémonique",
        required: true
      },
      label_fr: {
        label: "Label fr",
        required: true
      },
      description_fr: {
        label: "Description",
        required: true
      },
    },
    sortBy: ["cd_nomenclature"],
    idFieldName: 'id_type',
    displayFieldName: 'mnemonique',
  };
  