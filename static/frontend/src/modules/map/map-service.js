/**
 * class pour gérer les cartes de l'application oeasc
 */

import 'leaflet/dist/leaflet.css';
import 'leaflet/dist/leaflet';
import * as L from 'leaflet';

import './map.css'; // css

import { mapConfig, staticMapConfig } from './map-elements/map-config.js';
import { mapPane } from './map-elements/map-pane.js';
import { mapTile } from './map-elements/map-tile.js';
import { mapTooltip } from './map-elements/map-tooltip.js';
import { mapLayer } from './map-elements/map-layer.js';
import { mapLegend } from './map-elements/map-legend.js';

const mapModules = [
  mapConfig,
  mapPane,
  mapTile,
  mapTooltip,
  mapLayer,
  mapLegend
];

const staticMapModules = [
    staticMapConfig
]


class MapService {
  _id; // map id
  _config; // configuration
  _map = null; // map leaflet object

  constructor(id, config = null) {
    this._id = id;
    this._config = config;
  }
  
  map = function() {
    return this._map;
  };

  // initialisation de la carte
  init = function() {
    // process config
    if (!this.processConfig()) {
      console.log('pb avec la config');
      return;
    }

    // map
    this._map = L.map(this._id);

    // set view
    this._map.setView(this._config.INIT_VIEW, this._config.INIT_ZOOM);

    // init panes
    this.initPanes();

    // init tiles
    this.initTiles();
    
    // init layers
    this.initLayers();

    // init legends
    this.initLegends();

    // init succeed
    return true;
  };
}

// ajout des methodes à la classe mapConfig
for (const methods of mapModules) {
  Object.assign(MapService.prototype, methods)
}

// ajout des méthodes statiques
for (const methods of staticMapModules) {
  Object.assign(MapService, methods)
}

export { MapService };
