const L = window.L;
/**
config {
    markerList: {
        <key>: {
            legend: "legend",
            markers: [
                ...
                {
                    coords: [lat, lon],
                    autre ?? type etc...
                }
                ...
            ]
        }
    }
}

 */

const mapMarker = {
  _markers: [],
  _markerFilters: [],

  removeMarkers() {
    for (let marker of this._markers) {
      this._map.removeLayer(marker);
    }
    this._markers = [];
  },

  initMarkers() {
    this.removeMarkers();
    for (const [key, markerConfig] of Object.entries(
      this._config.markers || {}
    )) {
      this.addMarkers({ ...markerConfig, key });
    }
  },
  addMarkers(config) {
    for (const markerConfig of config.markers) {
      this.addMarker(markerConfig);
    }
  },

  addMarker(markerConfig) {
    let marker;
    if (markerConfig.type == "marker") {
      marker = L.marker(markerConfig.coords, markerConfig.options).addTo(
        this._map
      );
    } else if (markerConfig.type == "circle") {
      marker = L.circleMarker(markerConfig.coords, markerConfig.options).addTo(
        this._map
      );
    }

    marker.type = markerConfig.type;
    marker.properties = markerConfig.properties;
    marker.style = markerConfig.style;

    this._markers.push(marker);

    this.applyFilters(marker);
    this.setMarkerStyle(marker);
  },

  applyFilters(marker) {
    let cond = true;
    for (const filter of this._markerFilters) {
      let condFilter = true;
      if (filter.type == "selectLayer") {
        condFilter = this.condFilterSelectLayer(filter, marker);
      }
      cond = cond && condFilter;
    }
    marker.selected = cond;
  },

  condFilterSelectLayer(filter, marker) {
    let value = this.baseModel[filter.key];
    if (!value || (Array.isArray(value) && !value.length)) {
      return true;
    }
    if (!Array.isArray(value)) {
      value = [value];
    }

    let valueMarker = marker.properties[filter.markerFieldName];

    if (!valueMarker || (Array.isArray(valueMarker) && !valueMarker.length)) {
      return false;
    }
    if (!Array.isArray(valueMarker)) {
      valueMarker = [valueMarker];
    }
    const cond = value.find(v => valueMarker.includes(v));
    return cond;
  },

  setMarkerStyle(marker) {
    marker.style.opacity = marker.selected ? 1 : 0.1;
    if(marker.type == 'marker') {
      marker.setOpacity(marker.style.opacity);
    }
  }
};

export { mapMarker };
