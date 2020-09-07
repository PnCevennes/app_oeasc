<template>
  <div v-if="config">
    <base-map ref="map" :mapId="mapId" :config="config" fillHeight :height="results.height"></base-map>
  </div>
</template>

<script>
import baseMap from "@/modules/map/base-map.vue";

export default {
  name: "map-restitution",
  components: { baseMap },
  props: ["results"],
  data: () => ({
    config: null,
    mapId: `map_${Math.ceil(Math.random() * 1e10)}`,
  }),
  watch: {
    results() {
      this.processConfig();
    },
  },
  methods: {
    zoomOnFilter(zoomOnFilterKey, fieldName) {
      if(! ( this.$refs.map && this.$refs.map.mapService)) { return; }
      let layers = this.$refs.map.mapService.findLayers("key", zoomOnFilterKey);
      const filters = this.results.filters[zoomOnFilterKey] || [];
      if (filters.length) {
        layers = this.$refs.map.mapService.findLayers(
          fieldName,
          filters,
          layers
        );
      }
      setTimeout(() => {
        this.$refs.map.mapService.zoomOnLayers(layers);
      }, 100);
    },
    processConfig() {
      const config = {
        layerList: {
          zc: {},
          aa: {},
          secteur: {
            zoom: true,
          },
        },
      };
      if (this.results) {
        config.markers = this.results && this.results.markers;
        config.markerLegendGroups =
          this.results && this.results.markerLegendGroups;
      }
      this.config = config;
      if (this.$refs.map && this.$refs.map.mapService) {
        this.$refs.map.mapService._config.markers = config.markers;
        this.$refs.map.mapService._config.markerLegendGroups =
          config.markerLegendGroups;
        this.$refs.map.mapService.initMarkers();
      }

      const zoomOnFilterKey = Object.keys(this.results.items).find(
        (key) => this.results.items[key].zoomOnFilter
      );
      if (zoomOnFilterKey) {
        setTimeout(() => {
          document
            .getElementById(this.mapId)
            .addEventListener("layer-data", ($event) => {
              const key = $event.detail.key;
              if (key != zoomOnFilterKey) {
                return;
              }
              this.zoomOnFilter(
                key,
                this.results.items[zoomOnFilterKey].zoomOnFilter
              );
            });
        }, 100);
        this.zoomOnFilter(
          zoomOnFilterKey,
          this.results.items[zoomOnFilterKey].zoomOnFilter
        );
      }
    },
  },
  mounted() {
    this.processConfig();
  },
};
</script>
