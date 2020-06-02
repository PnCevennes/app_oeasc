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
import * as chroma from "chroma-js";

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
    color(ug, type) {
      const colors = {
        Méjean: "yellow",
        "Mont Aigoual": "red",
        "Mont Lozère": "blue",
        "Vallées cévenoles": "green"
      };

      var color = colors[ug];

      if (!color) {
        return;
      }

      color = chroma(color);

      if (type == "error") {
        color = color.darken(1);
      }

      if (type == "reglin") {
      color = color.darken(1);
      }

      return color.toString();
    },
    initGraph() {
      if (!(this.dataIn && this.espece)) {
        return;
      }
      console.log("initGraph");
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
          regLin.push([
            parseInt(annee),
            parseInt(annee) * data_ug.reg_lin.a + data_ug.reg_lin.b
          ]);
        }
        var dec = 4;

        series.push({
          name: `y = ${round(data_ug.reg_lin.a, dec)}x + ${round(
            data_ug.reg_lin.b,
            dec
          )} (err=${round(data_ug.reg_lin.err, dec)})`,
          data: regLin,
          linkedTo: ug,
          enableMouseTracking: false,
          color: this.color(ug, "reglin")
        });

        series.push({
          id: ug,
          name: ug,
          data: serie,
          color: this.color(ug),

          tooltip: {
            pointFormatter: function() {
              var point = this;
              var x = point.options.x;
              var y = point.options.y;
              var inf = data_ug.annees[String(x)].inf;
              var sup = data_ug.annees[String(x)].sup;
              var { a, b, err } = data_ug.reg_lin;
              var out = `<b>UG</b> : ${ug}<br>`;
              out += `<b>IN</b> : ${round(y, dec)}<br>`;
              if (sup) out += `<b>Sup</br>: ${round(sup, dec)}<br>`;
              if (inf || inf == 0) out += `<b>Inf</>: ${round(inf, dec)}<br>`;
              if (a && b && err) {
                out += `y = ${round(inf, dec)}x + ${round(b, dec)}<br>`;
                out += `err = ${round(err, dec)}<br>`;
              }
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
          enableMouseTracking: false,
          color: this.color(ug, "error")
        });

        console.log(regLin);

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
