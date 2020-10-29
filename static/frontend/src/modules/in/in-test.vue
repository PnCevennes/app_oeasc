<template>
  <div>
    <h1>
      Indices nocturnes
    </h1>
    <div v-for="nom_espece of nom_especes" :key="nom_espece">
      <div v-if="chartOptions[nom_espece]">
        <highcharts
          style="height:600px; width:800px"
          :options="chartOptions[nom_espece]"
          :highcharts="hcInstance"
        ></highcharts>
      </div>
    </div>
  </div>
</template>

<script>
import Highcharts from "highcharts";

const round = function(x, dec) {
  if (x == 0) return 0;
  return Math.floor(x * 10 ** dec) / 10 ** dec;
};

export default {
  name: "in-test",
  data: () => ({
    chartOptions: {},
    hcInstance: Highcharts,
    nom_especes: ["Cerf", "Chevreuil", "Lievre", "Renard"],
    dataIn: null
  }),
  methods: {
    initGraph() {
      if (!this.dataIn) {
        return;
      }

      for (const nom_espece of this.nom_especes) {
        const series = [];
        const data_espece = this.dataIn.nom_especes[nom_espece];
        for (const [ug, data_ug] of Object.entries(data_espece.ugs)) {
          const serie = [],
            error = [];

          for (const [annee, data_annee] of Object.entries(data_ug.annees)) {
            serie.push([parseInt(annee), data_annee.moy]);
            if (data_annee.sup) {
              error.push([parseInt(annee), data_annee.inf, data_annee.sup]);
            }
          }
          series.push({
            id: ug,
            name: ug,
            data: serie,
            tooltip: {
              pointFormatter: function() {
                var point = this;
                var x = point.options.x;
                var y = point.options.y;
                var inf = data_ug.annees[String(x)].inf;
                var sup = data_ug.annees[String(x)].sup;
                var out = `<b>UG</b> : ${ug}<br>`;
                var dec = 2;
                out += `<b>IN</b> : ${round(y, dec)}<br>`;
                if (sup) out += `<b>Sup</br>: ${round(sup, dec)}<br>`;
                if (inf || inf == 0) out += `<b>Inf</>: ${round(inf, dec)}<br>`;
                // return point.series.name + ': ' + (point.y > 0 ? 'On' : 'off') + '<br>'
                return out;
              }
            }
          });
          series.push({
            type: "errorbar",
            linkedTo: ug,
            data: error,
            enableMouseTracking: false
          });
          this.chartOptions[nom_espece] = {
            title: {
              text: `Indices nocturnes par unité de gestion (${nom_espece})`
            },
            xAxis: {
              title: {
                text: "Année"
              }
            },
            yAxis: {
              min: -0.01,
              endOnTick: false,
              startOnTick: false,
              title: {
                text: "IN (individus / km)"
              }
            },
            series: series,
            height: "600px",
            width: "600px"
          };
        }
      }
      this.chartOptions = { ...this.chartOptions };
    }
  },

  mounted() {
    this.$store.dispatch("inResults").then(data => {
      this.dataIn = data;
      this.initGraph();
    });
  }
};
</script>
