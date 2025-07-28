import "./map-legend.css";
// import * as chroma from "chroma-js";
import chroma from "chroma-js";

var L = window.L;

const mapLegend = {
  
  // Renvoie la ligne de la légende pour un layer (couche cartographique)
  // Prend en paramètre la configuration du layer et retourne le HTML de la légende
  layerLegend(layerConfig) {
    // Utilise chroma-js pour gérer la couleur de remplissage avec l'opacité
    const fillColor = chroma(layerConfig.style.fillColor || "black").alpha(
      layerConfig.style.fillOpacity
    );
    // Génère le HTML de la légende pour le layer
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
    // Ancienne version en commentaire : utilisait directement les propriétés sans chroma-js
  },

  // Renvoie la ligne de la légende pour un marker (marqueur sur la carte)
  // Prend en paramètre la configuration du marker et retourne le HTML de la légende
  markerLegend(markerLegend) {
    // Génère le HTML de la légende pour le marker avec l'icône et la couleur
    const legend = `
        <div class='marker-legend'>
        <i 
        class='mdi mdi-${markerLegend.icon}'
        style="
            font-size: 1.8em;
            color:${markerLegend.color}
          "
          ></i>
          <span class="legendText">
          ${markerLegend.text}
          </span>
        </div>
        `;
    return legend;
  },

  // Initialise les légendes sur la carte Leaflet
  // Crée le contrôle de légende et ajoute les éléments de légende pour les markers et les layers
  initLegends: function() {
    // Création du contrôle Leaflet pour la légende, positionné en bas à droite
    const legend = L.control({ position: "bottomright" });

    // Fonction appelée lors de l'ajout du contrôle à la carte
    legend.onAdd = () => {
      // Création des éléments HTML pour contenir la légende
      var div = L.DomUtil.create("div", "legend-container");
      var divLegend = L.DomUtil.create("div", "legend");

      // Ajout des légendes des marqueurs
      for (const markerConfig of Object.values(this._config.markers || {})) {
          for (const legendConfig of  markerConfig.legends || []) {
            divLegend.innerHTML += this.markerLegend(legendConfig);
          }

          // Ajout des légendes des couches
          for (const layerConfig of Object.values(this._config.layers || {})) {
            divLegend.innerHTML += this.layerLegend(layerConfig);
          }
      }

      // Ajout du contenu de la légende au conteneur principal
      div.appendChild(divLegend);
      return div;
    };
    // Ajout du contrôle de légende à la carte
    legend.addTo(this._map);
  },

};

export { mapLegend };
