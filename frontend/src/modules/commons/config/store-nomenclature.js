export default {
    group: "commons",
    name: "nomenclature",
    label: "Nomenclature",
    defs: {
      id_nomenclature: {
        label: "Id",
        hidden: true
      },
      id_type: {
        label: "Type",
        required: true,
        storeName: 'commonsNomenclatureType'
      },
      cd_nomenclature: {
        label: "Code",
        required: true
      },
      label_fr: {
        label: "Label fr",
        required: true
      },
      mnemonique: {
        label: "Mnemonique",
        required: true
      },
      description_fr: {
        label: "Description",
        required: true
      },
    },
    displayFieldName: 'label_fr',
    sortBy: ['type', 'cd_nomenclature']
  };
  