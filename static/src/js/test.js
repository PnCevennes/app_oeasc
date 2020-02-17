import { apiRequest } from './data/api.js';
import { makeGraphs } from './graph/graph.js'
import '../css/test.css'

var views = [
  'nb_declaration_secteur',
  'nb_declaration_organisme',
  'timeline_declaration',
  'timeline_declaration_secteur',
]

var processData = (values) => {
  var data = {};
  for (const [i, v] of views.entries()) {
    data[v] = values[i];
  }
  makeGraphs(data);
};

document.addEventListener('DOMContentLoaded', () => {

  var promises = views.map(v => apiRequest(`api/declaration/get_view/oeasc_declarations/${v}`))
  Promise.all(promises).then(processData);

});
