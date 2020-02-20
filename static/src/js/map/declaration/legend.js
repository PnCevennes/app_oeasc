import { removeElementByClass } from '../../util/util.js';

const declarationMarkerLegend = (type, color, legend) => {
  let sIcon = '';
  switch (type) {
    case 'marker':
      sIcon = `<i class="fa fa-map-marker-alt fa-lg" style="color: ${color};"></i>`;
      break;
    case 'point':
      sIcon = `<i style="color:${color};font-size:0.5rem; transform:translateY(5px)" class="fas fa-circle"></i>`;
      break;
    case 'circleMarker':
      sIcon = `<i style="color:${color}; transform:translateY(2px)" class="far fa-lg fa-circle"></i>`;
      break;
    default:
  }

  return `<div class="legend-declaration">${sIcon}${legend}</div>`;
}
/*
 *   If (mapConfig.declarations) {
 *     switch(mapConfig.declarations.type) {
 *       case 'marker':
 *         div.innerHTML += declarationMarkerLegend()
 *         break;
 *       case 'point':
 *         div.innerHTML += declarationPointLegend()
 *         break;
 *       case 'circleMarker':
 *         div.innerHTML += declarationCircleMarkerLegend()
 *         break;
 *       default:
 *     }
 *   }
 */

const initDeclarationsLegend = (map, mapConfig) => {
  const [legend] = document.
    getElementById(map.id).
    getElementsByClassName('legend');
  removeElementByClass('legend-declaration', legend);

  if (!mapConfig.declarations.display) {
    return;
  }
  const { fieldName } = mapConfig.declarations.display;
  const colors = mapConfig.declarations.colors[fieldName];
  legend.innerHTML += `<div class="legend-declaration"><b>${mapConfig.declarations.display.label}</b></div>`
  for (const key of Object.keys(colors)) {
    legend.innerHTML += declarationMarkerLegend(mapConfig.declarations.type, colors[key], key);
  }
};

export { initDeclarationsLegend };
