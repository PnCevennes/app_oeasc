/**
 *  Fonds de cartes
 */

var L = window.L;

const mapTile = {
  makeTileConfig: function() {
    this._config.tilesConfig = {};
    for (const key of Object.keys(this._config.tileList)) {
      this._config.tilesConfig[key] = this._config.baseTilesConfig[key];
      // replace IGN_KEY
      this._config.tilesConfig[key].url = this._config.tilesConfig[
        key
      ].url.replace('IGN_KEY', this._config.IGN_KEY);
    }
  },

  initTiles: function() {
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
        id: tileConfig.id
      });
      this._map.tiles[tileConfig.label] = tile;
    }

    // Set default tile

    const tileKey =
      Object.keys(this._config.tileList).find(
        key => this._config.tileList[key].default
      ) || this._config.tileList[0];

    this._map.tiles[this._config.tilesConfig[tileKey].label].addTo(this._map);
    this._map.layerControl = L.control.layers(this._map.tiles).addTo(this._map);
  }
};

export { mapTile };
