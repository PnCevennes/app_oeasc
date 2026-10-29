<template>
  <div v-if="config">
    <base-map
      exportImg
      ref="map"
      :mapId="mapId"
      :config="config"
      fillHeight
      :height="results.options.height"
    ></base-map>
  </div>
</template>

<script>
import baseMap from '@/components/map/base-map.vue';

export default {
  name: 'restitution-map',
  components: { baseMap },
  props: ['results'],
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
      if (!(this.$refs.map && this.$refs.map.mapService)) {
        return;
      }
      let layers = this.$refs.map.mapService.findLayers('key', zoomOnFilterKey);
      const filters = this.results.options.filters[zoomOnFilterKey] || [];
      if (filters && filters.length) {
        layers = this.$refs.map.mapService.findLayers(fieldName, filters, layers);
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

        config.markerLegendGroups = this.results && this.results.markerLegendGroups;
      }
      this.config = config;
      if (this.$refs.map && this.$refs.map.mapService) {
        this.$refs.map.mapService._config.markers = config.markers;
        this.$refs.map.mapService._config.markerLegendGroups = config.markerLegendGroups;
        this.$refs.map.mapService.initMarkers();
      }

      const zoomOnFilterKey = Object.keys(this.results.items).find(
        (key) => this.results.items[key].zoomOnFilter
      );
      if (zoomOnFilterKey) {
        // un seul écouteur à la fois : processConfig est rappelé à chaque changement de results
        this.removeLayerDataListener();
        this.layerDataHandler = ($event) => {
          if ($event.detail.key != zoomOnFilterKey) {
            return;
          }
          this.zoomOnFilter(zoomOnFilterKey, this.results.items[zoomOnFilterKey].zoomOnFilter);
        };
        this.$nextTick(() => {
          const elem = document.getElementById(this.mapId);
          if (elem && this.layerDataHandler) {
            elem.addEventListener('layer-data', this.layerDataHandler);
          }
        });
        this.zoomOnFilter(zoomOnFilterKey, this.results.items[zoomOnFilterKey].zoomOnFilter);
      }
    },
    removeLayerDataListener() {
      const elem = document.getElementById(this.mapId);
      if (elem && this.layerDataHandler) {
        elem.removeEventListener('layer-data', this.layerDataHandler);
      }
      this.layerDataHandler = null;
    },
  },
  mounted() {
    this.processConfig();
  },
  beforeUnmount() {
    // l'élément est encore dans le DOM ici (contrairement à unmounted)
    this.removeLayerDataListener();
  },
};
</script>
