import { apiRequest } from '../../data/api.js';
import { sTooltipDegats } from './tooltip.js';
import { makeDeclarationMarker, initDeclarationsMakerColors } from './marker.js'
import { initDeclarationsLegend } from './legend.js'
import { chroma } from 'chroma-js'

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

const processDeclarations = (map, mapConfig, declarations) => {
  console.log(declarations[0])
  initDeclarationsMakerColors(mapConfig, declarations);
  initDeclarationsLegend(map, mapConfig, declarations);
  for (const declaration of declarations) {
    const elem = makeDeclarationMarker(map, mapConfig, declaration);

    if (!elem) {
      continue;
    }
    // if (mapConfig.declarations.popup) {
    //   elem.bindPopup(makeSPopupDeclaration(declaration), {
    //     pane: 'PANE_35'
    //   });
    // }

    // if (mapConfig.declarations.display === 'gravite') {
    //   elem.bindTooltip(sTooltipDegats(declaration.degats), {
    //     pane: 'PANE_30',
    //     permanent: true,
    //     direction: 'top',
    //     color: 'white',
    //     opacity: 1,
    //     fillOpacity: 1,
    //     interactive: true,
    //     className: 'tooltip',
    //   });
    // }

    elem.addTo(map);
  }
}

const loadDeclarations = (map, mapConfig) => {
  apiRequest('api/declaration/declarations/').then(declarations => {
    map.declarations = declarations;
    processDeclarations(map, mapConfig, declarations);
  });
};

const loadDeclaration = (map, mapConfig, declarationId) => {};

export { loadDeclarations, loadDeclaration, processDeclarations };
