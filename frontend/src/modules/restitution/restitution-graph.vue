<template>
  <div>
    <highcharts
      v-if="chartOptions"
      :style="
        `width:${width || '100%'}; height:${results.options.height || '600px'}`
      "
      :options="chartOptions"
      :highcharts="hcInstance"
    ></highcharts>
  </div>
</template>

<script>
import Highcharts from "highcharts";

export default {
  name: "restitution-graph",
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
      this.chartOptions = null;
      const categories = this.results.choix.choix1.dataList.map(
        data => `${data.text} (${data.count})`
      );
      const series =
        !this.results.condSame &&
        this.results.choix.choix2 &&
        ["column", "bar"].includes(this.results.options.typeGraph)
          ? this.results.choix.choix2.dataList.map(res2 => ({
              name: `${res2.text} (${res2.count})`,
              data: this.results.choix.choix1.dataList.map(res1 => {
                const res = res1.subDataList.find(d => d.text == res2.text);
                return (res && res.count) || 0;
              }),
              color: res2.color
            }))
          : // pie
            [
              {
                name: this.results.choix.choix1.text,
                colorByPoint: true,
                data: this.results.choix.choix1.dataList.map(data => ({
                  name: `${data.text} (${data.count})`,
                  y: data.count,
                  color: data.color,
                })),
                dataLabels: {
                  style: {
                    fontSize: '1.15em',
                    fontWeight: 1
                  }
                }
              }
            ];
      const chartOptions = {
        chart: {
          type: this.results.options.typeGraph,
        
        },
        title: {
          text: this.results.options.typeGraph == 'pie' ? this.results.yTitle : null,
          verticalAlign: 'bottom',
          style: {fontSize: '1em'}  
        },
        xAxis: {
          categories
        },
        yAxis: {
          min: 0,
          title: {
            text: this.results.yTitle
          }
        },
        plotOptions: {
          series: {
            stacking: this.results.options.typeGraph != 'pie' && this.results.options.stacking ? "normal" : null
          }
        },
        series
      };
      setTimeout(() => {
        this.chartOptions = chartOptions;
      });
    }
  },
  mounted() {
    this.initGraph();
  }
};
</script>
