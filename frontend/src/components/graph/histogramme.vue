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
  name: "histogramme_comparatif",
  props: {
    data_db: { default: null },
    fieldGroup: { default: null }, // nom du champ retourné par l'API qui contient les noms des groupes (ex: "type_espece" qui contiendra "cerf", "sanglier", etc.)
    listfieldValues: { default: null }, // liste des noms de champs retournés par l'API qui contiennent les valeurs à comparer (ex: ["nb_attributions", "nb_realisations"])
    nameGroup: { default: '' }, // nom à afficher pour le groupe dans la légende (ex: "Type de bracelet")
    listNameValues: { default: null }, // liste des noms à afficher pour les valeurs dans la légende (ex: ["Nombre d'attributions
    title: { default: '' },
    width: { default: '100%' },
    height: { default: '400px' },
    code_couleurs: { default: null } // objet de la forme { 'nom_categorie': 'couleur1', 'nom_categorie2': 'couleur2', ... } pour colorer les points en fonction de la valeur d'un champ
  },
  data() {
    return {
      hcInstance: Highcharts, // instance de highcharts à passer au composant highcharts pour éviter les problèmes d'import
      isProcessing: true, // test pour ne pas lancer plusieurs requêtes en même temps

      // width/height are props with defaults (see props definition)

      chartOptions: {
        title: { text: this.$props.title || '' },
        chart: { type: 'bar' },
        // animation: true, // active l'animation à chaque mise à jour de la série

        stacking: false,
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

          bar: {
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
        if (!Array.isArray(data) || data.length === 0) {
          console.log("creation_serie_highcharts: data is not an array or is empty", data);
          return { categories: [], series: [] };
        }

        const categories = data.map(item => item[props.fieldGroup]);
        console.log("creation_serie_highcharts: categories", categories);


        const series = props.listfieldValues.map((name_field, index ) => {
          console.log("index:", index, ", name_field:", name_field);
          return {
            name: props.listNameValues && props.listNameValues[index] ? props.listNameValues[index] : name_field,
            data: data.map(item2 => {
              return item2[name_field]
            }

            ),
            color: props.code_couleurs && props.code_couleurs[name_field] ? props.code_couleurs[name_field] : undefined
          };
        });
        console.log("creation_serie_highcharts: series", series);

        return { categories, series };
    },

    actualisation_propriete() {
      this.isProcessing = true;
      // test sur les champs requis
      // const requiredProps = ['fieldName', 'fieldValue', 'data_db'];

      // if (requiredProps.some(p => !this.$props[p])) {
      //   return;
      // }

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
      const result = this.creation_serie_highcharts(this.$props.data_db, this.$props);
      console.log("creation_serie_highcharts result", result);
      this.chartOptions.series = Array.isArray(result.series) ? result.series : [];
      this.chartOptions.xAxis.categories = Array.isArray(result.categories) ? result.categories : [];
      this.isProcessing = false;
    }
  },

  mounted() {

    // finalement pas besoin de lancer actualisation_propriete au montage, car le watch sur $props avec immediate: true s'en charge déjà et évite un double appel à la fonction de création de la série
    // this.actualisation_propriete();
  }
};
</script>
