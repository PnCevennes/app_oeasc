import { apiRequest } from '../../data/api.js';

const displayLabel = (feature, layer, fieldName) => {
  const label = feature.properties[fieldName];
  layer.bindTooltip(label, {
    pane: 'PANE_30',
    permanent: true,
    direction: 'center',
    opacity: 0.8,
    fillOpacity: 1,
    weight: 3,
    className: 'label-layer'
  });
};

const zoomOnLayer = (map, layer) => {
    map.fitBounds(layer.getBounds())
}

const addLayer = (map, layerConfig) => {
  apiRequest(layerConfig.url).then(data => {
    const layer = L.geoJSON(data, {
      style: layerConfig.style,
      pane: layerConfig.pane,
      onEachFeature: (feature, layer) => {
        if (layerConfig.displayLabel) {
          displayLabel(feature, layer, layerConfig.displayLabel);
        }
      }
    }).addTo(map);
    if(layerConfig.zoom) {
        zoomOnLayer(map, layer);
    }
  });
};

const initLayers = (map, mapConfig) => {
  for (const key of Object.keys(mapConfig.layers)) {
    const layerConfig = mapConfig.layers[key];
    addLayer(map, layerConfig);
  }
};

export { initLayers };
