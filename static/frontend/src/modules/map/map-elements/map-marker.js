const L = window.L;

const mapMarker = {
  _markers: [],

  removeMarkers() {
    for (let marker of this._markers) {
      this._map.removeLayer(marker);
    }
    this._markers = [];
  },

  markerLabel(marker) {
    let defs = [];
    let label = "";

    if (marker.defs) {
      defs = marker.defs;
    } else {
      const color = marker.style.color || "blue";
      const icon = marker.style.icon || "circle";
      const colors = Array.isArray(color) ? color : [color];
      const icons = Array.isArray(icon) ? icon : [icon];

      if (marker.cond_same) {
        for (var i = 0; i < colors.length; i++) {
          defs.push({ icon: icons[i], color: color[i] });
        }
      } else {
        // bourrin...
        for (const color of colors) {
          for (const icon of icons) {
            defs.push({ icon: icon, color: color });
          }
        }
      }
    }

    for (const def of defs) {
      label += `<i class='mdi mdi-${def.icon}' style='color:${def.color}'></i>`;
    }
    return label;
  },

  initMarkers() {
    this.removeMarkers();
    for (const marker of this._config.markers || []) {
      this.addMarker(marker);
    }

    this.upConfig();
  },

  addMarker(markerConfig) {
    markerConfig.options = {};
    markerConfig.options.pane = markerConfig.pane || "PANE_MARKER_1";

    let marker;
    if (markerConfig.type == "marker") {
      marker = L.marker(markerConfig.coords, markerConfig.options).addTo(
        this._map
      );
    } else if (markerConfig.type == "circle") {
      marker = L.circleMarker(markerConfig.coords, markerConfig.options).addTo(
        this._map
      );
    } else if (markerConfig.type == "label") {
      marker = L.circle(markerConfig.coords, {
        ...markerConfig.options,
        opacity: 0,
        fillOpacity: 0,
        color: "rgba(0,0,0,0)",
        fillColor: "rgba(0,0,0,0)"
      })
        .bindTooltip(this.markerLabel(markerConfig), {
          pane: "PANE_TOOLTIP",
          permanent: true,
          direction: "center",
          color: "white",
          opacity: 1,
          fillOpacity: 1,
          interactive: true,
          className: "tooltip-label"
        })
        .addTo(this._map);
    }

    marker.type = markerConfig.type;
    marker.properties = markerConfig.properties;
    marker.style = markerConfig.style;

    this._markers.push(marker);

    this.setMarkerStyle(marker);
  },

  // applyFilters(marker) {
  //   let cond = true;
  //   for (const filter of this._markerFilters) {
  //     let condFilter = true;
  //     if (filter.type == "selectLayer") {
  //       condFilter = this.condFilterSelectLayer(filter, marker);
  //     }
  //     cond = cond && condFilter;
  //   }
  //   marker.selected = cond;
  // },

  // condFilterSelectLayer(filter, marker) {
  //   let value = this.baseModel[filter.key];
  //   if (!value || (Array.isArray(value) && !value.length)) {
  //     return true;
  //   }
  //   if (!Array.isArray(value)) {
  //     value = [value];
  //   }

  //   let valueMarker = marker.properties[filter.markerFieldName];

  //   if (!valueMarker || (Array.isArray(valueMarker) && !valueMarker.length)) {
  //     return false;
  //   }
  //   if (!Array.isArray(valueMarker)) {
  //     valueMarker = [valueMarker];
  //   }
  //   const cond = value.find(v => valueMarker.includes(v));
  //   return cond;
  // },

  setMarkerStyle(marker) {
    marker.style.opacity = 1;
    marker.style.fillOpacity = 0.2;
    if (marker.type == "marker") {
      marker.setOpacity(marker.style.opacity);
    } else if (marker.type == "circle") {
      marker.setStyle(marker.style);
    } else {
      marker.setStyle({ opacity: 0, fillOpacity: 0 });
    }
  }
};

export { mapMarker };
