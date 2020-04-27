<template>
  <div class="map-container" :style="`height:${height || '600px'}`">
    <!-- map -->
    <div
      class="map"
      :id="mapId"
      :config="config"
      :style="`height:${height || '600px'}; z-index:0`"
    >
      <map-legend
        :config="(mapService && mapService._config || {})"
      ></map-legend>
    </div>

    <!-- aside   -->
    <div>

      <div
        v-for="[key, configSelect] of Object.entries(configSelects)"
        :key="key"
      >
        <div
          v-if="configSelect && mapService && mapService.baseModel"
          class="map-select"
        >
          <list-form
            :baseModel="mapService.baseModel"
            :config="configSelect"
          ></list-form>
        </div>
      </div>
      <div>
        <slot name="aside"> </slot>
      </div>
    </div>
  </div>
</template>

<script>
import { MapService } from "@/modules/map";
import listForm from "@/components/form/list-form";
import mapLegend from "./map-legend";

export default {
  name: "baseMap",
  components: { listForm, mapLegend },
  data: () => ({
    mapService: null,
    configSelects: {}
  }),
  props: ["config", "mapId", "preConfigName", "height"],
  methods: {
    initSelect($event) {
      const key = $event.detail.key;
      this.configSelects[key] = this.mapService.configSelect(key);
      this.configSelects = { ...this.configSelects };
    }
  },
  mounted: function() {
    if (!this.config) {
      this.config = MapService.getPreConfigMap(this.preConfigName);
    }
    this.mapService = new MapService(this.mapId, this.config);
    this.$store.commit("setMapService", this.mapService);
    this.mapService.init();

    document
      .getElementById(this.mapId)
      .addEventListener("layer-data", this.initSelect);
  }
};
</script>
