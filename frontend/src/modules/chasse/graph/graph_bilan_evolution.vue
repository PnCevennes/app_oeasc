<template>
  <div>
    <!-- 
      Graphique Highchart spécifique à la chasse. 
      C'est le "bilan d'évolution des plans de chasse" présent dans les analyses détaillées et les bilans de données.
        Est composé d'un histogramme avec les affectations min et max,
        et de courbes pour les réalisations avant novembre et les réalisations totales.
    -->

    <div
      v-if="chartOptions && chartOptions.series && chartOptions.series.length > 0"
      :style="`position: relative; margin-bottom: 40px; height:${$props.height || '400px'}; width: ${$props.width || '100%'}`"
    >
      <!--
        Petit formulaire de date placé à droite de la légende : définit la date de fin (exclue)
        des réalisations représentées par la courbe "Réalisations avant ...". Défaut : 01/11.
      -->
      <div
        class="date-fin-form"
        title="Date de fin (exclue) des réalisations de la courbe verte"
      >
        <span class="date-fin-label">Date de la courbe verte : avant le</span>
        <v-select
          v-model="jourFin"
          :items="jours"
          density="compact"
          variant="outlined"
          hide-details
          class="date-fin-select"
        ></v-select>
        <v-select
          v-model="moisFin"
          :items="mois"
          item-title="title"
          item-value="value"
          density="compact"
          variant="outlined"
          hide-details
          class="date-fin-select date-fin-select-mois"
        ></v-select>
      </div>
      <!-- 
        Composant Highcharts affiché si le traitement n'est pas en cours.
        Les options et l'instance Highcharts sont passées en props.
      -->
      <highcharts
        v-if="!processing && data_bilan && chartOptions"
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
import Highcharts, { Chart as highcharts } from '@/core/js/highcharts.js';
import { apiRequest } from '../../../core/js/data/api.js';
import { localisationTitle } from '../config/util.js';

export default {
  name: 'graph_bilan_evolution',
  components: { highcharts },
  props: {
    bilanParams: { type: Object, default: () => ({}) }, // Paramètres de filtrage pour récupérer les données du bilan d'évolution
    height: { type: String, default: '400px' }, // Hauteur du graphique
    width: { type: String, default: '100%' }, // Largeur du graphique
  },

  data: () => ({
    // Déclaration de la fonction data qui retourne un objet d'état local du composant
    msgError: null, // Message d'erreur à afficher dans le snackbar en cas de problème lors du chargement des données
    bError: null, // Booléen pour contrôler l'affichage du snackbar d'erreur
    hcInstance: Highcharts, // Instance de Highcharts utilisée par le composant <highcharts>
    data_bilan: null, // Données du bilan d'évolution des plans de chasse récupérées depuis l'API
    processing: false, // Booléen indiquant si un traitement (chargement des données) est en cours
    jourFin: 1, // Jour de la date de fin des réalisations "avant novembre" (défaut 01/11)
    moisFin: 11, // Mois de la date de fin
    jours: Array.from({ length: 31 }, (_, i) => i + 1),
    mois: [
      'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet',
      'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre',
    ].map((title, i) => ({ title, value: i + 1 })),
    chartOptions: null, // Options de configuration du graphique Highcharts, générées dynamiquement en fonction des données récupérées
  }),

  computed: {
    // Date de fin au format MM-JJ attendu par l'API
    dateFinParam() {
      const pad = (n) => String(n).padStart(2, '0');
      return `${pad(this.moisFin)}-${pad(this.jourFin)}`;
    },
    // Libellé de la série, ex : "Réalisations avant le 01/11"
    labelAvant() {
      const pad = (n) => String(n).padStart(2, '0');
      return `Réalisations avant le ${pad(this.jourFin)}/${pad(this.moisFin)}`;
    },
  },

  watch: {
    jourFin() {
      this.recuperation_data_bilan();
    },
    moisFin() {
      this.recuperation_data_bilan();
    },
    $props: {
      handler() {
        this.recuperation_data_bilan();
      },
      deep: true,
      immediate: true,
    },
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

      this.chartOptions = {
        // Options du graphique Highcharts générées dynamiquement selon les données reçues
        title: {
          text: `Évolution des plans de chasse - ${data.nom_espece}${localisationTitle(data)}.`,
        },
        xAxis: {
          title: {
            text: 'Saisons',
          },
          labels: {
            enabled: true,
            formatter: function () {
              return data.nb_realisation[this.value][0];
            },
          },
        },
        yAxis: {
          title: {
            text: 'Réalisation',
          },
        },
        tooltip: {
          xDateFormat: '%d/%m/%Y',
          shared: true,
          split: false,
          enabled: true,
        },
        legend: {
          // laisse la place au formulaire de date à droite de la légende
          align: 'left',
          width: '70%',
        },
        series: [
          {
            type: 'column',
            name: 'Affectation min',
            data: data.nb_attribution_min,
          },
          {
            type: 'column',
            name: 'Affectation max',
            data: data.nb_attribution_max,
          },
          {
            name: this.labelAvant,
            data: data.nb_realisation_avant_11,
          },
          {
            name: 'Réalisations',
            data: data.nb_realisation,
            dataLabels: {
              enabled: true,
            },
          },
        ],
        height: this.$props.height,
        width: this.$props.width,
      };
    },

    recuperation_data_bilan() {

      this.processing = true;
      if (!this.bilanParams.id_espece) {
        this.bilanParams.id_espece = 1; // om met les CERFS par défaut
      }
      apiRequest('GET', 'api/chasse/results/bilan', { params: { ...this.bilanParams, date_fin_realisation: this.dateFinParam } }).then((result) => {
        this.data_bilan = result;
        this.maj_chartOptions();
        this.processing = false;
      });
    },
  },
  mounted() {
    // pas besoin de récupérer les données à l'initialisation, le watcher sur les props s'en charge et est déclenché immédiatement grâce à immediate: true
  },
};
</script>

<style scoped>
.date-fin-form {
  position: absolute;
  right: 8px;
  bottom: 4px;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
}
.date-fin-select {
  width: 75px;
  flex: none;
}
.date-fin-select-mois {
  width: 130px;
}
.date-fin-form :deep(.v-field__input) {
  font-size: 0.8rem;
  min-height: 30px;
  padding: 2px 6px;
}
.date-fin-form :deep(.v-field) {
  --v-input-control-height: 30px;
}
</style>
