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

var initTiles = (map, mapConfig) => {
  map.attributionControl.addAttribution('&copy; <a href=\'https://occitanie.cnpf.fr/\'>CRPF Occitanie</a>');

  const tileConfig = makeTileConfig(mapConfig);

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

  const tileKey = Object.keys(mapConfig.tileList).find(key => mapConfig.tileList[key].default) || mapConfig.tileList[0];
  map.tiles[tileConfig[tileKey].label].addTo(map);

  map.layerControl = L.control.layers(map.tiles).addTo(map);
};

export { initTiles };
