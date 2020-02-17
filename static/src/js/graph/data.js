/* eslint-disable no-ternary */
/* eslint-disable no-magic-numbers */
import { removeDoublons } from '../util/util.js';
import { Chart } from './chart-commons.js'


var makeDataTime = (dataChart, options) => {

  var labels = removeDoublons(dataChart.map(e => e.date));
  var datasets = {};
  if (options.split) {
    let datasetLabels = dataChart.map(e => e[options.split]).sort();
    datasetLabels = removeDoublons(datasetLabels);
    let i = -1;
    datasets = datasetLabels.map(l => {
      // eslint-disable-next-line no-magic-numbers
      i += 1;

      return {
        backgroundColor: Chart.colorschemes.tableau.Tableau10[i],
        data: labels.map(date => {
          // Console.log(date, l)
          var e = dataChart.find(d => d.date === date && d[options.split] === l);
          var y = e
            ? e.value
            : 0;

          return {
            x: date,
            y
          };
        }),
        label: l,
      };
    });
  } else {
    datasets = [
      {
        backgroundColor: 'red',
        data: dataChart.map(e => ({
          t: e.date,
          y: e.value
        })),
      }
    ];
  }

  return {
    datasets,
    labels
  };
};

var makeData = (chartOptions, dataChart, options) => {
  switch (options.util) {
    case 'time':
      chartOptions.data = makeDataTime(dataChart, options);

      chartOptions.options.plugins.datalabels = {
        display: false
      };
      break;
    default:
      chartOptions.data = {
        datasets: [
          {
            backgroundColor: Chart.colorschemes.tableau.Tableau10,
            data: dataChart.map(e => e.value),
          }
        ],
        labels: dataChart.map(e => e.label),
      };
      break;
  }
};

export { makeData };
