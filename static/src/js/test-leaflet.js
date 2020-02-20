import { makeMap, processDeclarations } from './map/commons.js';
import '../css/test-leaflet.css';

var mapConfig = {
  layerList: {
    zc: {},
    aa: {},
    secteurs: {
      zoom: true,
      displayLabel: 'label'
    }
  },
  declarations: {

    /*
     * display: {
     *   fieldName: "peuplement_type_label",
     *   label: "Alerte selon le type de peuplement"
     * fieldName: 'peuplement_ess_1_label',
     * label: 'Alerte selon l\'essence objectif principale',
     * },
     */
    type: 'circleMarker',

    /*
     * type: 'point',
     * type: 'marker',
     */
    popup: {}
  }
};

var displays = [
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
  }
];

const map = makeMap('map', mapConfig);

const selectParam1 = document.getElementById('param1')
for (const display of displays) {
  selectParam1.innerHTML += `<option value="${display.fieldName}">${display.label}</option>`;
}

selectParam1.addEventListener('change', () => {
  const { value } = selectParam1;

  if (!value) {

    return;
  }
  mapConfig.declarations.display = displays.find(display => display.fieldName === value);
  processDeclarations(map, mapConfig, map.declarations);
});
