import { removeElementByClass } from '../../util/util.js';
import { defaultIcon, defaultColor } from './marker.js'

const declarationMarkerLegend = (type, legend, color, icon) => {
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
    case 'icon':
      sIcon = `<i style="color:${color}; transform:translateY(2px)"; class="${icon} fa-lg shadow"></i>`;
    default:
  }

  return `<div class="legend-declaration">${sIcon}${legend}</div>`;
};

const sLegendForType = (mapConfig, type) => {

  if (!(mapConfig.declarations[type] && mapConfig.declarations[type].fieldName)) {
    return '';
  }

  const fieldNameColor = mapConfig.declarations.color.fieldName;
  const curListColor = mapConfig.declarations.color.curList;

  const fieldNameIcon = mapConfig.declarations.icon.fieldName;
  const curListIcon = mapConfig.declarations.icon.curList;


  if (fieldNameColor === fieldNameIcon && type === 'icon') {
    return '';
  }

  const { label, curList } = mapConfig.declarations[type];

  let sLegend = `<div class="legend-declaration"><b>${label}</b></div>`;

  for (const key of Object.keys(curList)) {
    const markerLabel =
      key !== ''
        ? key
        : 'Aucun';

    const color = type === 'color' && curList[key] || defaultColor;
    let icon = type === 'icon' && curList[key] || defaultIcon;

    if (fieldNameColor === fieldNameIcon) {
      icon = 'icon' && curListIcon[key] || defaultIcon
    }

    sLegend += declarationMarkerLegend(
      mapConfig.declarations.type,
      markerLabel,
      color,
      icon
    );
  }

  return sLegend;
}

const initDeclarationsLegend = map => {
  const [legend] = document.
    getElementById(map.id).
    getElementsByClassName('legend');
  removeElementByClass('legend-declaration', legend);

  legend.innerHTML += sLegendForType(map.config, 'color');
  legend.innerHTML += sLegendForType(map.config, 'icon');
};

export { initDeclarationsLegend };
