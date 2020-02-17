import { makeLegend } from './legend.js';
import { makeScale } from './scale.js';
import { makeData } from './data.js';

var makeChartOptions = (options, dataChart) => {
  var chartOptions = {
    options: {
      plugins: {
        datalabels: {
          color: 'black',
          font: {
            weight: 'bold'
          }
        }
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

  makeLegend(chartOptions, options);
  makeData(chartOptions, dataChart, options);
  makeScale(chartOptions, options);

  return chartOptions;
};

export { makeChartOptions };
