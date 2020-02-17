/* eslint-disable no-magic-numbers */
/* eslint-disable prefer-destructuring */
import { Chart } from 'chart.js';
import 'chartjs-plugin-colorschemes';
import 'chartjs-plugin-datalabels';


var generateBarLegendLabels = (chart) => {
    var labels = chart.data.labels;
    var dataset = chart.data.datasets[0];
    // Var dataset = chart.data.datasets[0];

    const legend = labels.map((label, index) => ({
        datasetIndex: 0,
        fillStyle: dataset.backgroundColor && dataset.backgroundColor[index],
        lineWidth: dataset.borderWidth,
        strokeStyle: dataset.borderColor && dataset.borderColor[index],
        text: label
      }));

return legend;
  }

var makeData = (options, data) => ({
    datasets: [
      {
        backgroundColor: Chart.colorschemes.tableau.Tableau10,
        data: data.map(e => e.value),
      }
    ],
    labels: data.map(e => e.label),
  });

export { Chart, generateBarLegendLabels, makeData }
