<template>
  <div :style="`height:${height || '400px'}; width: 100%`">
    <highcharts
      v-if="chartOptions"
      :style="`width:${width || '100%'}; height:${height || '400px'}`"
      :options="chartOptions"
      :highcharts="hcInstance"
    ></highcharts>
    <v-progress-linear v-else active indeterminate></v-progress-linear>
    <div v-if="commentaires" class="commentaires" v-html="commentaires"></div>
  </div>
</template>

<script>
import Highcharts from "highcharts";
import exportingInit from "highcharts/modules/exporting";
import offlineExporting from "highcharts/modules/offline-exporting";
import * as chroma from "chroma-js";
import { round } from "@/core/js/util/util.js";
exportingInit(Highcharts);
offlineExporting(Highcharts);


export default {
  name: "in-graph",
  props: [
    "displayTitle",
    "dataIn",
    "nom_espece",
    "ugs",
    "ug",
    "width",
    "height",
    "displayReg",
    "commentaires"
  ],
  data: () => ({
    dataGraph: null,
    chartOptions: null,
    hcInstance: Highcharts
  }),
  computed: {
    getUgs() {
      return this.ugs && this.ugs.length
        ? this.ugs
        : this.ug
        ? [this.ug]
        : null;
    } 
  },
  watch: {
    dataIn() {
      this.initGraph();
    },
    nom_espece() {
      this.initGraph();
    },
    ug() {
      this.initGraph();
    },
    displayReg() {
      this.initGraph();
    }
  },
  methods: {
    color(ug, type) {
      const colors = {
        Méjean: "#e8e805",
        "Aigoual": "red",
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
      if (this.dataIn) {
        this.dataGraph = this.dataIn;
      }
      this.chartOptions = null;
      setTimeout(() => {
        if (!(this.dataGraph && this.nom_espece)) {
          return;
        }
        const nom_espece = this.nom_espece;
        const series = [];
        const data_espece = this.dataGraph.nom_especes[nom_espece];
        for (const [ug, data_ug] of Object.entries(data_espece.ugs)) {
          if (this.getUgs && !this.getUgs.includes(ug)) {
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
              parseInt(annee) * data_ug.reg_lin.params[0] +
                data_ug.reg_lin.params[1]
            ]);
          }

          var dec = 2;

          const pValue = data_ug.reg_lin.pvalues[0];
          if (pValue && pValue <= 0.1) {
            series.push({
              name: `y = ${round(data_ug.reg_lin.params[0], dec)}x + ${round(
                data_ug.reg_lin.params[1],
                dec
              )} (R2=${round(data_ug.reg_lin.R2, dec)})`,
              data: regLin,
              linkedTo: ug,
              dashStyle: pValue <= 0.05 ? "Solid" : "Dash",
              enableMouseTracking: false,
              color: "grey",
              lineWidth: 1 * (this.displayReg !== undefined),
              marker: {
                enabled: false
              }
            });
          }
          series.push({
            id: ug,
            name: ug,
            data: serie,
            lineWidth: 0,
            color: this.color(ug),
            tooltip: {
              pointFormatter: function() {
                var point = this;
                var y = point.options.y;
                var out = `Secteur : <b>${ug}</b><br>`;
                out += `IN : <b>${round(y, 2)}</b><br>`;
                return out;
              }
            },
            cursor: "pointer",
            point: {
              events: {
                click: e => {
                  this.$emit("clickPoint", e.point.options.x);
                }
              }
            }
          });
          series.push({
            type: "errorbar",
            linkedTo: ug,
            data: error,
            enableMouseTracking: false,
            maxPointWidth: 40,
            color: this.color(ug, "error")
          });

          this.chartOptions = {
            exporting: {
              buttons: {
                contextButton: {
                  menuItems: [
                    {
                      text: "Télécharger l'image au format JPEG",
                      onclick: function() {
                        this.exportChart({
                          type: "image/jpeg"
                        });
                      }
                    }
                  ]
                }
              },
              chartOptions: {
                // specific options for the exported image
                plotOptions: {
                  series: {
                    dataLabels: {
                      // enabled: true,
                    }
                  }
                }
              },
              fallbackToExportServer: false
            },
            title: {
              text:
                this.displayTitle && `Indices nocturnes (${nom_espece}, ${ug})`
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
      }, 10);
    }
  },

  mounted() {
    if (!this.dataIn) {
      this.$store.dispatch("inResults").then(data => {
        this.dataGraph = data;
        this.initGraph();
      });
    } else {
      this.initGraph();
    }
  }
};
</script>
<style>
.commentaires {
  color: rgb(100, 100, 100);
}
</style>
