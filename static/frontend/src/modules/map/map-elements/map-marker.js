import { restitution } from "@/core/js/restitution";

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

  processMarkersConfig(config) {
    config.markers = config.data.map(d => ({
      type: config.type,
      properties: d,
      style: config.style || {},
      icon: config.icon,
      coords: d[config.coords],
    }));

    //filter
    for (const markerConfig of config.markers) {
      this.applyFilters(markerConfig);
    }

    // color ...icon
    for (const type of ["color", "icon"]) {
      const configType = config[type];
      if (configType) {
        configType.dataList = restitution.dataList(
          config.markers.map(m => ({ ...m.properties, selected: m.selected })),
          configType.options
        );

        for (const markerConfig of config.markers) {
          markerConfig.style[type] = restitution.valueOfType(
            type,
            markerConfig.properties[configType.options.name],
            configType.dataList,
            configType.options
          );
        }

        const cond_same =
          config.color &&
          config.icon &&
          config.color.options.name == config.icon.options.name;

        if (!(type == "icon" && cond_same)) {
          config.legends.push(
            {
              title: configType.options.text
            },
            ...configType.dataList.map(d => {
              const legend = {
                text: `${d.text} (${d.count})`,
                color: "grey",
                icon: "square"
              };
              legend[type] = restitution.valueOfType(
                type,
                d.text,
                configType.dataList,
                configType.options
              );
              if (cond_same) {
                legend['icon'] = restitution.valueOfType(
                  'icon',
                  d.text,
                  configType.dataList,
                  configType.options
                );
  
              }

              return legend;
            })
          );
        }
      }
    }

    // add marker
    for (const markerConfig of config.markers) {
      this.addMarker(markerConfig);
    }
  },

  markerLabel(marker) {
    if(! marker.selected) {
      return '';
    }
    const color = marker.style.color || "blue";
    const icon = marker.style.icon || "circle";
    const label = `<i class='mdi mdi-${icon}' style='color:${color}'></i>`;
    return label;
  },

  initMarkers() {
    this.removeMarkers();
    for (const [key, markerConfig] of Object.entries(
      this._config.markers || {}
    )) {
      markerConfig.key = key;
      this.processMarkersConfig(markerConfig); //filter & color & legend
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

    marker.selected = markerConfig.selected;
    marker.type = markerConfig.type;
    marker.properties = markerConfig.properties;
    marker.style = markerConfig.style;

    this._markers.push(marker);

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
    marker.style.opacity = marker.selected ? 0.8 : 0.1;
    marker.style.fillOpacity = marker.selected ? 0.2 : 0;
    if (marker.type == "marker") {
      marker.setOpacity(marker.style.opacity);
    } else if (marker.type == 'circle') {
      marker.setStyle(marker.style);
    } else {
      marker.setStyle({opacity: 0, fillOpacity: 0})
    }
  }
};

export { mapMarker };
