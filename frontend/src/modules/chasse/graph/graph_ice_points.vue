<template>
  <div>
    <!-- 
      Affiche le graphique si les options du graphique sont définies.
      La hauteur est définie par la prop 'height' ou 400px par défaut.
    -->
    <div
      v-if="chartOptions && chartOptions.series && chartOptions.series.length > 0"
      :style="`height:${$props.height || '400px'}; width: ${$props.width || '100%'}`"
    >
      <!-- 
        Composant Highcharts affiché si le traitement n'est pas en cours.
        Les options et l'instance Highcharts sont passées en props.
      -->
      <highcharts
        v-if="!processing"
        :style="`width:${$props.width || '100%'}; height:${$props.height || '400px'}`"
        :options="chartOptions"
        :highcharts="hcInstance"
      ></highcharts>
      <!-- 
        Affiche une barre de progression si le traitement est en cours.
      -->
      <v-progress-linear
        v-else
        active
        indeterminate
      ></v-progress-linear>
    </div>
    <!-- 
      Snackbar affiché en cas d'erreur, avec un message d'erreur personnalisé.
      Disparaît automatiquement après 5 secondes.
    -->
    <v-snackbar
      color="error"
      v-model="bError"
      :timeout="5000"
    >
      {{ msgError }}
    </v-snackbar>
  </div>
</template>

<script>
import Highcharts from 'highcharts';
import exportingInit from 'highcharts/modules/exporting';
import offlineExporting from 'highcharts/modules/offline-exporting';
import { round } from '@/core/js/util/util.js';
import { dataTxt, localisationTitle } from '../config/util.js';

// Initialise le module d'exportation de Highcharts (permet l'export PNG, PDF, etc. depuis le menu du graphique)
exportingInit(Highcharts);
// Initialise le module d'exportation hors-ligne de Highcharts (permet l'export même sans connexion internet)
offlineExporting(Highcharts);

export default {
  name: 'graphChasseIcePoints',
  props: {
    width: { default: '100%' },
    height: { default: '500px' },
    poids_ou_dagues: { default: true },
    data_db: { default: null },
    filterParams: { default: null },
    do_api_request: { default: false },
  },
  data: () => ({
    // Déclaration de la fonction data qui retourne un objet d'état local du composant
    msgError: null, // Message d'erreur à afficher dans le snackbar en cas de problème lors du chargement des données
    bError: null, // Booléen pour contrôler l'affichage du snackbar d'erreur
    chartOptions: null, // Options du graphique Highcharts générées dynamiquement selon les données reçues
    hcInstance: Highcharts, // Instance de Highcharts utilisée par le composant <highcharts>
    data_api: null, // Données brutes récupérées depuis l'API pour ce graphique, à traiter pour générer les options du graphique
    processing: false, // Booléen indiquant si un traitement (chargement des données) est en cours
  }),

  watch: {
    $props: {
      handler() {
        if (this.$props.do_api_request) {
          this.do_request();
        } else if (this.$props.data_db) {
          this.data_api = this.$props.data_db;
        }
        if (this.data_api) {
          this.process();
        }
      },
      deep: true,
      immediate: true,
    },
  },

  methods: {
    /**
     * Traite les données brutes pour générer les options du graphique.
     */
    process() {
      this.processing = true;

      // res_lm_data contient toutes les valeures des points (res_lm_moy ne contient que les moyennes par jour)
      const dataGraph = this.data_api.res_lm_data;
      if (!dataGraph || !dataGraph.x || dataGraph.x.length === 0) {
        this.chartOptions.series = [];
        this.chartOptions.title.text = `Evolution des ICE - ${this.poids_ou_dagues ? 'Masse Corporelle' : 'Dagues'} - ${this.data_api.nom_espece}${localisationTitle(this.data_api)} (pas de données)`;
        this.processing = false;
        return;
      }
      const { dataTypeAxis, dataTypeTitle, dataTypeSerie } = dataTxt(this.data_api);

      this.chartOptions = {
        title: {
          text: `${dataTypeTitle} / jour - ${this.data_api.nom_espece}${localisationTitle(this.data_api)}`,
        },

        xAxis: {
          title: {
            text: 'Jour',
          },
          labels: {
            enabled: true,
            formatter: function () {
              return `${this.value}`;
            },
          },
        },
        // Configuration de l'axe des Y (valeur de l'ICE ou autre indicateur)
        yAxis: {
          // min, endOnTick, startOnTick peuvent être décommentés pour ajuster l'affichage si besoin
          title: {
            text: dataTypeAxis, // Libellé dynamique selon le type de données (ex: "ICE (kg/ha/jour)")
          },
        },

        series: [
          {
            id: 'pv',
            name: dataTypeSerie,
            lineWidth: 0,
            marker: {
              enabled: true,
              radius: 3,
            },
            states: {
              hover: {
                lineWidthPlus: 0,
              },
            },
            data: Object.keys(dataGraph.x).map((ind) => [dataGraph.x[ind], dataGraph.y[ind]]),
          },
          {
            name: `Regression (p-value=${round(dataGraph.p_value_slope, 3)})`,
            data: [
              [dataGraph.x[0], dataGraph.intercept + dataGraph.x[0] * dataGraph.slope],
              [
                dataGraph.x[dataGraph.x.length - 1],
                dataGraph.intercept + dataGraph.x[dataGraph.x.length - 1] * dataGraph.slope,
              ],
            ],
            dashStyle: dataGraph.p_value_slope < 0.05 ? 'Solid' : 'ShortDash',
            lineWidth: dataGraph.p_value_slope <= 0.1 ? 2 : 0,
            enableMouseTracking: false,
            maxPointWidth: 40,
          },
        ],

        height: this.$props.height,
        width: this.$props.width,
      };

      this.processing = false;
    },

    do_request() {
      // pour le cas de la page indice de performance. La page est créé dynamiquement. Il faut donc faire la requête depuis le component
      // Dans les autres cas on fait la requête en dehors sinon elle sera faite plusieurs fois inutilement
      if (this.$props.filterParams) {
        this.processing = true;
        const filterParams = this.$props.filterParams;
        apiRequest('GET', 'api/chasse/results/ice', {
          params: { ...filterParams, poids_ou_dagues: this.$props.poids_ou_dagues },
        }).then((result) => {
          if (result.error) {
            return;
          }
          this.data_api = result;
          this.process();
        });
      }
    },
  },
  mounted() {
    // this.process();
  },
};
</script>
