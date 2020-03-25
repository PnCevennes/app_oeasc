const required=true;

export default {
  test_map: {
    title: 'Test select map',
    forms: {
      foret_onf: {
        type: 'select_map',
        legend: 'Forêt relevant du régime forestier',
        url: 'api/ref_geo/areas_simples_from_type_code/l/OEASC_ONF_FRT',
        dataFieldNames: {
          value: 'id_area',
          text: 'label'
        }
      }
    }
  },
  test_bool: {
    title: 'Test booléen',
    forms: {
      choix1: {
        label: 'Test choix 1',
        type: 'bool_radio',
        labels: {
          true: 'Public',
          false: 'Privée'
        }
      },
      choix2: {
        label: 'Test choix 2',
        type: 'bool_switch'
      }
    }
  },
  test_input: {
    title: 'Test Input',
    forms: {
      number1: {
        label: 'Input number 1',
        type: 'number',
        rules: [
          v => !!v || 'Number is required',
          v => typeof v !== 'number' || 'Entry must be a number',
          v => v >= 0 || 'Number must be >= 0'
        ]
      },
      text1: {
        label: 'Input text 1',
        type: 'text',
        rules: [
          v => !!v || 'Name is required',
          v => (!v ||(v &&v.length <= 10)) || 'Name must be less than 10 characters',
        ],
        required,
      },
      text_area1: {
        label: 'Input text_area 1',
        type: 'text_area'
      }
    }
  },
  test_nomenclature: {
    title: 'Test nomenclature',
    forms: {
      nomenclature_select: {
        label: 'Select nomenclature',
        type: 'nomenclature',
        display: 'select',
        nomenclatureType: 'OEASC_PEUPLEMENT_ACCES'
      },
      nomenclature_select_multi: {
        label: 'Select nomenclature (multi)',
        type: 'nomenclature',
        display: 'select',
        multiple: true,
        nomenclatureType: 'OEASC_PEUPLEMENT_ACCES'
      },
      nomenclature_radio: {
        label: 'Radio nomenclature',
        type: 'nomenclature',
        display: 'radio',
        nomenclatureType: 'OEASC_PEUPLEMENT_ACCES'
      },
      nomenclature_radio_multi: {
        label: 'Radio nomenclature (multi)',
        type: 'nomenclature',
        display: 'radio',
        multiple: true,
        nomenclatureType: 'OEASC_PEUPLEMENT_ACCES'
      }
    }
  }
};
