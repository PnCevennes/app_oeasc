export const configMap = {
    INIT_VIEW: [44.323546, 3.593954],
    INIT_ZOOM: 8,
    IGN_KEY: 'choisirgeoportail',
    INIT_TILE: 'IGN (Cartes)',
    baseTilesConfig: {
      open_topo_map: {
        url: 'https://b.tile.opentopomap.org/{z}/{x}/{y}.png',
        attribution: '&copy; <a href="https://opentopomap.org/">OpenTopoMap</a>',
        id: 'open_topo_map',
        label: 'OpenTopoMap'
      },
      mapbox: {
        url: 'https://api.tiles.mapbox.com/v4/mapbox.streets/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw',
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>',
        id: 'mapbox',
        label: 'Mapbox'
      },
      ign_carte: {
        url: `https://wxs.ign.fr/IGN_KEY/geoportail/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&FORMAT=image%2Fjpeg`,
        attribution: '&copy; <a href="http://www.ign.fr/">IGN</a>',
        id: 'ign_carte',
        label: 'IGN (Cartes)'
      },
      ign_ortho: {
        url: `https://wxs.ign.fr/IGN_KEY/geoportail/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=ORTHOIMAGERY.ORTHOPHOTOS&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&FORMAT=image%2Fjpeg`,
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
      'ign_ortho': {},
    },
    layers: {
      zc: {
        legend: 'Zone cœur du Parc national',
        url: 'api/ref_geo/areas_simples_from_type_code/l/ZC_PNC',
        style: {
          weight: 1,
          opacity: 1,
          fillOpacity: 0.4,
          color: 'grey',
          fillColor: '#feb24c'
        },
        pane: 'PANE_2'
      },
      aa: {
        legend: 'Aire d\'adhésion du Parc national',
        url: 'api/ref_geo/areas_simples_from_type_code/l/AA_PNC',
        style: {
          weight: 1,
          opacity: 1,
          fillOpacity: 0.4,
          color: 'grey',
          fillColor: '#ffeda0'
        },
        pane: 'PANE_1'
      },
      po: {
        legend: 'Périmètre de l\'Observatoire',
        url: 'api/ref_geo/areas_simples_from_type_code/l/OEASC_PERIMETRE',
        style: {
          weight: 2,
          opacity: 0.5,
          fillOpacity: 0.2,
          color: 'black'
        },
        pane: 'PANE_3'
      },
      secteurs: {
        legend: 'Secteurs d\'étude de l\'Observatoire',
        url: 'api/ref_geo/areas_simples_from_type_code/l/OEASC_SECTEUR',
        style: {
          weight: 2,
          opacity: 1,
          fillOpacity: 0.1,
          color: 'grey',
          fillColor: '#dfdfdf'
        },
        pane: 'PANE_4'
      }
    }
  }
