import { apiRequest } from '../data/api.js';
import { htmlToElement } from '../util/util.js';
import { makeChartOptions } from './chart-options.js';
import { Chart } from './chart-commons.js'

var defaultOptions = {
  'data-name': '',
  height: '300px',
  'label-position': 'left',
  scheme: 'brewer.YlGn4',
  stacked: false,
  title: null,
  type: 'bar',
  util: null,
  view: '',
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

var getDataCache = (options, data) => {
  const [schema, view] = options.view.split('.');

  return data[schema] && data[schema][view]
}

var getData = (options) => {
  const [schema, view] = options.view.split('.');

  return apiRequest(`api/resultat/get_view/${schema}/${view}`)
};

var makeGraph = (elementId, data = null) => {
  // Dom manip
  const options = getOptions(elementId);
  domManipulation(elementId, options);

  const dataGraph = getDataCache(options, data);
  if (dataGraph) {
    const chartOptions = makeChartOptions(options, dataGraph);

    return new Chart(elementId, chartOptions);
  }

  getData(options).then((data) => {
    const chartOptions = makeChartOptions(options, data);
    
    return new Chart(elementId, chartOptions);
  });

};

var makeGraphs = (data={}) => {

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
