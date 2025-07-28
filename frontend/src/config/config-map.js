// Importation des styles des couches depuis le fichier de configuration
import { styles } from './config-style.js'

// Clés d'accès pour les différents fournisseurs de tuiles cartographiques
const IGN_KEY = '3s8maqk3hm42vsjty9yoajtb'; // Clé IGN pour les cartes topographiques
const IGN_KEY2 = 'decouverte'; // Clé IGN pour les orthophotos
const MAPBOX_ACCESS_TOKEN = 'pk.eyJ1Ijoiam9lbGNsZW1zIiwiYSI6ImNrbDBtaDkzcDBwZGwycG1sejQxczh0bWIifQ.LkAgAh9XQXuK1UeAcisSAA'; // Token d'accès Mapbox
const MAPBOX_ID = 'mapbox/streets-v11'; // Identifiant du style Mapbox

// Objet principal de configuration de la carte
const configMap = {
  // Vue initiale de la carte (latitude, longitude)
  INIT_VIEW: [44.323546, 3.593954],
  // Niveau de zoom initial
  INIT_ZOOM: 8,
  // Fond de carte initial
  INIT_TILE: 'IGN (Cartes)',
  // Styles des couches (importés)
  styles, // style des layers définis dans config-style.js

  // Configuration des fonds de carte disponibles
  baseTilesConfig: {
    // Fond OpenTopoMap
    open_topo_map: {
      url: 'https://b.tile.opentopomap.org/{z}/{x}/{y}.png',
      attribution: '&copy; <a href="https://opentopomap.org/">OpenTopoMap</a>',
      id: 'open_topo_map',
      label: 'OpenTopoMap'
    },
    // Fond Mapbox Streets
    mapbox: {
      url:`https://api.mapbox.com/styles/v1/${MAPBOX_ID}/tiles/{z}/{x}/{y}?access_token=${MAPBOX_ACCESS_TOKEN}`,
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>',
      id: 'mapbox',
      label: 'Mapbox'
    },
    // Fond IGN Cartes
    ign_carte: {
      url: `https://wxs.ign.fr/${IGN_KEY}/geoportail/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&FORMAT=image%2Fjpeg`,
      attribution: '&copy; <a href="http://www.ign.fr/">IGN</a>',
      id: 'ign_carte',
      label: 'IGN (Cartes)'
    },
    // Fond IGN Orthophotos
    ign_ortho: {
      url: `https://wxs.ign.fr/${IGN_KEY2}/geoportail/wmts?` +
      "&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0" +
      "&STYLE=normal" +
      "&TILEMATRIXSET=PM" +
      "&FORMAT=image/jpeg"+
      "&LAYER=ORTHOIMAGERY.ORTHOPHOTOS"+
      "&TILEMATRIX={z}" +
      "&TILEROW={y}" +
      "&TILECOL={x}",
      attribution: '&copy; <a href="http://www.ign.fr/">IGN</a>',
      id: 'ign_ortho',
      label: 'IGN (Ortho.)'
    }
  },

  // Liste des fonds de carte disponibles et configuration du fond par défaut
  tileList: {
    'open_topo_map': {},
    'mapbox': {
      default: true // Mapbox est le fond par défaut
    },
    'ign_carte': {},
    'ign_ortho': {}
  },

  // Définition des couches vectorielles affichables sur la carte
  layers: {
    // Zone cœur du Parc national
    zc: {
      legend: 'Zone cœur du Parc national', // Nom affiché dans la légende
      url: 'api/ref_geo/areas_simples_from_type_code/l/ZC_PNC', // URL d'accès aux données
      type: 'ZC_PNC', // Type de couche (utilisé pour les requêtes)
      style: styles.zc, // Style appliqué à la couche
      pane: 'PANE_FOND_2' // Pane Leaflet où la couche est ajoutée
    },
    // Aire d'adhésion du Parc national
    aa: {
      legend: "Aire d'adhésion du Parc national",
      url: 'api/ref_geo/areas_simples_from_type_code/l/AA_PNC',
      type: 'AA_PNC',
      style: styles.aa,
      pane: 'PANE_FOND_1'
    },
    // Périmètre de l'Observatoire
    po: {
      legend: "Périmètre de l'Observatoire",
      url: 'api/ref_geo/areas_simples_from_type_code/l/OEASC_PERIMETRE',
      type: 'OEASC_PERIMETRE',
      style: styles.po,
      pane: 'PANE_FOND_3'
    },
    // Secteurs d'étude de l'Observatoire
    secteur: {
      legend: "Secteurs d'étude de l'Observatoire",
      url: 'api/ref_geo/areas_simples_from_type_code/l/OEASC_SECTEUR',
      type: 'OEASC_SECTEUR',
      style: styles.secteur,
      pane: 'PANE_FOND_4'
    },
    // Forêt relevant du régime forestier
    foret_onf: {
      legend: "Forêt relevant du régime forestier",
      url: 'api/ref_geo/areas_simples_from_type_code/l/OEASC_ONF_FRT',
      type: 'OEASC_ONF_FRT',
      style: styles.normal,
      pane: 'PANE_LAYER_1'
    },
  }
};

// Configuration de base pour les sélections sur la carte (utilisée pour les couches interactives)
const select_map_base = {
    zoom: true, // Active le zoom sur la sélection
    tooltip: {
      label: 'label', // Champ utilisé pour l'affichage du tooltip
    },
    hover: {
      style: styles.hover // Style appliqué au survol
    },
    select: {
      style: styles.selected // Style appliqué à la sélection
    },
    dataFieldNames: {
      value: "id_area", // Champ utilisé comme identifiant
      text: "label" // Champ utilisé comme texte affiché
    },
}

// Pré-configuration de la carte pour différents contextes d'affichage
const preConfigMap = {
  // Configuration pour l'affichage du périmètre
  perimetre: {
    layerList: {
      zc: {},
      aa: {},
      secteur: {
        zoom: true,
        tooltip: {
          permanent: true,
          className: 'tooltip-label',
          label: 'label'
        }
      }
    }
  },
  // Configuration pour la sélection des forêts ONF
  select_map_onf_frt: {
    layerList: {
      po: {},
      foret_onf: { ...select_map_base }
    }
  },
  // Configuration pour la sélection des parcelles ONF
  select_map_onf_prf: {
    layerList: {
      po: {},
      parcelle_onf: { ...select_map_base }
    }
  }
};

// Configuration de base pour la sélection sur la carte (utilisée pour les couches interactives)
const configBaseSelect = {
  pane: 'PANE_LAYER_1', // Pane Leaflet pour la couche sélectionnée
  style: styles.normal, // Style par défaut
  select: {
    style: styles.select // Style appliqué à la sélection
  },
  zoom: true, // Active le zoom sur la sélection
  tooltip: {
    label: 'label', // Champ utilisé pour le tooltip
    direction: 'top', // Direction du tooltip
    offset: [0,-20], // Décalage du tooltip
    className: 'anim-tooltip', // Classe CSS pour le tooltip
  },
  hover: {
    style: styles.hover // Style appliqué au survol
  },
  click: {
    dispatch: {
      name: 'select-map-click', // Nom de l'événement dispatché au clic
      detail: ['id_area'] // Détail envoyé avec l'événement
    }
  }
}

// Ajout de la configuration de sélection à l'objet principal de configuration
configMap.configBaseSelect = configBaseSelect;

// Exportation des objets de configuration pour utilisation dans l'application Vue.js
export { configMap, preConfigMap };
