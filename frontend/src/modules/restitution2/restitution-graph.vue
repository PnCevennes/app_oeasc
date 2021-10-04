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

exportingInit(Highcharts);
offlineExporting(Highcharts);

export default {
  name: "restitution-graph",
  props: [
    "dataType", // type de données (chasse) => quelle api / view est utilisée pour les données
    "fieldName", // quel champs est utilsé pour les rendus²
    "height", // hauteur du composant
    "width", // largeur du composant
    "title", // titre du composant
    "typeGraph", // type de graphique : ['pie', 'bar', 'colmun']
    "filters", // filtres
  ],
  data: () => ({
    chartOptions: null, // option pour le graphique highchart (calculé en fonction des options et des données)
    hcInstance: Highcharts,
    isProcessing: false // test pour ne pas lancer plusieurs requêtes en même temps
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
      if (this.isProcessing) {
          return
      }

      // test sur les champs requis
      const requiredProps = ['fieldName', 'dataType']
      if (requiredProps.some(p => !this[p])) {
        return;
      }

      // debut process
      this.isProcessing = true;

      // configuration de la restitution selon le type
      const restitution = restitutions[this.dataType];

      this.$store
        // requete avec les props en parametres de route
        // l'action restitutionCustom est définie dans l'index
        .dispatch('restitutionCustom', this.$props)
        .then(data => {

          // calcul des options du graph
          this.chartOptions = processData(data, this.$props, restitution);

          // process terminé
          this.isProcessing = false;
        });
    }
  },

  mounted() {
    this.process();
  }
};
</script>
