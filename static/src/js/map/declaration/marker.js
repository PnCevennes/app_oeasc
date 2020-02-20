import { removeDoublons } from "../../util/util.js";
import * as chroma from "chroma-js";

const initDeclarationsMakerColors = (mapConfig, declarations) => {
  const colors = chroma.brewer.Dark2;

  if (!mapConfig.declarations.display) {
    return;
  }

  const { fieldName } = mapConfig.declarations.display;

  const values = removeDoublons(declarations.map(d => d[fieldName]));
  const countValues = {};
  for (const value of values) {
    countValues[value] = declarations.filter(
      d => d[fieldName] === value
    ).length;
  }

  values.sort((a, b) => {
    const test1 = countValues[b] - countValues[a];

    if (test1) {
      return test1;
    }

    return 2 * (a - b) - 1;
  });

  mapConfig.declarations.colors = {};
  // mapConfig.declarations.colors = mapConfig.declarations.colors || {};
  mapConfig.declarations.colors[fieldName] = {};
  for (const [i, value] of values.entries()) {
    mapConfig.declarations.colors[fieldName][value] = colors[i];
  }
};

const makeDeclarationMarkerColor = (mapConfig, declaration) => {
  const defaultColor = "grey";

  if (!mapConfig.declarations.display) {
    return defaultColor;
  }

  const { fieldName } = mapConfig.declarations.display;
  const value = declaration[fieldName];

  const color = mapConfig.declarations.colors[fieldName][value] || defaultColor;

  return color;
};

const makeDeclarationMarkerRadius = (mapConfig, declaration) => 10;

const makeDeclarationMarkerConfig = (mapConfig, declaration) => {
  const color = makeDeclarationMarkerColor(mapConfig, declaration);
  const radius = makeDeclarationMarkerRadius(mapConfig, declaration);

  const declarationMarkerConfig = {
    pane: "PANE_20",
    color,
    radius
  };

  return declarationMarkerConfig;
};

const findDeclarationMarker = (map, mapConfig, idDeclaration) => {

  return Object.values(map._layers).find(l => l.id_declaration === idDeclaration);
};

const makeDeclarationMarker = (map, mapConfig, declaration) => {
  const declarationMarkerConfig = makeDeclarationMarkerConfig(
    mapConfig,
    declaration
  );
  let elem = findDeclarationMarker(map, mapConfig, declaration.id_declaration);
  // eslint-disable-next-line no-negated-condition
  if (!elem) {
    switch (mapConfig.declarations.type) {
      case "marker":
        elem = L.marker(declaration.centroid, {
          ...declarationMarkerConfig
        });
        break;

      case "point":
        elem = L.circle(declaration.centroid, {
          ...declarationMarkerConfig
        });
        break;

      case "circleMarker":
        elem = L.circleMarker(declaration.centroid, {
          ...declarationMarkerConfig
        });
        break;

      default:
        break;
    }
    elem.id_declaration = declaration.id_declaration;
  } else {
    elem.setStyle(declarationMarkerConfig);
  }
  return elem;
};

export { makeDeclarationMarker, initDeclarationsMakerColors };
