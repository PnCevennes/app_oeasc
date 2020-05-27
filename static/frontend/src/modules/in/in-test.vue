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

export default {
  name: "in-test",
  data: () => ({
    chartOptions: null,
    hcInstance: Highcharts,
    espece: "Cerf",
    dataIn: null
  }),
  methods: {
    initGraph() {
      if (!this.dataIn) {
        return;
      }
      const series = [];
      series;

      const data_espece = this.dataIn.especes[this.espece];
      console.log("data", data_espece.ugs);
      for (const [ug, data_ug] of Object.entries(data_espece.ugs)) {
        console.log(ug, data_ug);

        const serie = [],
          error = [];

        for (const [annee, data_annee] of Object.entries(data_ug.annees)) {
          serie.push([parseInt(annee), data_annee.moy]);
          if (data_annee.sup) {
            error.push([parseInt(annee), data_annee.inf, data_annee.sup]);
          }
        }
        console.log(serie)
        console.log(error)
        series.push({
          id: ug,
          name: ug,
          data:serie,
          }
          );
        series.push({
          type: "errorbar",
              linkedTo: ug,data:error});
        //   for (const ug of ugs) {
        //     const data_ug = data.filter(d => d.ug == ug);

        //     series.push({
        //       id: ug,
        //       name: ug,
        //       data: data_ug.map(d => [d.annee, d.in])
        //     });
        //     series.push({
        //       type: "errorbar",
        //       linkedTo: ug,
        //       data: data_ug.map(d => [
        //         d.annee,
        //         d.in - d.variance / 2,
        //         d.in + d.variance / 2
        //       ])
        //     });
        //   }
        //   console.log(series);
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
              text: "IN (individu / km)"
            }
          },
          series: series,
          height: "600px",
          width: "600px"
        };
      }
    }
  },

  mounted() {
    console.log("mounted");
    this.$store.dispatch("in_results").then(data => {
      this.dataIn = data;
      this.initGraph();
    });
  }
};
</script>
