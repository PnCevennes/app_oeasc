<template>
    <!--
      Graphique pour afficher les resultats de type custom
    -->

    <!-- par defaut hauteur à 400px et largeur à 100% -->
  <div :style="`height:${height || '400px'}; width: 100%`">

    <!-- graphique highchart -->
    <highcharts
      v-if="!isProcessing && chartOptions"
      :style="`width:${width || '100%'}; height:${height || '400px'}`"
      :options="chartOptions"
      :highcharts="hcInstance"
    ></highcharts>

    <!-- chargement en cours (en attendant les données) -->
    <v-progress-linear v-else active indeterminate></v-progress-linear>
  </div>
</template>

<script>

import Highcharts from "highcharts";
import exportingInit from "highcharts/modules/exporting";
import offlineExporting from "highcharts/modules/offline-exporting";
import processData from "./process/graph-custom";
import restitutions from "./config/restitutions";
import props from './config/props';
import { jsoncopy, fde }  from '../../core/js/util/util'


exportingInit(Highcharts);
offlineExporting(Highcharts);

export default {
  name: "restitution-graph",
  props: props,
  data: () => ({
    chartOptions: null, // option pour le graphique highchart (calculé en fonction des options et des données)
    hcInstance: Highcharts,
    isProcessing: false, // test pour ne pas lancer plusieurs requêtes en même temps
    processedProps: null,
  }),

  // on déclenche process à chaque changement de propriété
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

      // test pour ne pas lancer plusieurs requêtes en meme temps
      if (this.isProcessing && fde(this.$props, this.processedProps)) {
        console.log('processing', this.$props, this.processedProps)
          return
      }

      // test sur les champs requis
      const requiredProps = ['fieldName', 'dataType']
      if (requiredProps.some(p => !this[p])) {
        return;
      }

      this.processedProps = jsoncopy(this.$props)

      // debut process
      this.isProcessing = true;

      // configuration de la restitution selon le type
      const restitution = restitutions[this.dataType];

      const params = this.$props
      params.sort = restitution.items[params.fieldName].sort;

      this.$store
        // requete avec les props en parametres de route
        // l'action restitutionCustom est définie dans l'index
        .dispatch('restitutionCustom', params)
        .then(data => {

          // calcul des options du graph
          this.chartOptions = processData(data, this.$props, restitution.items[params.fieldName].text);

          // process terminé
          this.isProcessing = false;
          this.processedProps = null;

        });
    }
  },

  mounted() {
    this.process();
  }
};
</script>
