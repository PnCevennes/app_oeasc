<template>
  <div>
    <highcharts
      v-if="chartOptions"
      :style="`width:${width || '800px'}; height:${height || '400px'}`"
      :options="chartOptions"
      :highcharts="hcInstance"
    ></highcharts>
    <pre>
        {{ chartOptions }}
        </pre
    >
  </div>
</template>

<script>
import Highcharts from "highcharts";

export default {
  name: "graph-restitution",
  props: ["results"],
  data: () => ({
    chartOptions: null,
    hcInstance: Highcharts,
    width: null,
    height: null
  }),
  watch: {
    results() {
      this.initGraph();
    }
  },
  methods: {
    initGraph() {
      if (!this.results) {
        return;
      }

      const categories = this.results.choix.color.dataList.map(
        data => data.text
      );
      const series = [
        {
          name: this.results.choix.color.text,
          colorByPoint: true,

          data: this.results.choix.color.dataList.map(data => ({
            name: data.text,
            y: data.count,
            color: data.color,
          }))
        }
      ];
      const data = this.results.choix.color.dataList.map(data => data.count);
      console.log(categories, data);
      const yTitle = this.results.choix.color.text;

      const chartOptions = {
        chart: {
          type: "column"
        },
        title: "Test graphique",
        xAxis: {
          categories
        },
        yAxis: {
          min: 0,
          title: {
            text: yTitle
          }
        },
        series
      };
      this.chartOptions = chartOptions;
      console.log("initGraph");
    }
  },
  mounted() {
    this.initGraph();
  }
};
</script>
