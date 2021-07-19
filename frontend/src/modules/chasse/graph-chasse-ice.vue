<template>
  <div :style="`height:${height || '400px'}; width: 100%`">
    <highcharts
      v-if="chartOptions"
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
import { round } from "@/core/js/util/util.js";

exportingInit(Highcharts);
offlineExporting(Highcharts);

export default {
  name: "graph-chasse-ice",
  props: ["id_espece", "id_zone_cynegetique", "width", "height"],
  data: () => ({
    dataBilanChasse: null,
    chartOptions: null,
    hcInstance: Highcharts
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
      if (!(this.id_zone_cynegetique && this.id_espece)) {
        return;
      }

      this.$store
        .dispatch("chasseIce", {
          id_espece: this.id_espece,
          id_zone_cynegetique: this.id_zone_cynegetique
        })
        .then(data => {
          console.log(data);
          const dataGraph = data.res_lm_moy;
          this.chartOptions = {
            title: {
              text: `Evolution des ICE - Masse Corporelle - ${data.nom_espece} - ${data.nom_zone_cynegetique}`
            },
            xAxis: {
              title: {
                text: "Saison"
              },
              labels: {
                enabled: true,
                formatter: function() {
                  return `${this.value}-${this.value + 1}`;
                }
              }
            },
            yAxis: {
              // min: -0.01,
              // endOnTick: false,
              // startOnTick: false,
              title: {
                text: "Poids (kg)"
              }
            },
            series: [
              {
                id: "ice",
                name: "Poids moyen",
                data: Object.keys(dataGraph.x).map(ind => [
                  dataGraph.x[ind],
                  dataGraph.y[ind]
                ])
              },
              {
                type: "errorbar",
                linkedTo: "ice",
                name: "Intervalle de confiance",
                data: Object.keys(dataGraph.x).map(ind => [
                  dataGraph.x[ind],
                  dataGraph.inf[ind],
                  dataGraph.sup[ind]
                ]),
                enableMouseTracking: false,
                maxPointWidth: 40
              },
              {
                name: `Regression (p-value=${round(dataGraph.p_value_slope, 3)})`,
                data: [
                  [dataGraph.x[0], dataGraph.intercept + dataGraph.x[0] * dataGraph.slope],
                  [dataGraph.x[dataGraph.x.length - 1], dataGraph.intercept + dataGraph.x[dataGraph.x.length - 1] * dataGraph.slope],
                ],
                enableMouseTracking: false,
                maxPointWidth: 40
              }
            ],
            height: "600px",
            width: "600px"
          };
        });
    }
  },
  mounted() {
    this.process();
  }
};
</script>
