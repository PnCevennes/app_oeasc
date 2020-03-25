<template>
  <div class="map-container">
    <!-- map -->
    <div class="map" :id="mapId" :config="config"></div>

    <!-- aside   -->
    <div>
      <slot name="aside">aa</slot>
    </div>
  </div>
</template>

<script>
import { MapService } from "@/modules/map";

export default {
  name: "baseMap",
  data: () => ({
    mapService: null
  }),
  props: ["config", "mapId"],
  methods: {},
  mounted: function() {
    this.mapService = new MapService(this.mapId, this.config);
    this.$store.commit('setMapService', this.mapService)
    this.mapService.init();
  }
};
</script>