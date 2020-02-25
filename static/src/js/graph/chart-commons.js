/* eslint-disable max-lines-per-function */
/* eslint-disable no-ternary */
/* eslint-disable multiline-ternary */
/* eslint-disable no-negated-condition */
/* eslint-disable max-statements */
/* eslint-disable no-magic-numbers */
/* eslint-disable prefer-destructuring */
import { Chart } from 'chart.js';
import 'chartjs-plugin-colorschemes';
import 'chartjs-plugin-datalabels';
import { removeDoublons } from '../util/util.js';


var generateBarLegendLabels = chart => {
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
};

var makeData = (options, data) => {
  var datasets = {};
  var labels = removeDoublons(data.map(e => e.label));
  if (!data[0].split) {
    datasets = [
      {
        backgroundColor: Chart.colorschemes.tableau.Tableau10,
        data: data.map(e => e.value)
      }
    ];
  } else {
    const countSplit = {};
    for (const d of data) {
      const key = d.split;
      countSplit[key] = countSplit[key] || 0;
      countSplit[key] += d.value;
    }
    let datasetLabels = data.map(e => e.split);
    datasetLabels = removeDoublons(datasetLabels)
    // .sort((a, b) => {
    //   // Nb declaration decroissant
    //   const cpt1 = countSplit[b] - countSplit[a];
    //   // Nom 'split' croissant
    //   const cpt2 = 2 * (a > b) - 1;

    //   return cpt1 ? cpt1 : cpt2;
    // });
    let i = -1;
    datasets = datasetLabels.map(l => {
      i += 1;

      return {
        backgroundColor: Chart.colorschemes.tableau.Tableau10[i],
        data: labels.map(label => {
          var e = data.find(d => d.label === label && d.split === l);
          var value = e ? e.value : 0;

          return value;
        }),
        label: l
      };
    });
  }

  return {
    datasets,
    labels
  };
};

export { Chart, generateBarLegendLabels, makeData };
