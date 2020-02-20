import 'leaflet/dist/leaflet.css';
import 'leaflet/dist/leaflet';
import 'leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.webpack.css'; // Re-uses images from ~leaflet package
import * as L from 'leaflet';
import 'leaflet-defaulticon-compatibility';
import 'leaflet.awesome-markers'

// import '@fortawesome/fontawesome-free/js/fontawesome'
// import '@fortawesome/fontawesome-free/js/solid'
// import '@fortawesome/fontawesome-free/js/regular'
// import '@fortawesome/fontawesome-free/js/brands'
 

import { initTiles } from './util/tile.js';
import { initLayers } from './util/layer.js';
import { initLegend } from './util/legend.js';
import { config } from '../config/config.js';
import { loadDeclarations, processDeclarations } from './declaration/declaration.js';


var makeConfigDefault = (mapConfig) => {
  for (const key of Object.keys(config.map)) {
    mapConfig[key] = mapConfig[key] || config.map[key];
  }
  // Layers depuis mapConfig.layerList
  mapConfig.layers = {};
  if (mapConfig.layerList) {
    for (const key of Object.keys(mapConfig.layerList)) {
      mapConfig.layers[key] = {
        ...config.map.layers[key],
        ...mapConfig.layerList[key]
      };
    }
  }
};

var makePanes = map => {
  for (let i = 0; i <= 100; i++) {
    const paneName = `PANE_${i}`;
    map.createPane(paneName);
    map.getPane(paneName).style.zIndex = 600 + i;
  }
};

var makeMap = (mapId, mapConfig) => {
  var map = null;

  makeConfigDefault(mapConfig);
  map = L.map(mapId).setView(mapConfig.INIT_VIEW, mapConfig.INIT_ZOOM);
  map.id = mapId;
  makePanes(map, mapConfig);
  initTiles(map, mapConfig);
  initLegend(map, mapConfig);
  initLayers(map, mapConfig);
  var scale = L.control.scale({imperial: false}).addTo(map); 

  if (mapConfig.declarations) {
    loadDeclarations(map, mapConfig)
  }

  return map;
};

export { makeMap, processDeclarations };
