import "./map-legend.css";
import * as chroma from "chroma-js";

var L = window.L;

const mapLegend = {
  // renvoie la ligne de la légende pour un layer
  layerLegend(layerConfig) {
    const fillColor = chroma(layerConfig.style.fillColor || "black").alpha(
      layerConfig.style.fillOpacity
    );
    const legend = `
        <div class="${layerConfig.key}">
          <i style="
            background-color: ${fillColor};
            border: ${layerConfig.style.weight}px solid ${layerConfig.style.color};
          "></i>
          <span class="legendText">
          ${layerConfig.legend}
          </span>
        </div>
        `;
    return legend;
    // return `<div><i style="background-color: ${layerConfig.style.fillColor};background-opacity: ${layerConfig.style.fillOpacity};border: ${layerConfig.style.weight}px solid ${layerConfig.style.color};"></i>${layerConfig.legend}</div>`;
  },

  markerLegend(markerConfig) {
    const color = markerConfig.icon || "#4999D1";
    const icon = markerConfig.icon || 'map-marker';
    const legend = `
        <div>
        <i 
        class='mdi mdi-${icon}'
        style="
            font-size: 2em;
            color:${color}
          "
          ></i>
          <span class="legendText">
          ${markerConfig.legend}
          </span>
        </div>
        `;
    return legend;
  },

  setLayerLegendText(key, text) {
    const elements = document
      .getElementById(this._id)
      .getElementsByClassName(key);
    if (elements.length) {
      elements[0].getElementsByClassName("legendText")[0].innerHTML = text;
    }
  },

  // initialise les légendes
  initLegends: function() {
    const legend = L.control({ position: "bottomright" });

    legend.onAdd = () => {
      var div = L.DomUtil.create("div", "legend-container");
      var divLegend = L.DomUtil.create("div", "legend");

      // legendes des layers
      for (const layerConfig of Object.values(this._config.layers || {})) {
        divLegend.innerHTML += this.layerLegend(layerConfig);
      }

      // legendes des markers
      for (const markerConfig of Object.values(this._config.markers || {})) {
        divLegend.innerHTML += this.markerLegend(markerConfig);
      }


      div.appendChild(divLegend);

      return div;
    };
    legend.addTo(this._map);
  },

  addLayerLegend: function(layerConfig) {
    const elemLegend = document
      .getElementById(this._id)
      .getElementsByClassName("legend")[0];
    elemLegend.innerHTML += this.layerLegend(layerConfig);
  }
};

export { mapLegend };
