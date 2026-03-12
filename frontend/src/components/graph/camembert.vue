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

// Modification de highcharts pour permettre l'export des graphiques
exportingInit(Highcharts); // initialise le module export, doit être fait après l'import de highcharts
offlineExporting(Highcharts); // initialise l'export coté client, doit être fait après l'import de highcharts

export default {
  name: 'camembert',
  props: {
    data_db: { default: null },
    fieldName: { default: null },
    fieldValue: { default: null },
    title: { default: '' },
    width: { default: '100%' },
    height: { default: '400px' },
    code_couleurs: { default: null }, // objet de la forme { 'nom_categorie': 'couleur1', 'nom_categorie2': 'couleur2', ... } pour colorer les points en fonction de la valeur d'un champ
  },
  data() {
    return {
      hcInstance: Highcharts, // instance de highcharts à passer au composant highcharts pour éviter les problèmes d'import
      isProcessing: true, // test pour ne pas lancer plusieurs requêtes en même temps

      chartOptions: {
        title: { text: this.$props.title || '' },
        chart: { type: 'pie' },
        // animation: true, // active l'animation à chaque mise à jour de la série
        stacking: false,
        xAxis: { categories: [] },
        yAxis: {
          min: 0,
          title: { text: 'nb' },
        },

        tooltip: {
          pointFormat: '<b>{point.y}</b>: {point.percentage:.1f} %',
        },

        plotOptions: {
          pie: {
            allowPointSelect: false, // fige la sélection d'une part du camembert (sinon elle est désactivée par défaut)
            cursor: 'pointer',
            dataLabels: {
              enabled: true,
              format:
                '<b>{point.name}:</b> <br> <b style="text-align:center">{point.y}</b> ({point.percentage:.1f} %)',
              style: {
                fontSize: '1em',
                fontWeight: 1,
                color: 'black',
              },
            },
            showInLegend: false, // affiche les catégories dans la légende à côté du camembert (sinon elles sont
          },
        },

        legend: {
          enabled: false,
          align: 'right',
          verticalAlign: 'middle',
          layout: 'vertical',
        },

        series: [],
        colorByPoint: true,

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
       * transformation de data_db en serie bien formatée pour highcharts
       * sous la forme :
       */
      const total = data.reduce((p, c) => {
        return p + c[props.fieldValue];
      }, 0);
      let serie = {
        name: props.title || '',
        animation: true,
        data: data.map((d) => {
          return {
            name: `<b>${d[props.fieldName]}</b>`,
            useHTML: true,
            y: d[props.fieldValue],
            color: props.code_couleurs ? props.code_couleurs[d[props.fieldName]] : undefined,
          };
        }),
      };

      return serie;
    },

    actualisation_propriete() {
      // test sur les champs requis
      this.isProcessing = true;
      const requiredProps = ['fieldName', 'fieldValue', 'data_db'];

      if (requiredProps.some((p) => !this.$props[p])) {
        this.isProcessing = false;
        return;
      }

      const newSeries = [this.creation_serie_highcharts(this.$props.data_db, this.$props)];

      // si le chart existe déjà, on utilise l'API update pour forcer l'animation
      // try {
      //   if (this.$refs.hc && this.$refs.hc.chart) {
      //     // update(options, redraw=true, oneToOne=true)
      //     this.$refs.hc.chart.update({ series: newSeries }, true, true);
      //     return;
      //   }
      // } catch (e) {
      //   // si update échoue, on retombe sur l'affectation classique
      //   console.warn('Highcharts update failed:', e);
      // }

      // premier affichage ou fallback
      this.chartOptions.series = newSeries;
      this.isProcessing = false;
    },
  },

  mounted() {
    this.actualisation_propriete();
  },
};
</script>
