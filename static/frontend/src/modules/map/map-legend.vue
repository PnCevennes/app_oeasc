<template>
  <div class="legend-container" v-if="config">
    <div
      class="legend"
      v-for="(markerLegendGroup, index1) of config.markerLegendGroups || []"
      :key="index1"
    >
      <template v-if="markerLegendGroup.title">
        <b>{{ markerLegendGroup.title }}</b>
      </template>
      <div
        v-for="(legend, index) of markerLegendGroup.legends || []"
        :key="index"
      >
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
          <span v-if="legend.count">
            ({{ legend.count }})</span
          >
        </span>
      </div>
    </div>
    <div class="legend">
      <div v-if="Object.entries(config.layers || []).length && config.markers">
        <br />
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
      console.log("watch legend config");
    }
  },
  methods: {
    getColor(color, opacity) {
      return chroma(color || "black").alpha(opacity);
    }
  }
};
</script>
