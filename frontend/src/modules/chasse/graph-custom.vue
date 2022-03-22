<template>
  <div :style="`height:${height || '400px'}; width: 100%`">
    <highcharts
      v-if="!processing && chartOptions"
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
import processData from "./config/graph-custom";
import restitutionChasse from "./config/restitution-chasse";


exportingInit(Highcharts);
offlineExporting(Highcharts);

export default {
  name: "graph-chasse",
  props: ["field_name", "height", "width", "title", "typeGraph", "view"],
  data: () => ({
    chartOptions: null,
    hcInstance: Highcharts,
    processData: processData,
    action: "chasseCustom",
    processing: false
  }),
  watch: {
    $props: {
      handler() {
        console.log(this.field_name)
        this.process();
      },
      deep: true,
      immediate: true
    }
  },
  methods: {
    process() {
      if (this.processing) {
          return
      }
      if (
        !(this.field_name)
      ) {
        return;
      }

      this.processing = true;
      console.log(this.$props)
      this.$store
        .dispatch(this.action, this.$props)
        .then(data => {
          this.chartOptions = this.processData(data, this.$props, restitutionChasse);
          this.processing = false;
        });
    }
  },
  mounted() {
    this.process();
  }
};
</script>
