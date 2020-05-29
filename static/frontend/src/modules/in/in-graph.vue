<template>
  <div>
    <highcharts
      v-if="chartOptions"
      :style="`width:${width || '800px'}; height:${height || '400px'}`"
      :options="chartOptions"
      :highcharts="hcInstance"
    ></highcharts>
  </div>
</template>

<script>
import Highcharts from "highcharts";

const round = function(x, dec) {
  if (x == 0) return 0;
  return Math.floor(x * 10 ** dec) / 10 ** dec;
};

export default {
  name: "in-graph",
  props: ["dataIn", "espece", "ug", "width", "height"],
  data: () => ({
    chartOptions: null,
    hcInstance: Highcharts
  }),
  watch: {
    dataIn() {
      this.initGraph();
    },
    espece() {
      this.initGraph();
    },
    ug() {
      this.initGraph();
    }

  },
  methods: {
    initGraph() {
      if (!(this.dataIn && this.espece)) {
        return;
      }
      console.log('initGraph')
      const espece = this.espece;
      const series = [];
      console.log(this.dataIn);
      const data_espece = this.dataIn.especes[espece];
      for (const [ug, data_ug] of Object.entries(data_espece.ugs)) {
        if (this.ug && ug != this.ug) {
          continue;
        }
        const serie = [],
          error = [],
          regLin = [];

        for (const [annee, data_annee] of Object.entries(data_ug.annees)) {
          serie.push([parseInt(annee), data_annee.moy]);
          if (data_annee.sup) {
            error.push([parseInt(annee), data_annee.inf, data_annee.sup]);
          }
          regLin.push([parseInt(annee), parseInt(annee) * data_ug.reg_lin.a + data_ug.reg_lin.b]);
        }
        var dec = 4;

        series.push({
          name: `y = ${round(data_ug.reg_lin.a, dec)}a + ${round(data_ug.reg_lin.b, dec)} (err=${round(data_ug.reg_lin.err, dec)})`,
          data: regLin
        });


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
              out += `<b>IN</b> : ${round(y, dec)}<br>`;
              if (sup) out += `<b>Sup</br>: ${round(sup, dec)}<br>`;
              if (inf || inf == 0) out += `<b>Inf</>: ${round(inf, dec)}<br>`;
              // return point.series.name + ': ' + (point.y > 0 ? 'On' : 'off') + '<br>'
              return out;
            }
          },
          cursor: "pointer",
          point: {
            events: {
              click: e => {
                this.$emit("clickPoint", e.point.options.x);
                console.log("clickPoint send", e.point.options.x);
              }
            }
          }
        });
        series.push({
          type: "errorbar",
          linkedTo: ug,
          data: error,
          enableMouseTracking: false
        });

        console.log(regLin)

        this.chartOptions = {
          title: {
            text: `Indices nocturnes (${espece}, ${ug})`
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
    this.initGraph();
  }
};
</script>
