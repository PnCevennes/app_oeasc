import { styles } from './config-style.js'


const IGN_KEY = '3s8maqk3hm42vsjty9yoajtb'; // scan25
const IGN_KEY2 = 'decouverte'; // ORTHO
const MAPBOX_ACCESS_TOKEN = 'pk.eyJ1Ijoiam9lbGNsZW1zIiwiYSI6ImNrbDBtaDkzcDBwZGwycG1sejQxczh0bWIifQ.LkAgAh9XQXuK1UeAcisSAA';
const MAPBOX_ID = 'mapbox/streets-v11';

const configMap = {
  INIT_VIEW: [44.323546, 3.593954],
  INIT_ZOOM: 8,
  INIT_TILE: 'IGN (Cartes)',
  styles,
  baseTilesConfig: {
    open_topo_map: {
      url: 'https://b.tile.opentopomap.org/{z}/{x}/{y}.png',
      attribution: '&copy; <a href="https://opentopomap.org/">OpenTopoMap</a>',
      id: 'open_topo_map',
      label: 'OpenTopoMap'
    },
    mapbox: {
      url:`https://api.mapbox.com/styles/v1/${MAPBOX_ID}/tiles/{z}/{x}/{y}?access_token=${MAPBOX_ACCESS_TOKEN}`,
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>',
      id: 'mapbox',
      label: 'Mapbox'
    },
    ign_carte: {
      url: `https://wxs.ign.fr/${IGN_KEY}/geoportail/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&FORMAT=image%2Fjpeg`,
      attribution: '&copy; <a href="http://www.ign.fr/">IGN</a>',
      id: 'ign_carte',
      label: 'IGN (Cartes)'
    },
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
  tileList: {
    'open_topo_map': {},
    'mapbox': {
      default: true
    },
    'ign_carte': {},
    'ign_ortho': {}
  },
  layers: {
    zc: {
      legend: 'Zone cœur du Parc national',
      url: 'api/ref_geo/areas_simples_from_type_code/l/ZC_PNC',
      type: 'ZC_PNC',
      style: styles.zc,
      pane: 'PANE_FOND_2'
    },
    aa: {
      legend: "Aire d'adhésion du Parc national",
      url: 'api/ref_geo/areas_simples_from_type_code/l/AA_PNC',
      type: 'AA_PNC',
      style: styles.aa,
      pane: 'PANE_FOND_1'
    },
    po: {
      legend: "Périmètre de l'Observatoire",
      url: 'api/ref_geo/areas_simples_from_type_code/l/OEASC_PERIMETRE',
      type: 'OEASC_PERIMETRE',
      style: styles.po,
      pane: 'PANE_FOND_3'
    },
    secteur: {
      legend: "Secteurs d'étude de l'Observatoire",
      url: 'api/ref_geo/areas_simples_from_type_code/l/OEASC_SECTEUR',
      type: 'OEASC_SECTEUR',
      style: styles.secteur,
      pane: 'PANE_FOND_4'
    },
    foret_onf: {
      legend: "Forêt relevant du régime forestier",
      url: 'api/ref_geo/areas_simples_from_type_code/l/OEASC_ONF_FRT',
      type: 'OEASC_ONF_FRT',
      style: styles.normal,
      pane: 'PANE_LAYER_1'
    },
    //   parcelle_onf: {
    //   legend: "Parcelle forestière",
    //   url: (id_area_container) => `api/ref_geo/areas_simples_from_type_code_container/l/OEASC_ONF_PRF/${id_area_container}`,
    //   type: 'OEASC_ONF_PRF',
    //   style: styles.normal,
    //   pane: 'PANE_LAYER_1'
    // },
    // ug_onf: {
    //   legend: "Unité de gestion",
    //   url: (id_area_container) => `api/ref_geo/areas_simples_from_type_code_container/l/OEASC_ONF_UG/${id_area_container}`,
    //   type: 'OEASC_ONF_UG',
    //   style: styles.normal,
    //   pane: 'PANE_LAYER_1'
    // }
  }
};

const select_map_base = {
    zoom: true,
    tooltip: {
      label: 'label',
    },
    hover: {
      style: styles.hover
    },
    select: {
      style: styles.selected
    },
    dataFieldNames: {
      value: "id_area",
      text: "label"
    },
}

const preConfigMap = {
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
  select_map_onf_frt: {
    layerList: {
      po: {},
      foret_onf: { ...select_map_base }
    }
  },
  select_map_onf_prf: {
    layerList: {
      po: {},
      parcelle_onf: { ...select_map_base }
    }
  }
};

const configBaseSelect = {
  pane: 'PANE_LAYER_1',
  style: styles.normal,
  select: {
    style: styles.select
  },
  zoom: true,
    tooltip: {
      label: 'label',
      direction: 'top',
      offset: [0,-20],
      className: 'anim-tooltip',
    },
    hover: {
      style: styles.hover
    },
    click: {
      dispatch: {
        name: 'select-map-click',
        detail: ['id_area']
      }
    }
}

configMap.configBaseSelect = configBaseSelect;

export { configMap, preConfigMap };
