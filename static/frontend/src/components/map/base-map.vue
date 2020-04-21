<template>
  <div class="map-container" :style="`height:${height || '600px'}`">
    <!-- map -->
    <div
      class="map"
      :id="mapId"
      :config="config"
      :style="`height:${height || '600px'}; z-index:0`"
    ></div>

    <!-- aside   -->
    <div>
      <slot name="aside"> </slot>
    </div>
  </div>
</template>

<script>
import { MapService } from "@/modules/map";
import "./base-map.css";

export default {
  name: "baseMap",
  data: () => ({
    mapService: null
  }),
  props: ["config", "mapId", "preConfigName", "height"],
  methods: {},
  mounted: function() {
    if (!this.config) {
      this.config = MapService.getPreConfigMap(this.preConfigName);
    }
    this.mapService = new MapService(this.mapId, this.config);
    this.$store.commit("setMapService", this.mapService);
    this.mapService.init();
  }
};
</script>
