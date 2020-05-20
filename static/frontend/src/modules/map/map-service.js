/**
 * class pour gérer les cartes de l'application oeasc
 */

import { copy } from "@/core/js/util/util";

import "leaflet/dist/leaflet.css";
import "./map.css";
import "leaflet/dist/leaflet";
import * as L from "leaflet";
// const L = window.L

import icon from "leaflet/dist/images/marker-icon.png";
import iconRetina from "leaflet/dist/images/marker-icon-2x.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";

let DefaultIcon = L.icon({
  iconAnchor: [12, 41],
  iconSize: [25, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
  iconUrl: icon,
  iconRetinaUrl: iconRetina,
  shadowUrl: iconShadow
});

L.Marker.prototype.options.icon = DefaultIcon;
// L.Marker.prototype.options.icon.shadowUrl = iconShadow;

import { mapConfig, staticMapConfig } from "./map-elements/map-config.js";
import { mapPane } from "./map-elements/map-pane.js";
import { mapTile } from "./map-elements/map-tile.js";
import { mapTooltip } from "./map-elements/map-tooltip.js";
import { mapLayer } from "./map-elements/map-layer.js";
import { mapLegend } from "./map-elements/map-legend.js";
import { mapExport } from "./map-elements/map-export.js";
import { mapMarker } from "./map-elements/map-marker.js";

const mapModules = [
  mapConfig,
  mapPane,
  mapTile,
  mapTooltip,
  mapLayer,
  mapLegend,
  mapExport,
  mapMarker
];

const staticMapModules = [staticMapConfig];

class MapService {
  _id; // map id
  _config; // configuration
  _map = null; // map leaflet object

  baseModel = {};

  constructor(id, config = null) {
    this._id = id;
    this._config = config;
  }

  map = function() {
    return this._map;
  };

  upConfig() {
    this._config = copy(this._config);
  }

  // initialisation de la carte
  init = function() {
    // process config
    if (!this.processConfig()) {
      console.log("pb avec la config");
      return;
    }

    // map
    this._map = L.map(this._id, {
      zoomSnap: 0.1,
      zoomDelta: 0.5
    });

    // set view
    this._map.setView(this._config.INIT_VIEW, this._config.INIT_ZOOM);

    this._map.on("zoomend", () => {
      console.log(this._map.getZoom());
    });
    // scale
    L.control.scale().addTo(this._map);

    // init panes
    this.initPanes();

    // init tiles
    this.initTiles();

    // init layers
    this.initLayers();

    // init legends
    // this.initLegends();

    // init marker
    this.initMarkers();

    // init succeed

    // resize map in case oft                       bv
    for (const t of [100, 1000, 2000, 5000, 10000]) {
      setTimeout(() => {
        this._map.invalidateSize();
      }, t);
    }

    return true;
  };
}

// ajout des methodes à la classe mapConfig
for (const methods of mapModules) {
  Object.assign(MapService.prototype, methods);
}

// ajout des méthodes statiques
for (const methods of staticMapModules) {
  Object.assign(MapService, methods);
}

export { MapService };
