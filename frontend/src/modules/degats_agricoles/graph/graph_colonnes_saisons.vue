<template>
  <!--
      Graphique en barres verticales avec les saisons en abscisse.
      Une ou plusieurs séries (barres côte à côte).
    -->
  <div :style="`height:${height}; width:${width}`">
    <highcharts
      :style="`height:${height}; width:${width}`"
      :options="chartOptions"
      :highcharts="hcInstance"
    ></highcharts>
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
  name: 'graph_colonnes_saisons',
  components: { highcharts },
  props: {
    title: { default: '' },
    categories: { default: () => [] }, // noms des saisons, dans l'ordre d'affichage
    // [{ name: 'Surface détruite', data: [12.5, 8, ...], color: '#7cb5ec' }, ...]
    series: { default: () => [] },
    yTitle: { default: '' }, // titre de l'axe des ordonnées
    unite: { default: '' }, // unité ajoutée aux valeurs (ex: 'ha', '€')
    decimales: { default: 0 }, // nombre de décimales affichées
    width: { default: '100%' },
    height: { default: '400px' },
  },
  data: () => ({
    hcInstance: Highcharts, // instance de highcharts à passer au composant highcharts pour éviter les problèmes d'import
  }),
  computed: {
    chartOptions() {
      const decimales = this.decimales;
      const unite = this.unite ? ` ${this.unite}` : '';
      const format = (valeur) => `${Highcharts.numberFormat(valeur, decimales, ',', ' ')}${unite}`;
      return {
        chart: { type: 'column' },
        title: { text: this.title },
        credits: { enabled: false },
        xAxis: {
          categories: this.categories,
          title: { text: 'Saison' },
        },
        yAxis: {
          min: 0,
          title: { text: this.yTitle },
          labels: {
            formatter() {
              return Highcharts.numberFormat(this.value, 0, ',', ' ');
            },
          },
        },
        legend: { enabled: this.series.length > 1 },
        tooltip: {
          shared: true,
          formatter() {
            const lignes = this.points.map(
              (p) =>
                `<span style="color:${p.color}">●</span> ${p.series.name} : <b>${format(p.y)}</b>`
            );
            return [`<b>Saison ${this.x}</b>`, ...lignes].join('<br/>');
          },
        },
        plotOptions: {
          column: {
            dataLabels: {
              enabled: true,
              formatter() {
                return format(this.y);
              },
              style: { fontWeight: 'normal', textOutline: 'none' },
            },
          },
        },
        series: this.series.map((s) => ({ ...s })),
      };
    },
  },
};
</script>
