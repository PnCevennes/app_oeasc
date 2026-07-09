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
import Highcharts, { color } from 'highcharts';
import exportingInit from 'highcharts/modules/exporting';
import offlineExporting from 'highcharts/modules/offline-exporting';

// Modification de highcharts pour permettre l'export des graphiques
exportingInit(Highcharts); // initialise le module export, doit être fait après l'import de highcharts
offlineExporting(Highcharts); // initialise l'export coté client, doit être fait après l'import de highcharts

export default {
  compatConfig: { MODE: 3 }, // verrouille les acquis Phase 4 (composant testé sans warning au 2026-07-10)
  name: 'graph_lignes_multiples',
  props: {
    data_db: { default: null }, // données à afficher
    field_x: { default: null }, // nom du champ à utiliser pour les catégories de l'axe x
    field_y: { default: null }, // nom du champ à utiliser pour les valeurs de l'axe y
    fields_line: { default: null }, // nom du champ à utiliser pour différencier les lignes (une ligne par valeur de ce champ)
    title: { default: '' },
    colors: { default: null }, // objet de la forme { 'valeur1': 'couleur1', 'valeur2': 'couleur2', ... } pour colorer les points en fonction de la valeur d'un champ
    width: { default: '100%' },
    height: { default: '400px' },
  },
  data() {
    return {
      hcInstance: Highcharts, // instance de highcharts à passer au composant highcharts pour éviter les problèmes d'import
      isProcessing: false, // test pour ne pas lancer plusieurs requêtes en même temps

      chartOptions: {
        title: { text: this.$props.title || '' },
        chart: { type: 'line' },

        stacking: true,
        xAxis: { categories: [] }, // les catégories de l'axe x seront définies dynamiquement en fonction des données récupérées, à partir du champ spécifié dans field_x
        yAxis: {
          // min: 0, --- IGNORE ---
          min: 0,
          title: { text: 'nb' },
        },

        tooltip: {
          // la vignette qui s'affiche au survol d'un point du graphique
          enabled: true,
          useHTML: true,
          colorByPoint: true, // permet de colorer la vignette avec la même couleur que le point survolé
          formatter: function () {
            // this.point: le point survolé
            // this.point.series: la série (ligne)
            // this.point.x: index de la catégorie (colonne)
            const point = this.point || this;
            const chart = point.series && point.series.chart;
            const xIndex = point.x;

            // nom de la colonne (catégorie x)
            const columnName =
              (chart &&
                chart.xAxis &&
                chart.xAxis[0] &&
                chart.xAxis[0].categories &&
                chart.xAxis[0].categories[xIndex]) ||
              point.category ||
              '';

            // total de la colonne: somme des y de chaque série pour cet index
            // let totalCol = 0;
            // if (chart && Array.isArray(chart.series)) {
            //   chart.series.forEach(s => {
            //     if (!s || !s.data) return;
            //     const cell = s.data[xIndex];
            //     if (cell == null) return;
            //     if (typeof cell === 'number') {
            //       totalCol += cell;
            //     } else if (typeof cell.y === 'number') {
            //       totalCol += cell.y;
            //     }
            //   });
            // }

            // nom de la ligne (série) et total de la ligne (si présent dans les options sinon somme)
            const lineName = (point.series && point.series.name) || '';
            let totalLine = null;
            if (
              point.series &&
              point.series.options &&
              typeof point.series.options.total_ligne === 'number'
            ) {
              totalLine = point.series.options.total_ligne;
            } else if (point.series && Array.isArray(point.series.data)) {
              totalLine = point.series.data.reduce(
                (s, p) => s + (p && typeof p.y === 'number' ? p.y : 0),
                0
              );
            }

            const pointValue = typeof point.y === 'number' ? point.y : point.y || '';

            return `<span >${columnName}</span> <br> <span>${lineName} (${totalLine})</span> - <span style="color:#000; font-weight:bold">${pointValue}</span>`;
          },
        },

        plotOptions: {
          line: {
            allowPointSelect: false, // fige la sélection d'une part du camembert (sinon elle est désactivée par défaut)
            cursor: 'pointer',
            dataLabels: {
              // les labels affichés à côté de chaque point du graphique
              enabled: false,
              format: '<b>{point.name}:</b> <br> <b style="text-align:center">{point.y}</b>',
              style: {
                fontSize: '1em',
                fontWeight: 1,
                color: 'black',
              },
            },
            showInLegend: true, // affiche les catégories dans la légende à côté du camembert (sinon elles sont affichées dans les labels des points)
          },
        },

        legend: {
          // la légende du graphique, qui affiche les différentes catégories de lignes (une ligne par valeur du champ spécifié dans fields_line)
          enabled: true,
          align: 'center',
          verticalAlign: 'bottom',
          layout: 'horizontal',
          itemStyle: {
            fontSize: '1em',
            fontWeight: 1,
          },
          // Affiche le total de la ligne entre parenthèses à côté du nom
          labelFormatter: function () {
            // this est la série ici; preferer this.options.total_ligne si renseigné
            let total = 0;
            if (this.options && typeof this.options.total_ligne === 'number') {
              total = this.options.total_ligne;
            } else if (Array.isArray(this.data)) {
              total = this.data.reduce((s, p) => {
                if (p == null) return s;
                if (typeof p === 'number') return s + p;
                if (typeof p.y === 'number') return s + p.y;
                return s;
              }, 0);
            }
            return `${this.name} (${total})`;
          },
        },

        dataLabels: {
          //
          style: {
            fontSize: '1em',
            fontWeight: 1,
            color: 'black',
          },
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
    creation_serie_highcharts(data_db) {
      /**
       * transformation de data_db en serie bien formatée pour highcharts
       * sous la forme :
       */

      // validate input
      if (!Array.isArray(data_db) || data_db.length === 0) {
        return { months: [], series: [] };
      }

      // find first valid saison with data
      const first = data_db.find((s) => s && Array.isArray(s.data) && s.data.length);
      if (!first) {
        return { months: [], series: [] };
      }

      // 1. Récupérer les mois (une seule fois)
      const months = first.data.map((item) => item[this.$props.field_x]);

      // 2. Construire les séries
      const series = data_db.map((saison) => ({
        name: saison[this.$props.fields_line] || '',
        total_ligne: saison.data.reduce((sum, item) => sum + (item[this.$props.field_y] || 0), 0),
        data: Array.isArray(saison.data)
          ? saison.data.map((item) => item[this.$props.field_y] || 0)
          : [],
      }));

      // 3. Calculer le total par colonne et injecter dans Highcharts
      const totalsPerColumn = months.map((m, idx) =>
        series.reduce((s, serie) => {
          const v = Array.isArray(serie.data) ? serie.data[idx] : undefined;
          if (v == null) return s;
          if (typeof v === 'number') return s + v;
          if (typeof v.y === 'number') return s + v.y;
          return s;
        }, 0)
      );

      const labeledMonths = months.map((m, idx) => `${m} (${totalsPerColumn[idx]})`);

      this.chartOptions.xAxis.categories = labeledMonths;
      this.chartOptions.series = series;

      return { months, series };
    },

    actualisation_propriete() {
      // test sur les champs requis
      const requiredProps = ['data_db'];
      if (requiredProps.some((p) => !this.$props[p])) {
        this.isProcessing = false;
        return;
      }

      const result = this.creation_serie_highcharts(this.$props.data_db);

      // premier affichage ou fallback: appliquer la série formatée (ou vide)
      if (result && Array.isArray(result.series)) {
        this.chartOptions.series = result.series;
      } else {
        this.chartOptions.series = [];
      }

      this.chartOptions.title.text = this.$props.title || '';
      this.isProcessing = false;
    },
  },

  mounted() {
    // this.actualisation_propriete();
  },
};
</script>
