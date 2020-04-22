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
  initMarkers() {
    for (const [key, markerConfig] of Object.entries(
      this._config.markers || {}
    )) {
      this.addMarkers({ ...markerConfig, key });
    }
  },
  addMarkers(config) {
    for (const marker of config.markers) {
      this.addMarker({ ...marker, options: config.options });
    }
  },

  addMarker(markerConfig) {
    const marker = L.marker(markerConfig.coords, markerConfig.options).addTo(
      this._map
    );
    marker.properties = markerConfig.properties;
    marker.opacity = markerConfig.opacity || 1;
    this._markers.push(marker);
  },

  updateMarkers() {
    for (const marker of this._markers) {
      marker.setOpacity(marker.opacity);
    }
  }
};

export { mapMarker };
