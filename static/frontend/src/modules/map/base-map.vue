<template>
  <div>
    <div v-if="exportImg != undefined">
      <v-btn icon @click="epxortMapToImg()">
        <v-icon>
          image
        </v-icon>
      </v-btn>
    </div>
    <div class="map-container" :style="`height:${computedHeight}`">
      <!-- map -->
      <div
        class="map"
        :id="mapId"
        :config="config"
        :style="`height:${computedHeight}; z-index:0;`"
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
  props: [
    "config",
    "mapId",
    "preConfigName",
    "height",
    "fillHeight",
    "exportImg"
  ],
  methods: {
    epxortMapToImg() {
      this.mapService.toImgFile("png");
    },
    initSelect($event) {
      const key = $event.detail.key;
      this.configSelects[key] = this.mapService.configSelect(key);
      this.configSelects = { ...this.configSelects };
    }
  },
  computed: {
    computedHeight() {
      const computedHeight = !this.bInit
        ? "0px"
        : this.height
        ? this.height
        : "fillHeight" in this.$props && this.$el
        ? `${document.documentElement.clientHeight - this.$el.offsetTop - 40}px`
        : "600px";
      return computedHeight;
    }
  },
  mounted: function() {
    if (!this.config) {
      this.config = MapService.getPreConfigMap(this.preConfigName);
    }
    this.bInit = true;

    this.mapService = new MapService(this.mapId, this.config);
    this.$store.commit("setMapService", this.mapService);
    this.mapService.init();
    document
      .getElementById(this.mapId)
      .addEventListener("layer-data", this.initSelect);
  }
};
</script>
