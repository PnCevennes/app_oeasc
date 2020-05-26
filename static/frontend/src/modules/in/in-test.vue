<template>
  <div>
    <h1>
      Indices Nocturnes
    </h1>

    <div>
      <highcharts
        style="height:600px; width:800px"
        v-if="chartOptions"
        :options="chartOptions"
        :highcharts="hcInstance"
      ></highcharts>
    </div>
  </div>
</template>

<script>
import Highcharts from "highcharts";
import { removeDoublons } from "@/core/js/util/util.js";

export default {
  name: "in-test",
  data: () => ({
    chartOptions: null,
    hcInstance: Highcharts
  }),
  mounted() {
    this.$store.dispatch("in_results").then(data => {
      const ugs = removeDoublons(data.map(d => d.ug));
      const series = [];
      for (const ug of ugs) {
        const data_ug = data.filter(d => d.ug == ug);

        series.push({
          id: ug,
          name: ug,
          data: data_ug.map(d => [d.annee, d.in])
        });
        series.push({
          type: "errorbar",
          linkedTo: ug,
          data: data_ug.map(d => [
            d.annee,
            d.in - d.variance / 2,
            d.in + d.variance / 2
          ])
        });
      }
      console.log(series);
      this.chartOptions = {
        title: {
          text: "Indices nocturnes par unité de gestion"
        },
        xAxis: {
          title: {
            text: "Année"
          }
        },
        yAxis: {
          title: {
            text: "IN"
          }
        },
        series: series,
        height: "600px",
        width: "600px"
      };
    });
  }
};
</script>
