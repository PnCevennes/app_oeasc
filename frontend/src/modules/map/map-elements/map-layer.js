/**
 * Gestion des layers
 */

import { apiRequest } from "@/core/js/data/api.js";

const L = window.L;

const mapLayer = {
  /**
   * pour pouvoir gérer les url de façon dynamique:
   *
   * deux possibilités
   * - url est une chaine de caractères
   * - url est une fonction qui sera appelée avec le parametre urlParams
   *
   *  */

  getUrl: function(layerConfig) {
    return typeof layerConfig.url == "function"
      ? layerConfig.url(layerConfig.urlParams)
      : layerConfig.url;
  },

  /**
   * Ajoute un layer à partir de sa configuration
   */
  addLayer: function(layerConfig) {
    // url
    const url = this.getUrl(layerConfig);

    // requete
    apiRequest("GET", url).then(
      layerData => {
        this.processLayer(layerConfig, layerData);
      },
      error => {
        console.error(`MapLayer Error : ${error}`)        
      }
    );
  },

  /**
   * process layer
   */
  processLayer: function(layerConfig, layerData) {
    // select

    const layer = L.geoJSON(layerData, {
      style: layerConfig.style,
      pane: layerConfig.pane,
      onEachFeature: this.onEachFeature(layerConfig).bind(this)
    });
    layer.addTo(this._map);

    // zoom
    if (layerConfig.zoom) {
      setTimeout(() => {
        this.zoomOnLayer(layer);
      }, 100);
    }

    // dispatch layer-data
    const detail = {
      key: layerConfig.key
    };
    document
      .getElementById(this._id)
      .dispatchEvent(new CustomEvent("layer-data", { detail }));
  },

  /**
   * onEachFeature
   */
  onEachFeature: function(layerConfig) {
    return function(feature, layer) {
      // set key
      feature.properties.key = layerConfig.key;

      // set current style
      layer.curStyle = layerConfig.style;

      // tooltip
      if (layerConfig.tooltip) {
        const tooltipText = feature.properties[layerConfig.tooltip.label];
        this.addTooltip(layer, layerConfig.tooltip, tooltipText);
      }

      // hover
      if (layerConfig.hover && layerConfig.hover.style) {
        layer.on({
          mouseover: function() {
            layer.setStyle(layerConfig.hover.style);
          },
          mouseout: function() {
            layer.setStyle(layer.curStyle);
          }
        });
      }

      // click
      if (layerConfig.click) {
        layer.on(
          "click",
          function() {
            if (layerConfig.click.dispatch) {
              const name = layerConfig.click.dispatch.name;
              const detail = { key: layerConfig.key };
              for (const key of layerConfig.click.dispatch.detail) {
                detail[key] = layer.feature.properties[key];
              }
              const event = new CustomEvent(name, { detail });
              document.getElementById(this._id).dispatchEvent(event);
            }
          }.bind(this)
        );
      }
    }.bind(this);
  },

  /**
   * zoom on layer
   */
  zoomOnLayer: function(layer) {
    this._map.fitBounds(layer.getBounds());
  },

  reinitZoom() {
    for (const [key, layerConfig] of Object.entries(this._config.layers)) {
      if (layerConfig.zoom) {
        console.log(key)
        const layers = this.findLayers("key", key);
        this.zoomOnLayers(layers);
      }
    }
  },

  /**
   * zoom on layer
   */
  zoomOnLayers: function(layers) {
    if (!(layers && layers.length)) {
      return;
    }
    const layersGroup = L.featureGroup(layers);
    const bounds = layersGroup.getBounds();
    this._map.fitBounds(bounds);
    return true;
  },

  removeLayers: function(layers) {
    for (const layer of layers) {
      this.removeLayer(layer);
    }
  },

  removeLayer: function(layer) {
    this._map.removeLayer(layer);
  },

  /**
   * Initialise tous les layers
   * */
  initLayers: function() {
    for (const [key, layerConfig] of Object.entries(this._config.layers)) {
      layerConfig.key = key;
      this.addLayer(layerConfig);
    }
  },

  testLayer: function(properties, fieldName, value) {
    return (
      properties &&
      (Array.isArray(value)
        ? value.includes(properties[fieldName])
        : properties[fieldName] === value)
    );
  },

  findLayer: function(fieldName, value, layersIn = null) {
    const layers = layersIn || Object.values(this._map._layers);
    const layer = layers.find(layer =>
      this.testLayer(
        layer.feature && layer.feature.properties,
        fieldName,
        value
      )
    );
    return layer;
  },

  findLayers: function(fieldName, value, layersIn = null) {
    const layers = layersIn || Object.values(this._map._layers);
    return layers.filter(layer =>
      this.testLayer(
        layer.feature && layer.feature.properties,
        fieldName,
        value
      )
    );
  },

  configSelect(key) {
    if (!(this._config && this._config.layers && this._config.layers[key])) {
      return;
    }

    const layerConfig = this._config.layers[key];
    if (!(layerConfig.select && layerConfig.select.build)) {
      return;
    }
    const items = this.findLayers("key", key).map(
      layer => layer.feature.properties
    );

    const change = () => {
      if (layerConfig.select.markerFilter) {
        this.initMarkers();
      }

      layerConfig.select.change && layerConfig.select.change();
      if (layerConfig.select.zoomOnChange) {
        const value = this.baseModel[key];

        if (
          Array.isArray(value)
            ? value.length
            : value && value[layerConfig.select.valueFieldName]
        ) {
          const layers = this.findLayers(
            layerConfig.select.valueFieldName,
            value[layerConfig.select.valueFieldName]
          );
          this.zoomOnLayers(layers);
        } else {
          this.reinitZoom();
        }
      }
    };

    const configSelects = {
      name: key,
      label: layerConfig.legend,
      items,
      ...layerConfig.select,
      change
    };
    return configSelects;
  }
};

export { mapLayer };
