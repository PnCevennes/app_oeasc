<template>
  <div class="legend-container" v-if="config && config.layers">
    <div
      class="legend"
      v-for="[key, markerConfig] of Object.entries(config.markers || [])"
      :key="key"
    >
      <div v-for="(legend, index) of markerConfig.legends || []" :key="index">
        <template v-if="legend.title">
          <b>{{ legend.title }}</b>
        </template>
        <template v-else>
          <i
            :style="
              `
            font-size: 1.8em;
            color:${legend.color};
          `
            "
            :class="`mdi mdi-${legend.icon}`"
          ></i>
          <span class="legendText">
            {{ legend.text }}
          </span>
        </template>
      </div>
    </div>
    <div class="legend">
      <div v-if="Object.entries(config.layers || []).length && config.markers">
        <br>
      </div>
      <div
        v-for="[key, layerConfig] of Object.entries(config.layers || [])"
        :key="key"
      >
        <i
          v-if="layerConfig.style"
          :style="
            `
            background-color: ${getColor(
              layerConfig.style.fillColor,
              layerConfig.style.fillOpacity
            )};
            border: ${layerConfig.style.weight}px solid ${
              layerConfig.style.color
            };
          `
          "
        ></i>
        <span class="legendText">
          {{ layerConfig.legend }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import * as chroma from "chroma-js";

export default {
  name: "mapLegend",
  props: ["config"],
  watch: {
    config() {
      // console.log('watch config legend', this.config && this.config.markers && this.config.markers.declarations && this.config.markers.declarations.legends)
    }
  },
  methods: {
    getColor(color, opacity) {
      return chroma(color || "black").alpha(opacity);
    }
  }
};
</script>
