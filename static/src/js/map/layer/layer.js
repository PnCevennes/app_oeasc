import { apiRequest } from '../../data/api.js';
import { findLayers } from './util.js'

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

const zoomOnLayers = (map, layers) => {
  if (!(layers && layers.length)) {
    return
  }
  const layersGroup = L.featureGroup(layers);
  const bounds = layersGroup.getBounds();
  map.fitBounds(bounds);
}

const findAndZoomOnLayers = (map, type, fieldName = null, value = null) => {
  const layers = findLayers(map, type, fieldName, value);
  zoomOnLayers(map, layers);
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
    if(layerConfig.select) {
      makeLayerSelect(map, layerConfig, data)
    }
  });
};

const makeLayerSelect = (map, layerConfig, data) => {
  const select = document.getElementById(layerConfig.select.id);
  if (!select) {
    return;
  }
  select.innerHTML += `<option value='*'>Tout sectionner</option>`;
  for (const d of data.features) {
    select.innerHTML += `<option value='${d.properties[layerConfig.select.value]}'>${d.properties[layerConfig.select.label]}</option>`;
  }

  select.addEventListener('change', () => {
    const { value } = select;
    const { object, process, zoom } = layerConfig.select;

    // set filters
    map.config[object].filters = map.config[object].filters || {};
    if (value) {
      map.config.declarations.filters.secteur = value;
    } else {
      Reflect.deleteProperty(map.config.declarations.filters, 'secteur');
    }

    // process
    process(map)

    if (zoom) {
      findAndZoomOnLayers(map, layerConfig.type, layerConfig.select.value, value)
    }

  });

}

const initLayers = (map) => {
  for (const key of Object.keys(map.config.layers)) {
    const layerConfig = map.config.layers[key];
    addLayer(map, layerConfig);
  }
};

export { initLayers, findAndZoomOnLayers };
