import { apiRequest } from '../../data/api.js';
import { sTooltipDegats } from './tooltip.js';
import { makeDeclarationMarker, initDeclarationsMarkerType } from './marker.js'
import { initDeclarationsLegend } from './legend.js'
import { applyFilters } from '../layer/util.js';


const makeSPopupDeclaration = (declaration) => {
  var sPopup = '';
  sPopup += '<table class="table-sm table-popup">';
  sPopup += `<tr><th colspan="4"><a href="/declaration/declaration/${declaration.id_declaration}"  target="_blank">Alerte ${declaration.id_declaration} </a></th></tr>`;
  sPopup += `<tr><th>Date</th><td colspan="3">${declaration.declaration_date}</td></tr>`;
  sPopup += `<tr><th>Nom Foret</th><td colspan="3">${declaration.label_foret}</td></tr>`;
  for (const degat of declaration.degats) {
    sPopup += `<tr><th colspan="4">${degat.degat_type_label}</th>`;
    for (const degatEssence of degat.degat_essences) {
      sPopup += `<tr><td>${degatEssence.degat_essence_label}</td>`;
      if (degatEssence.degat_gravite) {
        sPopup += `<td>${degatEssence.degat_gravite_code}</td>`;
        sPopup += `<td>${degatEssence.degat_etendue_code}</td>`;
        sPopup += `<td>${degatEssence.degat_anteriorite_code}</td>`;
      }
      sPopup += '</tr>';
    }
    sPopup += '</tr>';
  }
  sPopup += '</table>';

  return sPopup;
};

const processDeclarations = (map) => {

  const { declarations } = map;
  console.log(declarations[0])

  // filter
  for (const declaration of declarations) {
    declaration.selected = applyFilters(map.config.declarations.filters, declaration);
  }

  initDeclarationsMarkerType(map.config, declarations, 'color');
  initDeclarationsMarkerType(map.config, declarations, 'icon');
  initDeclarationsLegend(map, declarations);

  for (const declaration of declarations) {
    // filter
    const elem = makeDeclarationMarker(map, declaration);

    if (!elem) {
      continue;
    }
    // if (mapConfig.declarations.popup) {
    //   elem.bindPopup(makeSPopupDeclaration(declaration), {
    //     pane: 'PANE_35'
    //   });
    // }

  }
}

const loadDeclarations = (map) => {
  apiRequest('api/declaration/declarations/').then(declarations => {
    map.declarations = declarations;
    processDeclarations(map);
  });
};

export { loadDeclarations, processDeclarations };
