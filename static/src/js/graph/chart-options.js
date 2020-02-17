import { makeBarChartOptions } from './bar.js';
import { makePieChartOptions } from './pie.js';
import { makeLineChartOptions } from './line.js';
import { makeTimeChartOptions } from './time.js';

var makeChartOptions = (options, data) => {
  var chartOptions = {};

  if (options.util === 'time') {
    chartOptions = makeTimeChartOptions(options, data);

    return chartOptions;
  }

  switch (options.type) {
    case 'bar':
      chartOptions = makeBarChartOptions(options, data);
      break;
    case 'pie':
      chartOptions = makePieChartOptions(options, data);
      break;
    case 'line':
      chartOptions = makeLineChartOptions(options, data);
      break;
    default:
  }

  return chartOptions;
};

/*
 * C  var chartOptions = {
 *     options: {
 *       plugins: {
 *         datalabels: {
 *           color: 'black',
 *           font: {
 *             weight: 'bold'
 *           }
 *         }
 *       },
 *       title: {
 *         display: true,
 *         text: options.title
 *       }
 *     },
 *     plugins: {
 *       colorschemes: {
 *         scheme: options.scheme
 *       }
 *     },
 *     type: options.type
 *   };
 */

/*
 *   MakeLegend(chartOptions, options);
 *   makeData(chartOptions, dataChart, options);
 *   makeScale(chartOptions, options);
 */

/*
 *   Return chartOptions;
 * };
 */

export { makeChartOptions };
