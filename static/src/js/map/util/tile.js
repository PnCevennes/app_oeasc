/**
 *  Fonds de cartes
 */

const makeTileConfig = mapConfig => {
  const tilesConfig = {};
  for (const key of Object.keys(mapConfig.tileList)) {
    tilesConfig[key] = mapConfig.baseTilesConfig[key];
    tilesConfig[key].url = tilesConfig[key].url.replace('IGN_KEY', mapConfig.IGN_KEY);
    // replace IGN_KEY
  }
  return tilesConfig
};

var initTiles = (map) => {
  map.attributionControl.addAttribution('&copy; <a href=\'https://occitanie.cnpf.fr/\'>CRPF Occitanie</a>');

  const tileConfig = makeTileConfig(map.config);

  map.tiles = {};

  for (const key of Object.keys(tileConfig)) {
    const config = tileConfig[key];
    const tile = L.tileLayer(config.url, {
      maxZoom: 18,
      opacity: 0.7,
      pane: 'PANE_0',
      attribution: config.attribution,
      id: config.id
    });
    map.tiles[config.label] = tile;
  }

  // Set default tile

  const tileKey = Object.keys(map.config.tileList).find(key => map.config.tileList[key].default) || map.config.tileList[0];
  map.tiles[tileConfig[tileKey].label].addTo(map);

  map.layerControl = L.control.layers(map.tiles).addTo(map);
};

export { initTiles };
