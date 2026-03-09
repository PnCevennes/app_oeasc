<template>
    <!--
      Graphique pour afficher les resultats de type custom
    -->

    <!-- par defaut hauteur à 400px et largeur à 100% -->
  <div :style="`height:${height || '400px'}; width: ${width || '100%'}`">

    <!-- graphique highchart -->
    <highcharts
      v-if="!isProcessing && chartOptions" 
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



// Modification de highcharts pour permettre l'export des graphiques
exportingInit(Highcharts); // initialise le module export, doit être fait après l'import de highcharts
offlineExporting(Highcharts); // initialise l'export coté client, doit être fait après l'import de highcharts


export default {
  name: "colonnes_empilees",
  props: {
    data_db: { default: null },

    fieldGroup: { default: null }, // nom du champ retourné par l'API qui contient les noms des colonnes (ex: "mois" qui contiendra "janvier", "février", etc.)
    
    fieldValues: { default: null }, // nom du champ qui contient les valeurs à afficher dans les colonnes (ex: "data" qui contiendra {'nombre d'attributions': 10, 'nombre de réalisations': 5} )
    nameGroup: { default: '' }, // nom à afficher pour le groupe dans la légende (ex: "Type de bracelet") si null ce sera la valeur de fieldGroup
    
    
    title: { default: '' },
    width: { default: '100%' },
    height: { default: '400px' },
    code_couleurs: { default: null } // objet de la forme { 'nom_champ': 'couleur1', 'nom_champ2': 'couleur2', ... } pour colorer les points en fonction de la valeur d'un champ
  },
  data() {
    return {
      hcInstance: Highcharts, // instance de highcharts à passer au composant highcharts pour éviter les problèmes d'import
      isProcessing: true, // test pour ne pas lancer plusieurs requêtes en même temps

      // width/height are props with defaults (see props definition)

      chartOptions: {
        title: { text: this.$props.title || '' },
        chart: { type: 'column' },
        // animation: true, // active l'animation à chaque mise à jour de la série

        stacking: true,
        xAxis: { categories: [] },
        yAxis: {
          min: 0,
          title: { text: "nb" }
        },

        tooltip: {
          shared: true, 
          pointFormat: '<span style="color:{point.color}">●</span> {series.name} : <b>{point.y}</b> : {point.percentage:.1f} %<br/>'

        },

        plotOptions: {

          column: {
            allowPointSelect: false, // fige la sélection d'une part du camembert (sinon elle est désactivée par défaut)
            cursor: 'pointer',
            grouping: true,
            dataLabels: {
              enabled: true,
              format: ' <br> <b style="text-align:center">{point.y}</b> ({point.percentage:.1f} %)',
              style: {
                fontSize: "1em",
                fontWeight: 1,
                color: 'black'
              },
            }
          }
        },

        legend: {
            enabled: false,
            align: 'right',
            verticalAlign: 'middle',
            layout: 'vertical'
        },

        series: [],
        // colorByPoint: true,

        height: this.$props.height || "600px",
        width: "600px"
      }
    };
  },

  // on déclenche process à chaque changement de propriété
  watch: {
    $props: {
      handler() {
        this.actualisation_propriete();
      },
      deep: true, // verifie les changements en profondeur des listes/objets de manière récursive
      immediate: true // lance le handler au montage du composant
    }
  },

  methods: {


    creation_serie_highcharts: (data, props) => {
        /**
         * 
         */
        const series = [];
        const categories = [];
        
    },

    actualisation_propriete() {
      this.isProcessing = true;
      // premier affichage ou fallback
      const result = this.creation_serie_highcharts(this.$props.data_db, this.$props);
      console.log("creation_serie_highcharts result", result);
      this.chartOptions.series = Array.isArray(result.series) ? result.series : [];
      this.chartOptions.xAxis.categories = Array.isArray(result.categories) ? result.categories : [];
      this.isProcessing = false;
    }
  },

  mounted() {
    this.actualisation_propriete();
  }
};
</script>
