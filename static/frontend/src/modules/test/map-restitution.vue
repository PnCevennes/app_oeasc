<template>
  <div v-if="config">
    <base-map ref="map" mapId="map" :config="config" fillHeight> </base-map>
  </div>
</template>

<script>
import baseMap from "@/modules/map/base-map.vue";

export default {
  name: "map-restitution",
  components: { baseMap },
  props: ["results"],
  data() {
    return {
      config: null
    };
  },
  watch: {
    results() {
      console.log(
        "res watch",
        (this.results.markerLegendGroups || []).map(a => a.title)
      );
      this.processConfig();
    }
  },
  methods: {
    processConfig() {
      const config = {
        layerList: {
          zc: {},
          aa: {},
          secteurs: {
            zoom: true
          }
        }
      };
      if (this.results) {
        config.markers = this.results && this.results.markers;
        config.markerLegendGroups =
          this.results && this.results.markerLegendGroups;
      }
      this.config = config;
      if (this.$refs.map && this.$refs.map.mapService) {
        this.$refs.map.mapService._config.markers = config.markers;
        this.$refs.map.mapService._config.markerLegendGroups = config.markerLegendGroups;
        this.$refs.map.mapService.initMarkers();
      }
    }
  },
  mounted() {
    this.processConfig();
  }
};
</script>
