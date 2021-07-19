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

exportingInit(Highcharts);
offlineExporting(Highcharts);

export default {
  name: "graph-bilan-chasse",
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

      Promise.all([
        this.$store.dispatch("chasseBilan", {
          id_espece: this.id_espece,
          id_zone_cynegetique: this.id_zone_cynegetique
        }),
        this.$store.dispatch("getAllCommonsEspece"),
        this.$store.dispatch("getAllChasseZoneCynegetique")
      ]).then(([dataBilanChasse, especes, zoneCynegetiques]) => {
        console.log(especes, zoneCynegetiques)
        this.dataBilanChasse = dataBilanChasse;
        const nom_espece = this.$store.getters.commonsEspece(this.id_espece).nom_espece;
        const nom_zone_cynegetique = this.$store.getters.chasseZoneCynegetique(this.id_zone_cynegetique).nom_zone_cynegetique;

        this.chartOptions = {
          title: {
            text: `Évolution des plans de chasse : ${nom_espece}, ${nom_zone_cynegetique}.`
          },
          xAxis: {
            title: {
              text: "Saisons"
            },
            labels: {
              enabled: true,
              formatter: function() {
                return (
                  dataBilanChasse && dataBilanChasse.nb_realise[this.value][0]
                );
              }
            }
          },
          yAxis: {
            // min: -0.01,
            // endOnTick: false,
            // startOnTick: false,
            title: {
              text: "Réalisation"
            }
          },
          series: [
            {
              type: "column",
              name: "Affectation min",
              data: this.dataBilanChasse.nb_affecte_min
            },
            {
              type: "column",
              name: "Affectation max",
              data: this.dataBilanChasse.nb_affecte_max
            },
            {
              name: "Réalisations avant novembre",
              data: this.dataBilanChasse.nb_realise_avant_11
            },
            {
              name: "Réalisations",
              data: this.dataBilanChasse.nb_realise
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
