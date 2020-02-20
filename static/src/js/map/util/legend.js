const layerLegend = (layerConfig) => {
    return `<div><i style="background-color: ${layerConfig.style.fillColor};background-opacity: ${layerConfig.style.fillOpacity};border: ${layerConfig.style.weight}px solid ${layerConfig.style.color};"></i>${layerConfig.legend}</div>`;
};

const initLegend = (map, mapConfig) => {
  const legend = L.control({ position: 'bottomright' });
  legend.onAdd = () => {
    var div = L.DomUtil.create('div', 'legend');

    for (const layerConfig of Object.values(mapConfig.layers)) {
      div.innerHTML += layerLegend(layerConfig);
    }

    return div;
  };
  legend.addTo(map);
};

export { initLegend };
