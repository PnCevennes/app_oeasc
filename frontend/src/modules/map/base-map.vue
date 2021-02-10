<template>
  <div>
    <div class="map-container" :style="`height:${computedHeight}`">
      <!-- map -->
      <div
        v-if="test"
        class="map"
        :ref="mapId"
        :id="mapId"
        :config="config"
        :style="`height:${computedHeight}; z-index:0;`"
      >
                  <div v-if="exportImg !== undefined" class='map-export'>
      <v-btn icon @click="bExportMap = true">
        <v-icon>
          image
        </v-icon>
      </v-btn>
      <v-dialog max-width="1400px" v-model="bExportMap">
        <v-card v-if="bExportMap">
          <generic-form
            class="edit-dialog"
            :config="configFormExportMap"
          ></generic-form>
        </v-card>
      </v-dialog>
    </div>

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
import configFormExportMap from "./config/form-export-map";
import GenericForm from "../../components/form/generic-form.vue";

export default {
  name: "baseMap",
  components: { listForm, mapLegend, GenericForm },
  data: () => ({
    bInit: false,
    mapService: null,
    configSelects: {},
    bExportMap: false,
    test: true
  }),
  props: [
    "config",
    "mapId",
    "preConfigName",
    "height",
    "fillHeight",
    "exportImg"
  ],
  watch: {
    height() {
      this.test = false;
      setTimeout(() => {
        this.test = true;
        setTimeout(() => {
          this.mapService.init();
        }, 100);
      });
    }
  },
  methods: {
    initSelect($event) {
      const key = $event.detail.key;
      this.configSelects[key] = this.mapService.configSelect(key);
      this.configSelects = { ...this.configSelects };
    }
  },
  computed: {
    configFormExportMap() {
      const out = {
        ...configFormExportMap,
        action: {
          process: ({ postData }) => {
            return new Promise(resolve => {
              const options = {
                filename: postData.filename,
                height: postData.height,
                width: postData.width,
                format: postData.filename.endsWith(".jpg") ? "jpg" : "png"
              };

              this.mapService.toImgFile(options).then(() => {
                this.bExportMap = false; // ferme le dialogue
                resolve();
              });
            });
          }
        },
        value: {
          filename: "export_carte_oeasc.png",
          // width: 1000,
          width: this.$refs[this.mapId].clientWidth,
          height: this.$refs[this.mapId].clientHeight
        }
      };
      return out;
    },
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
