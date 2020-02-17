/* eslint-disable no-negated-condition */
/* eslint-disable no-undefined */
/* eslint-disable no-mixed-operators */
/* eslint-disable max-statements */
/* eslint-disable max-lines-per-function */
/* eslint-disable no-ternary */
/* eslint-disable multiline-ternary */
/* eslint-disable no-magic-numbers */

import { addDays, removeDoublons } from '../util/util.js';
import { Chart } from './chart-commons.js';

var makeDataTime = (options, data) => {
  var datasets = {};
  var labels = removeDoublons(data.map(e => e.date)).sort();
  var dec = 20;
  labels.push(
    addDays(labels[0], -dec),
    addDays(labels[labels.length - 1], dec)
  );
  labels = labels.sort();

  if ('split' in data[0]) {
    const countSplit = {};
    for (const d of data) {
      const key = d.split;
      countSplit[key] = countSplit[key] || 0;
      countSplit[key] += d.value;
    }
    let datasetLabels = data.map(e => e.split);
    datasetLabels = removeDoublons(datasetLabels).sort((a, b) => {
      // Nb declaration decroissant
      const cpt1 = countSplit[b] - countSplit[a];
      // Nom 'split' croissant
      const cpt2 = 2 * (a > b) - 1;

      return cpt1 ? cpt1 : cpt2;
    });
    let i = -1;
    datasets = datasetLabels.map(l => {
      i += 1;

return {
        backgroundColor: Chart.colorschemes.tableau.Tableau10[i],
        data: labels.map(date => {
          var e = data.find(d => d.date === date && d.split === l);
          var y = e ? e.value : 0;

          return {
            x: date,
            y
          };
        }),
        label: l
      };
    });
  } else {
    datasets = [
      {
        backgroundColor: 'red',
        data: data.map(e => ({
          t: e.date,
          y: e.value
        }))
      }
    ];
  }

  return {
    datasets,
    labels
  };
};

var makeTimeChartOptions = (options, data) => {
  const chartOptions = {
    data: makeDataTime(options, data),
    options: {
      legend: {
        display: 'split' in data[0],
        position: 'left'
      },
      plugins: {
        datalabels: {
          color: 'black',
          font: {
            weight: 'bold'
          },
          formatter (value) {
            return value.y ? value.y : '';
          }
        }
      },
      scales: {
        xAxes: [
          {
            stacked: options.stacked,
            time: {
              unit: 'month'
            },
            type: 'time'
          }
        ],
        yAxes: [
          {
            stacked: options.stacked,
            ticks: {
              beginAtZero: true
            }
          }
        ]
      },
      title: {
        display: true,
        text: options.title
      }
    },
    plugins: {
      colorschemes: {
        scheme: options.scheme
      }
    },
    type: options.type
  };

  return chartOptions;
};

export { makeTimeChartOptions };
