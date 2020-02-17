import { makeData } from './chart-commons.js';

var makeBarChartOptions = (options, data) => {
    console.log(makeData(options, data))
  const chartOptions = {
    data: makeData(options, data),
    options: {
      legend: {
        display: false,
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

export { makeBarChartOptions };
