import { removeDoublons } from '@/core/js/util/util.js';
import { findLayer } from '../layer/util.js';

var L = window.L;

const defaultIcon = 'fas fa-circle';
const defaultColor = 'grey';

const getDeclarationValues = (declaration, fieldName) => {
  let sValues = '';
  if (fieldName in declaration) {
    sValues = declaration[fieldName];
  }

  // if (fieldName.includes('->')) {
  //   let value = '';
  //   for (const paramName of fieldName.split('->')) {
  //     console.log(paramName, declaration[paramName])
  //   }
  // }

  return sValues.split(', ');
}

const initDeclarationsMarkerType = (mapConfig, declarations, type) => {

  if (!(mapConfig.declarations[type] && mapConfig.declarations[type].fieldName)) {
    return;
  }

  const { fieldName } = mapConfig.declarations[type];
  const preValues = declarations.filter(d => d.selected).map(d => getDeclarationValues(d, fieldName));

  let values = [];
  for (const pv of preValues) {
    values = values.concat(pv);
  }
  values = removeDoublons(values);

  // comptage du nombre de declaration pour chaque valeur de fieldName
  const countValues = {};
  for (const value of values) {
    countValues[value] = declarations.filter(d => getDeclarationValues(d, fieldName).includes(value)).length;
  }

  // tri par ordre nb de declaration par *fieldName && ordre apha.
  values.sort((a, b) => {
    const test1 = countValues[b] - countValues[a];

    // si test1 == 0 on fait par ordre alpha.
    if (test1) {
      return test1;
    }

    return 2 * (a - b) - 1;
  });

  mapConfig.declarations[type].curList = {};
  for (const [i, value] of values.entries()) {
    mapConfig.declarations[type].curList[value] = mapConfig.declarations[type].list[i];
  }

}

const valuesOfType = (mapConfig, declaration, type) => {

  const default_ = type === 'color' && defaultColor || defaultIcon;

  if (!(mapConfig.declarations[type] && mapConfig.declarations[type].fieldName)) {
    return [default_]
  }

  const { fieldName } = mapConfig.declarations[type];
  const values = getDeclarationValues(declaration, fieldName).map(value => {
  const typeList = mapConfig.declarations[type] && mapConfig.declarations[type].curList || {};

  return typeList[value] || default_;
  });

  return values;
}

const stooltipDeclaration = declarationMarkerConfig => {
  let sTooltip = '';
  for (const config of declarationMarkerConfig) {
    sTooltip += `<i style="opacity:${config.opacity}; color:${config.color}" class="${config.faIcon} fa-lg shadow"></i>`;
  }

return sTooltip;
};

const makeDeclarationMarkerConfig = (mapConfig, declaration) => {

  const declarationMarkerConfig = []

  const colors = valuesOfType(mapConfig, declaration, 'color');
  const faIcons = valuesOfType(mapConfig, declaration, 'icon');

  for (const color of colors) {
    for (const faIcon of faIcons) {
      const config = {
        pane: 'PANE_20',
        color,
        faIcon,
        opacity: declaration.selected
          ? 0.9
          : 0,
        fillOpacity: declaration.selected
          ? 0.5
          : 0,
        type: mapConfig.declarations.type
      }
      declarationMarkerConfig.push(config)
    }
  }

  return declarationMarkerConfig;
};

const setDeclarationMarker = (mapConfig, declarationMarkerConfig, elem) => {

    let sTooltip = ' ';
    if (mapConfig.declarations.color.fieldName || mapConfig.declarations.icon.fieldName) {
      sTooltip = stooltipDeclaration(declarationMarkerConfig);
    }
    elem.setTooltipContent(sTooltip);
    declarationMarkerConfig.color = 'grey';
    elem.setStyle({
      opacity: declarationMarkerConfig[0].opacity,
      fillOpacity: declarationMarkerConfig[0].fillOpacity,
    });
}

const makeDeclarationMarker = (map, declaration) => {
  const declarationMarkerConfig = makeDeclarationMarkerConfig(
    map.config,
    declaration
  );
  let elem = findLayer(
    map,
    'declaration',
    'id_declaration',
    declaration.id_declaration
  );

  if (!elem) {
    switch (declarationMarkerConfig[0].type) {
      // case 'marker':
      //   elem = L.marker(declaration.centroid, {
      //     ...declarationMarkerConfig
      //   });
      //   break;

      // case 'point':
      //   elem = L.circle(declaration.centroid, {
      //     ...declarationMarkerConfig
      //   });
      //   break;

      // case 'circleMarker':
      //   elem = L.circleMarker(declaration.centroid, {
      //     ...declarationMarkerConfig
      //   });
      //   break;

      case 'icon':
        elem = L.circle(declaration.centroid, {
          pane: declarationMarkerConfig[0].pane,
          color: 'black'
        }).bindTooltip('', {
          pane: 'PANE_30',
          permanent: true,
          direction: 'top',
          color: 'white',
          opacity: 1,
          fillOpacity: 1,
          interactive: true,
          className: 'tooltip'
        });
        break;
      default:
        break;
    }
    elem.feature = {
      properties: {
        id_declaration: declaration.id_declaration,
        type: 'declaration'
      }
    };
    elem.addTo(map);
  }
  setDeclarationMarker(map.config, declarationMarkerConfig, elem);

  return elem;
};

export { makeDeclarationMarker, initDeclarationsMarkerType, defaultColor, defaultIcon };
