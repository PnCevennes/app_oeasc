export default {
  formDefs: {
    test_bool: {
      label: "bool",
      type: "bool_switch"
    },
    test_select_multi: {
      label: "Test select",
      type: "list_form",
      display: "select",
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
      display: "radio",
      nomenclatureType: "OEASC_PEUPLEMENT_ORIGINE2",
      multiple: true,
      required: true
    }
  },
  groups: [
      {
      forms: ["test_bool"]
      },
    {
      direction: "row",
      forms: ["test_select_multi", "test_multi", "test_radio"]
    },
    {
        forms: ['nomenclatures_peuplement_origine2']
    }
  ],
  // value: {
  //   test_select_multi: [],
  //   test_multi: [], 
  // }
  //   forms: ["nomenclatures_peuplement_origine2"],
};
