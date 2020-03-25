var L = window.L;

const layerLegend = (layerConfig) => {
    console.log(layerConfig)
    return `<div><i style="background-color: ${layerConfig.style.fillColor};background-opacity: ${layerConfig.style.fillOpacity};border: ${layerConfig.style.weight}px solid ${layerConfig.style.color};"></i>${layerConfig.legend}</div>`;
};

const initLegend = (map) => {
  console.log('legend')
  const legend = L.control({ position: 'bottomright' });
  legend.onAdd = () => {
    var div = L.DomUtil.create('div', 'legend-container');
    var divLegend = L.DomUtil.create('div', 'legend');

    for (const layerConfig of Object.values(map.config.layers)) {
      divLegend.innerHTML += layerLegend(layerConfig);
    }

    div.appendChild(divLegend)

    return div;
  };
  legend.addTo(map);
};

export { initLegend };
