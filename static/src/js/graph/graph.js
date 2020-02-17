import { htmlToElement } from '../util/util.js';
import { makeChartOptions } from './chart-options.js';
import { Chart } from './import-chart.js'

var defaultOptions = {
  'data-name': '',
  height: '300px',
  scheme: 'brewer.YlGn4',
  split: null,
  title: null,
  type: 'bar',
  util: null,
  width: '600px',
};

var getOptions = elementId => {
  var element = document.getElementById(elementId);
  var options = {};
  for (const optionName of Object.keys(defaultOptions)) {
    options[optionName] =
      element.getAttribute(optionName) || defaultOptions[optionName];
  }

  return options;
};

var domManipulation = (elementId, options) => {

  /** Transforme le dom pour accueillir le graph */
  var html = `
<div style='height: ${options.height}; width: ${options.width};'>
  <div class='chart-container'>
    <canvas id='${elementId}'></canvas>
  </div>
</div>`;
  var elementNew = htmlToElement(html);
  var element = document.getElementById(elementId);
  element.replaceWith(elementNew);
};


var makeGraph = (elementId, data) => {
  // Dom manip
  const options = getOptions(elementId);
  domManipulation(elementId, options);

  const dataChart = data[options['data-name']] || data;

  const chartOptions = makeChartOptions(options, dataChart);

  return new Chart(elementId, chartOptions);
};

var makeGraphs = data => {

/** Pour faire des graph sur tous les elements de type chart-graph */
  var elements = document.getElementsByClassName('chart-graph');
  var ids = [];
  for (const item of elements) {
    ids.push(item.id);
  }
  for (const id of ids) {
    makeGraph(id, data);
  }
};

export { makeGraph, makeGraphs };
