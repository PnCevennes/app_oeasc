import { makeMap } from './map/commons.js';
import '../css/test-leaflet.css';
import '../css/content.scss';

var mapConfig = {
  layerList: {
    zc: {},
    aa: {},
    secteurs: {
      zoom: true,
      displayLabel: 'label',
    }
  },
};

makeMap('map', mapConfig);
