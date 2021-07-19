<template>
  <div :style="`height:${height || '400px'}; width: 100%`">
    <highcharts
      v-if="!processing"
      :style="`width:${width || '100%'}; height:${height || '400px'}`"
      :options="chartOptions"
      :highcharts="hcInstance"
    ></highcharts>
    <v-progress-linear v-else active indeterminate></v-progress-linear>
  </div>
</template>

<script>
import Highcharts from "highcharts";
import exportingInit from "highcharts/modules/exporting";
import offlineExporting from "highcharts/modules/offline-exporting";
import processIce from "./config/graph-ice";
import processIceData from "./config/graph-ice-data";
import processBilan from "./config/graph-bilan";

exportingInit(Highcharts);
offlineExporting(Highcharts);

export default {
  name: "graph-chasse",
  props: ["id_espece", "id_zone_cynegetique", "type", "width", "height"],
  data: () => ({
    chartOptions: null,
    hcInstance: Highcharts,
    processData: {
      ice: processIce,
      ice_data: processIceData,
      bilan: processBilan
    },
    actions: {
      ice: "chasseIce",
      ice_data: "chasseIce",
      bilan: "chasseBilan"
    },
    processing: false
  }),
  watch: {
    $props: {
      handler() {
        this.process();
      },
      deep: true,
      immediate: true
    }
  },
  methods: {
    process() {
      if (this.processing) {
          console.log('uu', this.type)
          return 
      }
      if (
        !(this.id_zone_cynegetique && this.id_espece && this.type)
      ) {
        return;
      }
      if (!(this.actions[this.type] && this.processData[this.type])) {
        console.error(
          `Pas de fonctionalité définies pour le type ${this.type}`
        );
        return;
      }

      this.processing = true;
      this.$store
        .dispatch(this.actions[this.type], {
          id_espece: this.id_espece,
          id_zone_cynegetique: this.id_zone_cynegetique
        })
        .then(data => {
          console.log(this.type, data);
          this.chartOptions = this.processData[this.type](data);
          this.processing = false;
        });
    }
  },
  mounted() {
    this.process();
  }
};
</script>
