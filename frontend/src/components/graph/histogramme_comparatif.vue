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
/**======================================================================================================
 *    HISTOGRAMME HORIZONTAL COMPARATIF
 *    ATTENTION: histogramme un peu spécial. Il est conçu pour comparer des valeurs par rapport à
 *    une valeur de référence (ex: nombre de réalisations par rapport au nombre d'attributions). la
 *    valeur de référence sera toujours à 100% et les autres valeurs seront calculées en pourcentage
 *    de cette référence.
 *    Pour l'instant utilisé pour comparer le nombre de réalisations faites par rapport au nombre d'attributions, mais peut être réutilisé pour d'autres comparaisons du même type.
 *    Propriétés spécifiques:
 *    - fieldReference: nom du champ qui contient les valeurs de référence à comparer (ex: "nb_attributions")
 *    - listfieldValues: liste des noms de champs retournés par l'API qui contiennent les valeurs à comparer (ex: ["nb_attributions", "nb_truc"])
 *    - nameReference: nom à afficher pour la valeur de référence dans la légende (ex: "Nombre d'attributions")
 *    - nameGroup: nom à afficher pour le groupe dans la légende (ex: "Type de bracelet")
 *    - listNameValues: liste des noms à afficher pour les valeurs dans la légende (ex: ["Nombre d'attributions", "Nombre de trucs"])
 *    - code_couleurs: objet de la forme { 'nom_categorie': 'couleur1', 'nom_categorie2': 'couleur2', ... } pour colorer les points en fonction de la valeur d'un champ
 *
 * ======================================================================================================
 *  */

import Highcharts from 'highcharts';
import exportingInit from 'highcharts/modules/exporting';
import offlineExporting from 'highcharts/modules/offline-exporting';

// Modification de highcharts pour permettre l'export des graphiques
exportingInit(Highcharts); // initialise le module export, doit être fait après l'import de highcharts
offlineExporting(Highcharts); // initialise l'export coté client, doit être fait après l'import de highcharts

export default {
  name: 'histogramme_comparatif',
  props: {
    data_db: { default: null },
    fieldGroup: { default: null },
    fieldReference: { default: null }, // nom du champ qui contient les valeurs de référence à comparer (ex: "nb_attributions")
    listfieldValues: { default: null }, // liste des noms de champs retournés par l'API qui contiennent les valeurs à comparer (ex: ["nb_attributions", "nb_truc"])
    nameGroup: { default: '' }, // nom à afficher pour le groupe dans la légende (ex: "Type de bracelet")
    nameReference: { default: 'références' }, // nom à afficher pour la valeur de référence dans la légende (ex: "Nombre d'attributions")
    listNameValues: { default: null }, // liste des noms à afficher pour les valeurs dans la légende (ex: ["Nombre d'attributions", "Nombre de trucs"])
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
        chart: { type: 'bar' },
        animation: true, // active l'animation à chaque mise à jour de la série

        stacking: false,
        xAxis: { categories: [] },
        yAxis: {
          min: 0,
          title: { text: 'nb' },
        },

        tooltip: {
          shared: true,
          formatter: function () {
            const points = this.points || (this.point ? [this.point] : []);
            const visiblePoints = points.filter((p) => !p.series.userOptions.hideInTooltip);

            if (visiblePoints.length === 0) {
              return false;
            }

            let s = `<b>${this.x}</b><br/>`;
            const chart =
              this.points && this.points[0] && this.points[0].series && this.points[0].series.chart
                ? this.points[0].series.chart
                : null;
            const referenceLabel =
              chart && chart.options && chart.options.custom && chart.options.custom.referenceLabel
                ? chart.options.custom.referenceLabel
                : 'références';

            visiblePoints.forEach((p) => {
              s += `<span style="color:${p.color}">●</span> ${p.series.name} : <b>${p.y}</b> (${Highcharts.numberFormat(p.point.percentage, 1)} %) — sur <b>${p.point.stackTotal}</b> ${referenceLabel}<br/>`;
            });
            return s;
          },
        },

        plotOptions: {
          series: {
            stacking: 'normal',
          },
          bar: {
            allowPointSelect: false, // fige la sélection d'une part du camembert (sinon elle est désactivée par défaut)
            cursor: 'pointer',
            grouping: true,
            dataLabels: {
              enabled: true,
              formatter: function () {
                if (this.series.userOptions.hideDataLabels) {
                  return null;
                }
                return `<b style="text-align:center">${this.y} (${Highcharts.numberFormat(this.percentage, 1)} %)</b>`;
              },
              style: {
                fontSize: '1em',
                fontWeight: 1,
                color: 'white',
              },
            },
          },
        },

        legend: {
          enabled: false,
          align: 'right',
          verticalAlign: 'middle',
          layout: 'vertical',
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
       *
       */
      if (!Array.isArray(data) || data.length === 0) {
        return { categories: [], series: [] };
      }

      const categories = data.map((item) => item[props.fieldGroup]);

      const hasReference =
        typeof props.fieldReference === 'string' && props.fieldReference.trim() !== '';
      const hasValues = Array.isArray(props.listfieldValues) && props.listfieldValues.length > 0;

      let series = [];

      if (hasReference && hasValues) {
        const restantName = 'Restant';
        const referenceName = props.nameReference || props.fieldReference;

        const compareSeries = props.listfieldValues.map((name_field, index) => {
          const label =
            props.listNameValues && props.listNameValues[index]
              ? props.listNameValues[index]
              : name_field;
          return {
            name: label,
            data: data.map((item2) => Number(item2[name_field] || 0)),
            color:
              props.code_couleurs && props.code_couleurs[name_field]
                ? props.code_couleurs[name_field]
                : undefined,
          };
        });

        const restantSeries = {
          name: restantName,
          data: data.map((item2) => {
            const total = Number(item2[props.fieldReference] || 0);
            const sumValues = props.listfieldValues.reduce((acc, field) => {
              return acc + Number(item2[field] || 0);
            }, 0);
            return Math.max(total - sumValues, 0);
          }),
          hideInTooltip: true,
          hideDataLabels: true,
          color:
            props.code_couleurs &&
            (props.code_couleurs.restant || props.code_couleurs[props.fieldReference])
              ? props.code_couleurs.restant || props.code_couleurs[props.fieldReference]
              : undefined,
        };

        series = [restantSeries, ...compareSeries];
      } else {
        series = props.listfieldValues.map((name_field, index) => {
          return {
            name:
              props.listNameValues && props.listNameValues[index]
                ? props.listNameValues[index]
                : name_field,
            data: data.map((item2) => {
              return item2[name_field];
            }),
            color:
              props.code_couleurs && props.code_couleurs[name_field]
                ? props.code_couleurs[name_field]
                : undefined,
          };
        });
      }

      return { categories, series };
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
      this.chartOptions.custom = {
        referenceLabel: this.$props.nameReference || this.$props.fieldReference || 'référence',
      };
      this.isProcessing = false;
    },
  },

  mounted() {
    // finalement pas besoin de lancer actualisation_propriete au montage, car le watch sur $props avec immediate: true s'en charge déjà et évite un double appel à la fonction de création de la série
    // this.actualisation_propriete();
  },
};
</script>
