import { makeGraphs } from './graph/graph.js';
import { apiRequest } from './data/api.js';
import '../css/test-chart.css';


document.addEventListener('DOMContentLoaded', () => {
  var fieldNames = [
    'secteur',
    'type_foret',
    'secteur',
    'type_foret',
    'organisme_group',
    'peuplement_ess_1_mnemo',
    'peuplement_ess_2_mnemo',
    'degat_types_mnemo'
  ];


  fieldNames = ['secteur'];

  var views = [
    ...fieldNames.map(n => `oeasc_resultats.v_nb_declaration_${n}`),
    ...fieldNames.map(n => `oeasc_resultats.v_timeline_declaration_${n}`)
  ];


  var url = `api/resultat/get_views?view=${views.join('&view=')}`;
  apiRequest(`${url}`).then(data => {
    makeGraphs(data);
  });
});
