import { makeData } from './chart-commons.js';

var makePieChartOptions = (options, data) => {
  const chartOptions = {
    data: makeData(options, data),
    options: {
      legend: {
        display: true,
        position: 'left'
      },
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

  return chartOptions;
};

export { makePieChartOptions };
