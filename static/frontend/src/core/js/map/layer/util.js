const testCond = (test, value) => {
  // TODO regex??
  const bCond = test === value || test === '*';

  return bCond
}

const testLayer = (layer, layerType, fieldName = null, test = null) => {
    if (!layer.feature) {
        return false;
      }
      const condtype = layer.feature.properties.type === layerType || (layerType === '*');
      const condValue = !fieldName || testCond(test, layer.feature.properties[fieldName]);

      return condtype && condValue;
}

const findLayers = (map, layerType, fieldName = null, value = null) => {
    const layers = Object.values(map._layers).filter(layer => testLayer(layer, layerType, fieldName, value));
    return layers;
}

const findLayer = (map, layerType, fieldName = null, value = null) => {
    const layer = Object.values(map._layers).find(layer => testLayer(layer, layerType, fieldName, value));
    return layer;
}

const applyFilters = (filters, object) => {
  let bSelected = true;
  if (!filters) {
    return true;
  }

  for (const key of Object.keys(filters)) {
    bSelected = bSelected && testCond(filters[key], object[key]);
  }

  return bSelected;
};

export { findLayer, findLayers, applyFilters };
