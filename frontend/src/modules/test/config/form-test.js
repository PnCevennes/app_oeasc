export default {
  formDefs: {
    test_bool: {
      label: "bool",
      type: "bool_switch"
    },
    test_select_multi: {
      label: "Test select",
      type: "list_form",
      list_type: "select",
      items: ["a", "b", "c"],
      multiple: true
    },
    test_radio: {
        label: "Test radio",
        type: "list_form",
        items: ["a", "b", "c"],
      },
    test_multi: {
      label: "Test select",
      type: "list_form",
      items: ["a", "b", "c"],
      multiple: true
    },
    nomenclatures_peuplement_origine2: {
      label:
        "Origine des arbres / plants / semis touchés par les dégâts de grand gibier",
      type: "nomenclature",
      list_type: "radio",
      nomenclatureType: "OEASC_PEUPLEMENT_ORIGINE2",
      multiple: true,
      required: true
    },
    s_commune_proprietaire: {
      type: "list_form",
      list_type: "combobox",
      label: "Commune",
      dataReloadOnSearch: true,
      placeholder:
        "Entrez les premières lettres de la commune et/ou le code postal",
      url: ({ search }) => `api/commons/communes/${search}`,
      valueFieldName: "nom_cp",
      displayFieldName: "nom_cp",
      required: ({ baseModel }) => !baseModel.b_document,
    },
    b_document: {
      type: "file",
      label: 'Document'
    }
  },
  forms: ['b_document', 's_commune_proprietaire'],
  value: {s_commune_proprietaire: 'Azay-le-Rideau 37190'},
  // groups: [
  //     {
  //     forms: ["test_bool"]
  //     },
  //   {
  //     direction: "row",
  //     forms: ["test_select_multi", "test_multi", "test_radio"]
  //   },
  //   {
  //       forms: ['nomenclatures_peuplement_origine2']
  //   }
  // ],
  // value: {
  //   test_select_multi: [],
  //   test_multi: [], 
  // }
  //   forms: ["nomenclatures_peuplement_origine2"],
};
