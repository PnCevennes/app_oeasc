/* eslint-disable max-lines-per-function */
import { makeData } from './chart-commons.js';

var makeBarChartOptions = (options, data) => {
  const chartOptions = {
    data: makeData(options, data),
    options: {
      legend: {
        display: data[0].split,
        position: options['label-position']
      },
      plugins: {
        datalabels: {
          color: 'black',
          font: {
            weight: 'bold'
          },
          formatter: (value) => {
            if (value) {
              return value;
            }

            return null;
          }
        }
      },
      scales: {
        xAxes: [
          {
            stacked: options.stacked,
            ticks: {
              //   Display: false //this will remove only the label
            }
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

export { makeBarChartOptions };
