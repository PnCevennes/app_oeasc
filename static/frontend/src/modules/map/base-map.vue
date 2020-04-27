<template>
  <div class="map-container" :style="`height:${computedHeight}`">
    <!-- map -->
    {{ computedHeight }}
    <div
      class="map"
      :id="mapId"
      :config="config"
      :style="`height:${computedHeight}; z-index:0; background-color: red`"
    >
      <map-legend
        :config="(mapService && mapService._config) || {}"
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
    bInit: false,
    mapService: null,
    configSelects: {}
  }),
  props: ["config", "mapId", "preConfigName", "height", "fillHeight"],
  methods: {
    initSelect($event) {
      const key = $event.detail.key;
      this.configSelects[key] = this.mapService.configSelect(key);
      this.configSelects = { ...this.configSelects };
    },
    a() {
      console.log("a", this.$el);
    }
  },
  computed: {
    computedHeight() {
      this.a();
      const computedHeight = !this.bInit
        ? "0px"
        : this.height
        ? this.height
        : "fillHeight" in this.$props && this.$el
        ? `${document.documentElement.clientHeight - this.$el.offsetTop -20}px`
        : "600px";
      console.log(computedHeight, "fillHeight" in this.$props, this.$el);
      return computedHeight;
    }
  },
  mounted: function() {
    console.log("aa");
    if (!this.config) {
      this.config = MapService.getPreConfigMap(this.preConfigName);
    }

    this.mapService = new MapService(this.mapId, this.config);
    this.$store.commit("setMapService", this.mapService);
    this.mapService.init();
    this.bInit = true;
    document
      .getElementById(this.mapId)
      .addEventListener("layer-data", this.initSelect);
  }
};
</script>
