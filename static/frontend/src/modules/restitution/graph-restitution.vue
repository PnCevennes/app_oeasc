<template>
  <div>
    <highcharts
      v-if="chartOptions"
      :style="`width:${width || '100%'}; height:${results.height || '600px'}`"
      :options="chartOptions"
      :highcharts="hcInstance"
    ></highcharts>
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

      const categories = this.results.choix.choix1.dataList.map(
        data => data.text
      );
      const series = this.results.choix.choix2 && ['column'].includes(this.results.typeGraph)
        ? this.results.choix.choix2.dataList.map(res2 => ({
            name: res2.text,
            data: this.results.choix.choix1.dataList.map(
              res1 => res1.data2.find(d => d.text == res2.text).count
            ),
            color: res2.color
          }))
        : [
            {
              name: this.results.choix.choix1.text,
              colorByPoint: true,
              data: this.results.choix.choix1.dataList.map(data => ({
                name: data.text,
                y: data.count,
                color: data.color
              }))
            }
          ];
      // const data = this.results.choix.choix1.dataList.map(data => data.count);
      const yTitle = this.results.choix.choix1.text;
      const chartOptions = {
        chart: {
          // type: "pie",
          type: this.results.typeGraph
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
        plotOptions: {
          series: {
            stacking: this.results.stacking ? 'normal' : null,
          }
        },
        series
      };
      this.chartOptions = chartOptions;
    }
  },
  mounted() {
    this.initGraph();
  }
};
</script>
