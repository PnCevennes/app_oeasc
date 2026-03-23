/**
 *  Fonds de cartes
 */

var L = window.L;

/**
 * Objet mapTile pour la gestion des tuiles cartographiques dans une application Vue.js.
 *
 * @property {Object} _config - Configuration interne contenant la liste des tuiles et leur configuration de base.
 * @property {Object} _map - Instance de la carte Leaflet utilisée pour afficher les tuiles.
 *
 */
const mapTile = {
  /**
   * @method makeTileConfig
   * Initialise la configuration des tuiles à partir de la liste des tuiles et de la configuration de base.
   * Copie chaque configuration de tuile de base dans l'objet tilesConfig selon la clé correspondante.
   */
  makeTileConfig: function () {
    this._config.tilesConfig = {};
    for (const key of Object.keys(this._config.tileList)) {
      this._config.tilesConfig[key] = this._config.baseTilesConfig[key];
    }
  },

  /**
   * @method initTiles
   * Initialise les tuiles sur la carte :
   *  - Ajoute l'attribution du CRPF Occitanie à la carte.
   *  - Prépare la configuration des tuiles via makeTileConfig().
   *  - Crée chaque couche de tuile Leaflet à partir de la configuration et les ajoute à la carte.
   *  - Définit la tuile par défaut et l'ajoute à la carte.
   *  - Ajoute le contrôle de sélection des couches à la carte.
   */
  initTiles: function () {
    this._map.attributionControl.addAttribution(
      "&copy; <a href='https://occitanie.cnpf.fr/'>CRPF Occitanie</a>"
    );

    this.makeTileConfig();

    this._map.tiles = {};

    for (const tileConfig of Object.values(this._config.tilesConfig)) {
      const tile = L.tileLayer(tileConfig.url, {
        maxZoom: 18,
        opacity: 0.7,
        pane: 'PANE_TILE',
        attribution: tileConfig.attribution,
        id: tileConfig.id,
      });
      this._map.tiles[tileConfig.label] = tile;
    }

    // Set default tile

    const tileKey =
      Object.keys(this._config.tileList).find((key) => this._config.tileList[key].default) ||
      this._config.tileList[0];

    this._map.tiles[this._config.tilesConfig[tileKey].label].addTo(this._map);
    this._map.layerControl = L.control.layers(this._map.tiles).addTo(this._map);
  },
};

export { mapTile };
