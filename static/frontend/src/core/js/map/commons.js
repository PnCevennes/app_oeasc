import 'leaflet/dist/leaflet.css';
import 'leaflet/dist/leaflet';
import * as L from 'leaflet';

import '@/core/css/leaflet.css';

import { findLayers, findLayer } from './layer/util.js';
import { initTiles } from './util/tile.js';
import { initLayers } from './layer/layer.js';
import { initLegend } from './layer/legend.js';
import { config } from '@/config/config.js';
import { loadDeclarations, processDeclarations } from './declaration/declaration.js';


var getBaseConfig = function(mapId) {

  const elem = document.getElementById(mapId);
  if (!elem) {
    return;
  }

  const baseConfigName = elem.getAttribute('config');

  if (! baseConfigName) {
    return;
  }

  return config.baseConfigMap[baseConfigName] || {};
}

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

var makeMap = (mapId, mapConfig=null, options={}) => {
  var map = null;

  var elem = document.getElementById(mapId)

  if(!elem) {
    console.log('no map element')
    return;
  }

  if (!mapConfig) {
    mapConfig = getBaseConfig(mapId);
  }

  mapConfig = {...mapConfig ,...options};

  makeConfigDefault(mapConfig);

  map = L.map(mapId).setView(mapConfig.INIT_VIEW, mapConfig.INIT_ZOOM);
  map.id = mapId;
  map.config = mapConfig;
  makePanes(map);
  initTiles(map);
  initLegend(map);
  initLayers(map);
  L.control.scale({imperial: false}).addTo(map);

  if (mapConfig.declarations) {
    loadDeclarations(map)
  }

  // add functions
  map.findLayers = function(layerType, fieldName = null, value = null) {
    return findLayers(map, layerType, fieldName, value)
  }

  map.findLayer = function(layerType, fieldName = null, value = null) {
    return findLayer(map, layerType, fieldName, value)
  }


  return map;
};

export { makeMap, processDeclarations };
