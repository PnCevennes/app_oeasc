<template>
  <div>
    <div
      v-if="chartOptions"
      :style="`height:${height || '400px'}; width: 100%`"
    >
      <highcharts
        v-if="!processing"
        :style="`width:${width || '100%'}; height:${height || '400px'}`"
        :options="chartOptions"
        :highcharts="hcInstance"
      ></highcharts>
      <v-progress-linear v-else active indeterminate></v-progress-linear>
    </div>
    <v-snackbar color="error" v-model="bError" :timeout="5000">
      {{ msgError }}
    </v-snackbar>
  </div>
</template>

<script>
import Highcharts from "highcharts";
import exportingInit from "highcharts/modules/exporting";
import offlineExporting from "highcharts/modules/offline-exporting";
import processIce from "./config/graph-ice";
import processIceData from "./config/graph-ice-data";
import processBilan from "./config/graph-bilan";
import processAttributionBracelet from "./config/graph-attribution-bracelet";

exportingInit(Highcharts);
offlineExporting(Highcharts);

export default {
  name: "graph-chasse",
  props: [
    "id_espece",
    "id_zone_cynegetique",
    "id_secteur",
    "id_zone_indicative",
    "id_saison",
    "bracelet",
    "type",
    "width",
    "height"
  ],
  data: () => ({
    msgError: null,
    bError: null,
    chartOptions: null,
    hcInstance: Highcharts,
    processData: {
      ice: processIce,
      ice_data: processIceData,
      bilan: processBilan,
      attribution_bracelet: processAttributionBracelet
    },
    actions: {
      ice: "chasseIce",
      attribution_bracelet: "chasseAttributionBracelet",
      ice_data: "chasseIce",
      bilan: "chasseBilan"
    },
    processing: false
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
      if (this.processing) {
        return;
      }

      if (!(this.id_espece && this.type)) {
        return;
      }

      // test qu'il n'y ai pas 2 valeur pour zi zc secteur
      if (
        !!this.id_zone_cynegetique.length +
          !!this.id_zone_indicative.length +
          !!this.id_secteur.length >
        1
      ) {
        console.log(
          !!this.id_zone_cynegetique.length +
            !!this.id_zone_indicative.length +
            !!this.id_secteur.length
        );
        return;
      }

      if (!(this.actions[this.type] && this.processData[this.type])) {
        console.error(
          `Pas de fonctionalité définies pour le type ${this.type}`
        );
        return;
      }

      this.processing = true;

      this.$store
        .dispatch(this.actions[this.type], {
          id_espece: this.id_espece,
          id_zone_cynegetique: this.id_zone_cynegetique,
          id_zone_indicative: this.id_zone_indicative,
          id_secteur: this.id_secteur,
          id_saison: this.id_saison,
          bracelet: this.id_bracelet
        })
        .then(
          data => {
            this.chartOptions = this.processData[this.type](data, this.$props);
            this.processing = false;
          },
          error => {
            console.log("error", error);
            this.msgError = `pas de données pour les valeurs suivantes id_espece ${this.id_espece} id_zone_cynegetique ${this.id_zone_cynegetique} id_zone_indicative ${this.id_zone_indicative}`;
            this.bError = true;
            this.processing = false;
            this.chartOptions = null;
          }
        );
    }
  },
  mounted() {
    this.process();
  }
};
</script>
