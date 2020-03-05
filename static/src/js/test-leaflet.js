import { makeMap, processDeclarations } from './map/commons.js';
import * as chroma from 'chroma-js';
import '../css/test-leaflet.css';

var mapConfig = {
  layerList: {
    zc: {},
    aa: {},
    secteurs: {
      zoom: true,
      displayLabel: 'label',
      select: {
        object: 'declarations',
        id: 'secteur',
        value: 'label',
        label: 'label',
        process: processDeclarations,
        zoom: true,
        type: 'OEASC_SECTEUR'
      }
    }
  },
  declarations: {
    color: {
      fieldName: 'peuplement_type_label',
    label: 'Alerte selon le type de peuplement',
        // fieldName: 'degats->degat_type',
        // label: 'Alerte selon le type de dégât',
      // fieldName: 'peuplement_paturage_type_label',
      // label: 'Alerte selon le type de pâturage',
      list: chroma.brewer.Dark2
    },
    icon: {
      fieldName: 'peuplement_type_label',
    label: 'Alerte selon le type de peuplement',
      // fieldName: 'peuplement_type_label',
      // label: 'Alerte selon le type de peuplement',
      list: [
        'far fa-circle',
        'far fa-square',
        'far fa-star',
        'fas fa-adjust',
        'fas fa-circle',
        'fas fa-square'
      ]
    },
    // type: 'circleMarker',
    type: 'icon',
    // type: 'marker',
    popup: {}
  }
};

var simple = [
  {
    fieldName: 'peuplement_type_label',
    label: 'Alerte selon le type de peuplement'
  },
  {
    fieldName: 'peuplement_ess_1_label',
    label: 'Alerte selon l\'essence objectif principale'
  },
  {
    fieldName: 'peuplement_origine_label',
    label: 'Alerte selon l\'origine du peuplement'
  },
  {
    fieldName: 'type_foret',
    label: 'Alerte selon le type de forêt'
  },
  {
    fieldName: 'organisme',
    label: 'Alerte selon l\'organisme'
  },
  {
    fieldName: 'peuplement_acces_label',
    label: 'Alerte selon l\'acces au peuplement'
  }
];

var multi = [
  {
    fieldName: 'peuplement_ess_2_label',
    label: 'Alerte selon l\'essence objectif secondaire'
  },
  {
    fieldName: 'peuplement_ess_3_label',
    label: 'Alerte selon l\'essence complémentaire'
  },
  {
    fieldName: 'peuplement_paturage_type_label',
    label: 'Alerte selon le type de pâturage'
  },
  {
    fieldName: 'peuplement_paturage_saison_label',
    label: 'Alerte selon la saison de pâturage'
  },
  {
    fieldName: 'peuplement_paturage_type_label',
    label: 'Alerte selon le type de pâturage'
  },
  {
    fieldName: 'peuplement_maturite_label',
    label: 'Alerte selon la maturité du peuplement'
  },
  {
    fieldName: 'espece_label',
    label: 'Alerte selon l\'espèce avérée'
  },
  {
    fieldName: 'degat_types_label',
    label: 'Alerte selon le type de dégât'
  },
  {
    fieldName: 'peuplement_protection_type_label',
    label: 'Alerte selon le type de protection'
  },
]

var displays = {
  simple,
  multi
}
console.log('aa')
const map = makeMap('map', mapConfig);

const initSelectOfType = (id, type) => {
  const select = document.getElementById(id);

  const keys = Object.keys(displays);

  let displaysList = [];

  for (const displayType of keys) {
    displaysList = displaysList.concat(displays[displayType]);
    for (const display of displays[displayType].sort(d => d.fieldName)) {
      select.innerHTML += `<option value="${display.fieldName}">${display.label}</option>`;
    }
    if (displayType !== keys[keys.length - 1]) {
      select.innerHTML += '<option disabled>──────────</option>';
    }
  }


  select.addEventListener('change', () => {
    const { value } = select;
    // if (!value) {
      // return;
    // }
    const display = displaysList.find(display => display.fieldName === value);
    mapConfig.declarations[type].fieldName = display && display.fieldName;
    mapConfig.declarations[type].label = display && display.label;
    processDeclarations(map, mapConfig, map.declarations);
  })
}

initSelectOfType('select-color', 'color');
initSelectOfType('select-icon', 'icon');
