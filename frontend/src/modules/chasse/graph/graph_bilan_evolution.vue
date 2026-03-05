<template>
  <div>
    <!-- 
      Graphique Highchart spécifique à la chasse. 
      C'est le "bilan d'évolution des plans de chasse" présent dans les analyses détaillées et les bilans de données.
        Est composé d'un histogramme avec les affectations min et max,
        et de courbes pour les réalisations avant novembre et les réalisations totales.
    -->


    <div
      v-if="chartOptions"
      :style="`height:${height || '400px'}; width: ${width || '100%'}`"
    >
      <!-- 
        Composant Highcharts affiché si le traitement n'est pas en cours.
        Les options et l'instance Highcharts sont passées en props.
      -->
      <highcharts
        v-if="!processing && data_bilan && chartOptions"
        :style="`width:${width || '100%'}; height:${height || '400px'}`"
        :options="chartOptions"
        :highcharts="hcInstance"
      ></highcharts>
      <!-- 
        Affiche une barre de progression si le traitement est en cours.
      -->
      <v-progress-linear v-else active indeterminate></v-progress-linear>
    </div>
    <!-- 
      Snackbar affiché en cas d'erreur, avec un message d'erreur personnalisé.
      Disparaît automatiquement après 5 secondes.
    -->
    <v-snackbar color="error" v-model="bError" :timeout="5000">
      {{ msgError }}
    </v-snackbar>
  </div>
</template>

<script>
import Highcharts, { chart } from "highcharts";
import exportingInit from "highcharts/modules/exporting";
import offlineExporting from "highcharts/modules/offline-exporting";
import { apiRequest } from "../../../core/js/data/api.js";
import { localisationTitle } from '../config/util.js'

// Initialise le module d'exportation de Highcharts (permet l'export PNG, PDF, etc. depuis le menu du graphique)
exportingInit(Highcharts);
// Initialise le module d'exportation hors-ligne de Highcharts (permet l'export même sans connexion internet)
offlineExporting(Highcharts);

export default {
  name: "graph_bilan_evolution",
  props: {
    bilanParams: { type: Object, default: () => ({}) }, // Paramètres de filtrage pour récupérer les données du bilan d'évolution
    },

  data: () => ({ // Déclaration de la fonction data qui retourne un objet d'état local du composant
    msgError: null, // Message d'erreur à afficher dans le snackbar en cas de problème lors du chargement des données
    bError: null, // Booléen pour contrôler l'affichage du snackbar d'erreur
    hcInstance: Highcharts, // Instance de Highcharts utilisée par le composant <highcharts>
    data_bilan: null, // Données du bilan d'évolution des plans de chasse récupérées depuis l'API
    processing: false, // Booléen indiquant si un traitement (chargement des données) est en cours
    height: "400px", // Hauteur par défaut du graphique
    width: "100%", // Largeur par défaut du graphique
    chartOptions: null // Options de configuration du graphique Highcharts, générées dynamiquement en fonction des données récupérées
  }),
  

  watch: {
    $props: {
      handler() {
        this.recuperation_data_bilan();
      },
      deep: true,
      immediate: true
    }
  },

  
  methods: {

    maj_chartOptions() {
      if (!this.data_bilan) {
        return;
      }

      const data = this.data_bilan;

      // Traitement des données pour construire les options du graphique Highcharts
      // (extraction des séries, catégories, etc. à partir de this.data_bilan)
      // ...

      this.chartOptions = {  // Options du graphique Highcharts générées dynamiquement selon les données reçues
            title: {
              text: `Évolution des plans de chasse - ${data.nom_espece}${localisationTitle(data)}.`
            },
            xAxis: {
                title: {
                text: "Saisons"
                },
                labels: {
                enabled: true,
              formatter: function() {
                return (
                data.nb_realisation[this.value][0]
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
            tooltip: {
                xDateFormat: '%d/%m/%Y',
                shared: true,
                split: false,
                enabled: true
            },
            series: [
                {
                type: "column",
                name: "Affectation min",
                data: data.nb_attribution_min,
                },
                {
                type: "column",
                name: "Affectation max",
                data: data.nb_attribution_max,
                },
                {
                name: "Réalisations avant novembre",
                data: data.nb_realisation_avant_11,
                },
                {
                name: "Réalisations",
                data: data.nb_realisation,
                dataLabels: {
                    enabled: true
                }
                }
            ],
            height: "600px",
            width: "600px"
        }
    },

    recuperation_data_bilan() {
        // 

        this.processing = true;
        // console.log("Récupération des données du bilan d'évolution avec les paramètres suivants : ", this.bilanParams);
        if (!this.bilanParams.id_espece){
            this.bilanParams.id_espece = 1; // om met les CERFS par défaut
        }
        apiRequest("GET", 'api/chasse/results/bilan',  { params: this.bilanParams }) 
            .then(result => {
                this.data_bilan = result;
                // console.log("data_bilan_evolution", this.data_bilan);
                this.maj_chartOptions();
                this.processing = false;
            });
    }
  },
  mounted() {
    // pas besoin de récupérer les données à l'initialisation, le watcher sur les props s'en charge et est déclenché immédiatement grâce à immediate: true
    // this.recuperation_data_bilan();
  }
};
</script>

