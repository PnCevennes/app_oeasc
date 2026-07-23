/**
 * class pour gérer les cartes de l'application oeasc
 */

import { copy } from '@/core/js/util/util.js';
import 'leaflet/dist/leaflet.css';
import './map.css';
import 'leaflet/dist/leaflet';
import * as L from 'leaflet';
import 'leaflet-easyprint';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconRetina from 'leaflet/dist/images/marker-icon-2x.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
import { mapConfig, staticMapConfig } from './map-elements/map-config.js';
import { mapPane } from './map-elements/map-pane.js';
import { mapTile } from './map-elements/map-tile.js';
import { mapTooltip } from './map-elements/map-tooltip.js';
import { mapLayer } from './map-elements/map-layer.js';
import { mapLegend } from './map-elements/map-legend.js';
import { mapExport } from './map-elements/map-export.js';
import { mapMarker } from './map-elements/map-marker.js';

/**
 * @constant {L.Icon} DefaultIcon
 * @description
 * Icône par défaut utilisée pour les marqueurs sur la carte Leaflet.
 *
 * Propriétés :
 * - iconAnchor : [12, 41] — Position de l'ancre de l'icône (point de référence sur l'image).
 * - iconSize : [25, 41] — Taille de l'icône en pixels.
 * - popupAnchor : [1, -34] — Position de l'ancre du popup par rapport à l'icône.
 * - tooltipAnchor : [16, -28] — Position de l'ancre du tooltip par rapport à l'icône.
 * - iconUrl : URL de l'image de l'icône standard.
 * - iconRetinaUrl : URL de l'image de l'icône pour écrans Retina.
 * - shadowUrl : URL de l'image de l'ombre de l'icône.
 */
let DefaultIcon = L.icon({
  iconAnchor: [12, 41],
  iconSize: [25, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
  iconUrl: icon,
  iconRetinaUrl: iconRetina,
  shadowUrl: iconShadow,
});
L.Marker.prototype.options.icon = DefaultIcon;

/**
 * @constant {Array} mapModules
 * @description
 * Tableau contenant les différents modules utilisés pour la gestion de la carte dans l'application.
 * Chaque élément du tableau représente un module spécifique :
 * - mapConfig : Module de configuration de la carte.
 * - mapPane : Module de gestion des panneaux de la carte.
 * - mapTile : Module de gestion des tuiles de la carte.
 * - mapTooltip : Module d'affichage des infobulles sur la carte.
 * - mapLayer : Module de gestion des couches de la carte.
 * - mapLegend : Module d'affichage de la légende de la carte.
 * - mapExport : Module d'exportation de la carte.
 * - mapMarker : Module de gestion des marqueurs sur la carte.
 */
const mapModules = [
  mapConfig,
  mapPane,
  mapTile,
  mapTooltip,
  mapLayer,
  mapLegend,
  mapExport,
  mapMarker,
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

  map = function () {
    return this._map;
  };

  /**
   * Détruit la carte Leaflet et libère ses écouteurs internes (resize, etc.).
   * À appeler impérativement quand le composant qui possède la carte est démonté,
   * sinon Leaflet garde des références vivantes (tuiles, couches, listeners sur window/document)
   * qui s'accumulent au fil des navigations et finissent par saturer la mémoire du navigateur.
   */
  destroy = function () {
    if (this._map) {
      this._map.remove();
      this._map = null;
    }
  };

  upConfig() {
    this._config = copy(this._config);
  }

  /**
   * Initialise la carte Leaflet avec la configuration spécifiée.
   *
   * Étapes principales :
   * 1. Vérifie et traite la configuration de la carte.
   * 2. Crée l'objet carte Leaflet et définit les options de zoom.
   * 3. Centre la carte sur la vue initiale et le niveau de zoom défini dans la configuration.
   * 4. Ajoute le contrôle d'échelle à la carte.
   * 5. Initialise les panneaux (panes) pour la gestion des couches.
   * 6. Initialise les fonds de tuiles (tiles) de la carte.
   * 7. Initialise les couches supplémentaires (layers).
   * 8. Initialise les marqueurs sur la carte.
   * 9. Corrige la taille de la carte à différents intervalles pour éviter les bugs d'affichage liés aux animations ou aux requêtes asynchrones.
   *
   * @returns {boolean} true si l'initialisation a réussi, false sinon.
   */
  init = function () {
    // 1. Traite la configuration de la carte ; si elle est invalide, arrête l'initialisation.
    if (!this.processConfig()) {
      return;
    }

    // 2. Crée l'objet carte Leaflet avec des options de zoom personnalisées.
    this._map = L.map(this._id, {
      zoomSnap: 0.1, // Précision du zoom (fraction de niveau de zoom)
      zoomDelta: 0.5, // Incrément de zoom lors des actions utilisateur
    });

    // 3. Centre la carte sur la vue initiale et le niveau de zoom définis dans la configuration.
    this._map.setView(this._config.INIT_VIEW, this._config.INIT_ZOOM);

    // 4. Ajoute un contrôle d'échelle (barre d'échelle) à la carte.
    L.control.scale().addTo(this._map);

    // 5. Initialise les panneaux (panes) pour organiser les couches de la carte.
    this.initPanes();

    // 6. Initialise les fonds de tuiles (tiles) de la carte.
    this.initTiles();

    // 7. Initialise les couches supplémentaires (layers) sur la carte.
    this.initLayers();

    // 8. Initialise les marqueurs sur la carte.
    this.initMarkers();

    // 9. Corrige la taille de la carte à différents intervalles pour éviter les bugs d'affichage
    //    (utile lors d'animations ou de chargements asynchrones).
    for (const delay of [100, 1000, 2000, 5000, 10000]) {
      setTimeout(() => {
        this._map.invalidateSize();
      }, delay);
    }

    // Retourne true si l'initialisation s'est déroulée correctement.
    return true;
  };
}

// ajout des methodes des module Panes, Tiles, Layers, Markers à la classe mapConfig
for (const methods of mapModules) {
  Object.assign(MapService.prototype, methods);
}

// ajout des méthodes situés dans map-config.js à la classe MapService
for (const methods of staticMapModules) {
  Object.assign(MapService, methods);
}

export { MapService };
