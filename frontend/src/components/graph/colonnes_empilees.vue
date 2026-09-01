<template>
  <!--
      Graphique pour afficher les resultats de type custom
    -->

  <!-- par defaut hauteur à 400px et largeur à 100% -->
  <div
    v-if="chartOptions && chartOptions.series && chartOptions.series.length > 0"
    :style="`height:${$props.height || '400px'}; width: ${$props.width || '100%'}`"
  >
    <!-- graphique highchart -->
    <highcharts
      v-if="!isProcessing && chartOptions"
      :options="chartOptions"
      :highcharts="hcInstance"
    ></highcharts>

    <!-- chargement en cours (en attendant les données) -->
    <v-progress-linear
      v-else
      active
      indeterminate
    ></v-progress-linear>
  </div>
</template>

<script>
import Highcharts from 'highcharts';
import exportingInit from 'highcharts/modules/exporting';
import offlineExporting from 'highcharts/modules/offline-exporting';
import { Chart as highcharts } from 'highcharts-vue';

// Modification de highcharts pour permettre l'export des graphiques
exportingInit(Highcharts); // initialise le module export, doit être fait après l'import de highcharts
offlineExporting(Highcharts); // initialise l'export coté client, doit être fait après l'import de highcharts

export default {
  name: 'colonnes_empilees',
  components: { highcharts },
  props: {
    data_db: { default: null },

    fieldGroup: { default: null }, // nom du champ retourné par l'API qui contient les noms des colonnes (ex: "mois" qui contiendra "janvier", "février", etc.)
    field_data: { default: 'data' }, // on essayera de toujours garder "data" dans le données retournées par l'api. Juste là au cas où si ça change.
    values_field: { default: [] }, // valeurs à afficher dans les colonnes (ex: {'nom du bloc': "valeur du bloc"}).
    // Par exemple, si values_field = {'type de bracelet': "nb réalisations"} alors les données dans data doivent etre
    // [{"type de bracelet": "CEFF", "nb réalisations": 10}, {"type de bracelet": "CEM", "nb réalisations": 5}, ...]

    // résumé de la structure attendue des données :
    // data_db = [
    //   {"fieldGroup": "janvier",
    //    data: [
    //      "nom du bloc values_field": "CEFF", "valeur du bloc values_field": 10},
    //      {"nom du bloc values_field": "CEM", "valeur du bloc values_field": 5},
    //      ...
    //    ]
    //   },
    //   {"fieldGroup": "février",
    //    data: [
    //      {"nom du bloc values_field": "CEFF", "valeur du bloc values_field": 8},
    //      {"nom du bloc values_field": "CEM", "valeur du bloc values_field": 3},
    //      ...
    //    ]
    //   },
    //   ...

    title: { default: '' },
    width: { default: '100%' },
    height: { default: '400px' },
    code_couleurs: { default: null }, // objet de la forme { 'nom_champ': 'couleur1', 'nom_champ2': 'couleur2', ... } pour colorer les points en fonction de la valeur d'un champ
  },
  data() {
    return {
      hcInstance: Highcharts, // instance de highcharts à passer au composant highcharts pour éviter les problèmes d'import
      isProcessing: true, // test pour ne pas lancer plusieurs requêtes en même temps

      chartOptions: {
        title: { text: this.$props.title || '' },
        chart: { type: 'column' },
        // animation: true, // active l'animation à chaque mise à jour de la série

        stacking: true,
        xAxis: {
          categories: [],
          labels: {
            formatter: function () {
              const totals =
                this.axis && this.axis.chart && this.axis.chart.options
                  ? this.axis.chart.options.customTotals
                  : [];
              const total = Array.isArray(totals) ? totals[this.pos] || 0 : 0;
              return `${this.value} (${total})`;
            },
          },
        },
        yAxis: {
          min: 0,
          title: { text: 'nb' },
        },

        tooltip: {
          shared: true,
          pointFormat:
            '<span style="color:{point.color}">●</span> {series.name} : <b>{point.y}</b> : {point.percentage:.1f} %<br/>',
        },

        plotOptions: {
          column: {
            allowPointSelect: false, // fige la sélection d'une part du camembert (sinon elle est désactivée par défaut)
            cursor: 'pointer',
            grouping: true,
            stacking: true,
            dataLabels: {
              enabled: true,
              formatter: function () {
                if (!this.y) {
                  return null;
                }
                return `${this.y} `;
              },
              style: {
                fontSize: '1em',
                color: 'white',
                fontWeight: 'bold',
              },
            },
          },
        },

        legend: {
          enabled: true,
          align: 'center',
          verticalAlign: 'bottom',
          layout: 'horizontal',
          labelFormatter: function () {
            const total = this.options && this.options.custom ? this.options.custom.total : 0;
            return `${this.name} (${total})`;
          },
        },

        series: [],
        // colorByPoint: true,

        height: this.$props.height || '600px',
        width: this.$props.width || '600px',
      },
    };
  },

  // on déclenche process à chaque changement de propriété
  watch: {
    $props: {
      handler() {
        this.actualisation_propriete();
      },
      deep: true, // verifie les changements en profondeur des listes/objets de manière récursive
      immediate: true, // lance le handler au montage du composant
    },
  },

  methods: {
    creation_serie_highcharts: (data, props) => {
      /**
       *  création des séries
       */
      if (!Array.isArray(data) || data.length === 0) {
        return { series: [], categories: [] };
      }

      const categories = data.map((item) => item[props.fieldGroup]);
      const seriesMap = new Map();
      const seriesOrder = [];

      data.forEach((item, index) => {
        const rows = Array.isArray(item[props.field_data]) ? item[props.field_data] : [];

        rows.forEach((row) => {
          const name = row[props.values_field[0]] || 'inconnu';
          const value = Number(row[props.values_field[1]] || 0);

          if (!seriesMap.has(name)) {
            seriesMap.set(name, new Array(categories.length).fill(0));
            seriesOrder.push(name);
          }

          const serie = seriesMap.get(name);
          serie[index] += value;
        });
      });

      const series = seriesOrder.map((name) => {
        const serieData = seriesMap.get(name) || [];
        const total = serieData.reduce((acc, value) => acc + Number(value || 0), 0);
        const serie = {
          name,
          data: serieData,
          custom: { total },
        };

        if (props.code_couleurs && props.code_couleurs[name]) {
          serie.color = props.code_couleurs[name];
        }

        return serie;
      });

      return { series, categories };
    },

    actualisation_propriete() {
      this.isProcessing = true;

      const requiredProps = ['data_db'];
      if (requiredProps.some((p) => !this.$props[p])) {
        this.isProcessing = false;
        return;
      }

      // premier affichage ou fallback
      const result = this.creation_serie_highcharts(this.$props.data_db, this.$props);
      this.chartOptions.series = Array.isArray(result.series) ? result.series : [];
      this.chartOptions.xAxis.categories = Array.isArray(result.categories)
        ? result.categories
        : [];
      if (Array.isArray(result.categories) && Array.isArray(this.chartOptions.series)) {
        const totals = result.categories.map((_, index) => {
          return this.chartOptions.series.reduce((acc, serie) => {
            const value = Array.isArray(serie.data) ? Number(serie.data[index] || 0) : 0;
            return acc + value;
          }, 0);
        });
        this.chartOptions.customTotals = totals;
      } else {
        this.chartOptions.customTotals = [];
      }
      this.isProcessing = false;
    },
  },

  mounted() {
    // this.actualisation_propriete();
  },
};
</script>
