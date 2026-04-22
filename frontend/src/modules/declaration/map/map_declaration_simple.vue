<!--


-->
<template>
  <div style="width: 100%; display: flex; flex-direction: row">
    <div
      :id="mapId"
      class="map-container"
      style="height: 500px; width: 100%; z-index: 0"
    ></div>
  </div>
</template>

<script>
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { fetch_oeasc_perimetre } from '@/modules/declaration/utils/api_request.js'; // Importez les fonctions nécessaires si elles existent
import { apiRequest } from '@/core/js/data/api';

const config_layers = {
  OEASC: {
    id_type: 0,
    color: '#777777',
    weight: 1,
    fillColor: '#000000',
    fillOpacity: 0.1,
    zIndex: 200,
    legend: 'Périmètre OEASC',
  },
  SECTEUR: {
    id_type: 326,
    color: '#777777',
    weight: 1,
    fillColor: '#777777',
    fillOpacity: 0.2,
    zIndex: 300,
    legend: 'Secteurs',
  },

  COMMUNES: {
    id_type: 327,
    color: '#777777',
    weight: 1,
    fillColor: '#3371f7',
    fillOpacity: 0.4,
    zIndex: 400,
    legend: 'Communes',
  },
  SECTIONS: {
    id_type: 333,
    color: '#777777',
    weight: 1,
    fillColor: '#3371f7',
    fillOpacity: 0.5,
    zIndex: 350,
    legend: 'Sections cadastrales',
  },
  FORETS_ONF: {
    id_type: 328,
    color: '#777777',
    weight: 1,
    fillColor: '#227033',
    fillOpacity: 0.5,
    zIndex: 450,
    legend: 'Forêts ONF',
  },
  FORETS_DGD: {
    id_type: 331,
    color: '#777777',
    weight: 1,
    fillColor: '#227033',
    fillOpacity: 0.5,
    zIndex: 450,
    legend: 'Forêts DGD',
  },
  PARCELLES_ONF: {
    id_type: 329,
    color: '#777777',
    weight: 2,
    fillColor: '#976032',
    fillOpacity: 0.9,
    zIndex: 475,
    legend: 'Parcelles ONF',
  },

  UG_ONF: {
    id_type: 330,
    color: '#777777',
    weight: 1,
    fillColor: '#8A2BE2',
    fillOpacity: 0.5,
    zIndex: 500,
    legend: 'Unités de gestion ONF',
  },
  CADASTRES: {
    id_type: 332,
    color: '#777777',
    weight: 1,
    fillColor: '#976032',
    fillOpacity: 0.9,
    zIndex: 500,
    legend: 'Parcelles cadastrales',
  },
};

// style par défaut à utiliser quand aucun style spécifique n'est trouvé
const DEFAULT_STYLE = config_layers['OEASC'];

export default {
  name: 'MapDeclarationSimple',
  props: {
    declaration_data: {
      // toutes les données de déclaration récupérées depuis la bdd
      type: Object,
      required: true,
    },

    liste_layers: {
      // liste des types de zones à afficher sur la carte, par exemple ["COMMUNES", "FORETS_ONF"]
      type: Array,
      required: false,
      default: () => ['OEASC'], // par défaut, on affiche uniquement le périmètre oeasc
    },
    zoom_on: {
      // liste optionnelle de noms de couches à prioriser pour le zoom, ex ['OEASC','COMMUNES']
      type: Array,
      required: false,
      default: () => null,
    },
  },

  components: {},

  data() {
    return {
      map: null, // Instance de la carte Leaflet. Sera activé dans monted() avec initMap()
      mapId: null,
      geom_perimetre_oeasc: null, // geojson du périmètre oeasc, affiché en noir et non selectionnable. Affiché en permanence.
      all_areas_geojson: null, // GeoJSON de toutes les zones disponibles pour le type de carte sélectionné. Sert à afficher les pastilles sur la carte.
      areasLayerGroup: null,
      // runtime helpers for string-based layer selection
      requestedIdTypes: new Set(),
      requestedNames: new Set(),
      stylesById: {},
      legendControl: null,
      declarationMarker: null,
      labelLayerGroup: null,
      labelItems: [],
      useLabelgun: false,
    };
  },

  computed: {},
  watch: {
    liste_layers: {
      handler() {
        this.updateRequestedLayersFromProps();
        // refresh layers when the requested list changes
        if (this.map) this.addAreasLayers();
      },
      deep: true,
    },
  },

  created() {
    // générer un id unique pour le conteneur de la carte (évite conflit si plusieurs instances)
    this.mapId = `map-${this._uid || Math.floor(Math.random() * 1e9)}`;
  },

  async mounted() {
    // construire la liste des id_types à partir de liste_layers qui peut contenir des strings ou des id_types directs
    const list_id_types = this.liste_layers
      .map((item) => {
        if (typeof item === 'string') {
          const cfg = config_layers[item];
          return cfg && typeof cfg.id_type !== 'undefined' ? cfg.id_type : null;
        } else if (typeof item === 'number') {
          return item;
        }
        return null;
      })
      .filter((v) => v !== null);

    // maintenant qu'on a la liste des types d'areas demandés, on lance une requête pour récupérer les données correspondantes (en GeoJSON) et on les stocke dans all_areas_geojson
    try {
      const result = await apiRequest(
        'GET',
        `api/declaration/all_areas_declaration?id=${this.declaration_data.id_declaration}&list_id_types=${list_id_types}`
      );
      this.all_areas_geojson = result;
      //   console.debug('MapDeclarationSimple: fetched all_areas_geojson', this.all_areas_geojson && (this.all_areas_geojson.features ? this.all_areas_geojson.features.length : 'no-features'));
    } catch (error) {
      console.error(
        'Erreur lors de la récupération de toutes les aires de la déclaration :',
        error
      );
      this.all_areas_geojson = null;
    }

    // si OEASC demandé, récupérer son périmètre spécifique
    if (
      this.liste_layers.includes('OEASC') ||
      list_id_types.includes(config_layers['OEASC'].id_type)
    ) {
      try {
        this.geom_perimetre_oeasc = await fetch_oeasc_perimetre();
      } catch (e) {
        console.warn('Erreur récupération périmètre OEASC :', e);
        this.geom_perimetre_oeasc = null;
      }
    }

    // construire un mapping id_type → style pour un accès plus facile lors du rendu (évite de devoir faire des recherches à chaque feature)
    try {
      this.stylesById = {};
      Object.keys(config_layers).forEach((k) => {
        const v = config_layers[k];
        if (v && typeof v.id_type !== 'undefined') this.stylesById[v.id_type] = v;
      });
    } catch (e) {
      this.stylesById = {};
    }

    this.updateRequestedLayersFromProps();

    this.initMap();
  },

  beforeDestroy() {
    // s'assure que la carte est bien détruite quand le composant est démonté
    try {
      // remove declaration marker if any
      this.removeDeclarationMarker();
      if (this.map) {
        this.map.remove();
        this.map = null;
      }
    } catch (e) {
      console.warn('Erreur lors de la destruction de la carte :', e);
    }
  },

  methods: {
    updateRequestedLayersFromProps() {
      // normalize this.liste_layers which may contain strings like 'COMMUNES' or numbers
      this.requestedIdTypes = new Set();
      this.requestedNames = new Set();
      if (!Array.isArray(this.liste_layers)) return;
      this.liste_layers.forEach((item) => {
        if (typeof item === 'string') {
          this.requestedNames.add(item);
          const cfg = config_layers[item];
          if (cfg && typeof cfg.id_type !== 'undefined') this.requestedIdTypes.add(cfg.id_type);
        } else if (typeof item === 'number') {
          this.requestedIdTypes.add(item);
        }
      });
    },

    /**
     * Ajoute le périmètre oeasc à la carte.
     * Le périmètre oeasc est affiché en noir et non sélectionnable.
     */
    add_layer_perimetre_oeasc() {
      if (!this.geom_perimetre_oeasc) return;
      const s = config_layers['OEASC'] || DEFAULT_STYLE;
      const layer = L.geoJSON(this.geom_perimetre_oeasc, {
        style: () => ({
          color: s.color || '#000',
          weight: typeof s.weight === 'number' ? s.weight : 1,
          opacity: 1,
          fillColor: s.fillColor || s.color || '#000',
          fillOpacity: typeof s.fillOpacity === 'number' ? s.fillOpacity : 0.1,
        }),
      }).addTo(this.map);
    },

    async initMap() {
      if (this.map) return;
      // initialiser la carte Leaflet dans le conteneur spécifié par mapId
      const container = document.getElementById(this.mapId);
      if (!container) {
        setTimeout(() => this.initMap(), 50);
        return;
      }
      // création de la carte avec contrôle de zoom activé
      this.map = L.map(container, { zoomControl: true });

      // couche de fond basique
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
      }).addTo(this.map);

      this.areasLayerGroup = L.layerGroup().addTo(this.map);
      this.labelLayerGroup = L.layerGroup().addTo(this.map);

      // re calculer le placement des labels à chaque changement de vue (zoom/pan) pour éviter les chevauchements
      this.map.on('moveend zoomend', () => {
        this.placeLabels();
      });

      // fonction utilitaire pour créer une pane avec un z-index donné si elle n'existe pas déjà, ou mettre à jour son z-index si elle existe déjà (utile pour s'assurer que les couches sont empilées dans le bon ordre même si les données arrivent dans le désordre)
      this.createPaneIfNotExists = (paneName, z) => {
        if (!this.map) return;
        if (!this.map.getPane(paneName)) {
          const p = this.map.createPane(paneName);
          p.style.zIndex = z || 400;
        } else {
          const p = this.map.getPane(paneName);
          p.style.zIndex = z || p.style.zIndex || 200;
        }
      };

      // attendre que les données soient présentes
      const tryAdd = () => {
        if (this.all_areas_geojson) {
          this.addAreasLayers();
          // ajuster les bounds en choisissant la couche cible selon `zoom_on` ou la plus grande
          try {
            const getBoundsForId = (id) => {
              try {
                const tmp = L.geoJSON(this.all_areas_geojson, {
                  filter: (f) => f && f.properties && f.properties.id_type === id,
                });
                const b = tmp.getBounds();
                return b && b.isValid && b.isValid() ? b : null;
              } catch (err) {
                return null;
              }
            };

            let targetBounds = null;

            if (Array.isArray(this.zoom_on) && this.zoom_on.length) {
              // parcourir la liste zoom_on (noms) et zoomer sur le premier présent
              for (const name of this.zoom_on) {
                if (!name) continue;
                const cfg = config_layers[name];
                if (!cfg || typeof cfg.id_type === 'undefined') continue;
                const b = getBoundsForId(cfg.id_type);
                if (b) {
                  targetBounds = b;
                  break;
                }
              }
            }

            if (!targetBounds) {
              // si zoom_on absent ou n'a rien trouvé → zoom sur la couche la plus grande
              // on calcule pour chaque id présent l'aire approximée via bounds span
              const idArray = Array.from(
                new Set(
                  this.all_areas_geojson.features
                    .filter((f) => f && f.properties && typeof f.properties.id_type !== 'undefined')
                    .map((f) => f.properties.id_type)
                )
              );

              let best = { id: null, score: -1 };
              for (const id of idArray) {
                const b = getBoundsForId(id);
                if (!b) continue;
                const latDiff = Math.abs(b.getNorth() - b.getSouth());
                const lngDiff = Math.abs(b.getEast() - b.getWest());
                const score = latDiff * lngDiff; // approximation de surface
                if (score > best.score) best = { id, score, bounds: b };
              }
              if (best.id !== null) targetBounds = best.bounds;
            }

            if (targetBounds) {
              this.map.fitBounds(targetBounds);
              //   console.debug('MapDeclarationSimple: fitBounds applied to targetBounds', targetBounds);
            } else {
              // fallback général
              console.warn(
                'MapDeclarationSimple: no valid bounds found from data, setting default view'
              );
              this.map.setView([46.5, 2.5], 6);
              //   console.debug('MapDeclarationSimple: no bounds found, set default view');
            }
            // if declaration_data.centroid exists, add a marker
            try {
              if (
                this.declaration_data &&
                Array.isArray(this.declaration_data.centroid) &&
                this.declaration_data.centroid.length >= 2
              ) {
                // centroid is [lat, lng]
                const lat = Number(this.declaration_data.centroid[0]);
                const lng = Number(this.declaration_data.centroid[1]);
                if (!Number.isNaN(lat) && !Number.isNaN(lng) && this.map) {
                  // remove existing marker if present
                  this.removeDeclarationMarker();
                  // create marker with a high zIndex offset so it stays above other layers
                  this.declarationMarker = L.marker([lat, lng], { zIndexOffset: 1000 });
                  this.declarationMarker.addTo(this.map);
                }
              }
            } catch (e) {
              // ignore marker errors
            }
          } catch (e) {
            // ignore
          }
        }
        if (
          this.geom_perimetre_oeasc &&
          (this.requestedNames.has('OEASC') ||
            this.requestedIdTypes.has(config_layers['OEASC'].id_type))
        ) {
          this.add_layer_perimetre_oeasc();
        }
        if (!this.all_areas_geojson) {
          setTimeout(tryAdd, 200);
        }
      };

      tryAdd();
    },

    addAreasLayers() {
      if (!this.all_areas_geojson) return;
      // clear existing
      this.clearAreasLayers();

      // create one geoJson layer per id_type so we can assign panes (z-index) per type
      const idSet = new Set();
      if (this.all_areas_geojson && Array.isArray(this.all_areas_geojson.features)) {
        this.all_areas_geojson.features.forEach((f) => {
          if (f && f.properties && typeof f.properties.id_type !== 'undefined')
            idSet.add(f.properties.id_type);
        });
      }

      // only keep id types that are requested in liste_layers (props now provide names)
      const idsToRender = Array.from(idSet).filter((id) => this.requestedIdTypes.has(id));

      idsToRender.forEach((id) => {
        const paneName = `pane-${id}`;
        const s = this.stylesById[id] || {};
        const z = s.zIndex || 200;
        this.createPaneIfNotExists(paneName, z);

        const layerByType = L.geoJSON(this.all_areas_geojson, {
          pane: paneName,
          filter: (feature) => feature.properties && feature.properties.id_type === id,
          style: (feature) => {
            const sd = this.stylesById[id] ||
              DEFAULT_STYLE || { color: '#000', weight: 1, fillColor: '#000', fillOpacity: 0.2 };
            return {
              color: sd.color || '#000',
              weight: typeof sd.weight === 'number' ? sd.weight : 1,
              opacity: typeof sd.opacity === 'number' ? sd.opacity : 1,
              fillColor: sd.fillColor || sd.color || '#000',
              fillOpacity: typeof sd.fillOpacity === 'number' ? sd.fillOpacity : 0.2,
            };
          },
        });

        this.areasLayerGroup.addLayer(layerByType);
      });

      // create labels (will be positioned by placeLabels to avoid overlaps)
      try {
        if (this.labelLayerGroup) this.labelLayerGroup.clearLayers();
        const features = this.all_areas_geojson.features.filter(
          (f) =>
            f &&
            f.properties &&
            typeof f.properties.id_type !== 'undefined' &&
            this.requestedIdTypes.has(f.properties.id_type)
        );
        for (const f of features) {
          try {
            const id = f.properties.id_type;
            let areaName = f.properties.area_name || f.properties.name || null;
            // met areaName en minuscule et capitalise la première lettre en majuscules
            if (areaName)
              areaName = areaName.charAt(0).toUpperCase() + areaName.slice(1).toLowerCase();
            if (!areaName) continue;
            const tmp = L.geoJSON(f);
            let center = null;
            try {
              const b = tmp.getBounds();
              if (b && b.isValid && b.isValid()) center = b.getCenter();
            } catch (e) {
              center = null;
            }
            if (!center) continue;

            const cfg = this.stylesById[id] || DEFAULT_STYLE;
            const textColor =
              cfg && cfg.fillColor ? cfg.fillColor : cfg && cfg.color ? cfg.color : '#000';
            const html = `<div class="area-label-box" style="background:rgba(255,255,255,0.5);border:1px solid ${textColor};padding:2px 6px;border-radius:4px;display:inline-block;white-space:nowrap;"><div class=\"area-label\" style=\"color:${textColor};font-size:18px;font-weight:700;white-space:nowrap;display:inline-block;\">${String(areaName)}</div></div>`;
            // store label item for later placement
            this.labelItems.push({ feature: f, center, html });
          } catch (e) {
            /* per-feature ignore */
          }
        }
      } catch (e) {
        /* ignore label creation errors */
      }

      // perform placement now
      this.placeLabels();

      // update legend after layers created
      this.updateLegend();
    },

    clearAreasLayers() {
      if (this.areasLayerGroup) this.areasLayerGroup.clearLayers();
      if (this.labelLayerGroup) this.labelLayerGroup.clearLayers();
      this.labelItems = [];
    },

    resolveLabels() {
      // simple greedy overlap resolver: show/hide labels based on pixel bbox collisions
      try {
        if (!this.map || !this.labelLayerGroup) return;
        const layers = this.labelLayerGroup.getLayers();
        const rects = [];
        for (const m of layers) {
          try {
            const el = m.getElement();
            if (!el) continue;
            // ensure visible before measuring
            el.style.display = '';
            const p = this.map.latLngToContainerPoint(m.getLatLng());
            const w = el.offsetWidth || 60;
            const h = el.offsetHeight || 16;
            const rect = { x: p.x - w / 2, y: p.y - h / 2, w, h, marker: m };
            rects.push(rect);
          } catch (e) {
            /* ignore per marker */
          }
        }

        // vérifies si deux rectangles se chevauchent
        const overlap = (a, b) =>
          !(a.x + a.w < b.x || b.x + b.w < a.x || a.y + a.h < b.y || b.y + b.h < a.y);
        // greedy: keep first, hide later overlaps
        for (let i = 0; i < rects.length; i++) {
            // si le marker a déjà été caché par un chevauchement précédent, on le skip pour éviter de cacher tous les markers qui suivent
          if (!rects[i].marker) continue;
          for (let j = i + 1; j < rects.length; j++) {
            if (!rects[j].marker) continue;
            // si chevauchement, cacher le marker j (le marker i est prioritaire car il est plus tôt dans la liste)
            if (overlap(rects[i], rects[j])) {
              const elj = rects[j].marker.getElement();
              if (elj) elj.style.display = 'none';
              rects[j].marker = null;
            }
          }
        }
      } catch (e) {
        /* ignore */
      }
    },

    measureLabelSize(html) {
      try {
        const div = document.createElement('div');
        div.style.position = 'absolute';
        div.style.left = '-9999px';
        div.style.top = '-9999px';
        div.style.visibility = 'hidden';
        div.innerHTML = html;
        div.className = 'area-label';
        document.body.appendChild(div);
        const w = div.offsetWidth || 60;
        const h = div.offsetHeight || 20;
        document.body.removeChild(div);
        return { w, h };
      } catch (e) {
        return { w: 60, h: 20 };
      }
    },

    placeLabels() {
      try {
        if (!this.map) return;
        if (!this.labelItems || !this.labelItems.length) return;
        // clear previous
        if (this.labelLayerGroup) this.labelLayerGroup.clearLayers();
        const placed = [];

        for (const it of this.labelItems) {
          try {
            const f = it.feature;
            const btmp = L.geoJSON(f).getBounds();
            if (!btmp || !btmp.isValid || !btmp.isValid()) continue;
            const latSpan = Math.abs(btmp.getNorth() - btmp.getSouth()) || 0.0001;
            const lngSpan = Math.abs(btmp.getEast() - btmp.getWest()) || 0.0001;
            const latOffset = latSpan * 0.08;
            const lngOffset = lngSpan * 0.08;

            const candidates = [
              L.latLng(btmp.getNorth() - latOffset, btmp.getEast() - lngOffset), // NE
              L.latLng(btmp.getNorth() - latOffset, btmp.getWest() + lngOffset), // NW
              L.latLng(btmp.getSouth() + latOffset, btmp.getEast() - lngOffset), // SE
              L.latLng(btmp.getSouth() + latOffset, btmp.getWest() + lngOffset), // SW
              it.center,
            ];

            const size = this.measureLabelSize(it.html);
            let placedMarker = null;
            for (const cand of candidates) {
              try {
                const p = this.map.latLngToContainerPoint(cand);
                const rect = { x: p.x - size.w / 2, y: p.y - size.h / 2, w: size.w, h: size.h };
                let collision = false;
                for (const r of placed) {
                  if (
                    !(
                      rect.x + rect.w < r.x ||
                      r.x + r.w < rect.x ||
                      rect.y + rect.h < r.y ||
                      r.y + r.h < rect.y
                    )
                  ) {
                    collision = true;
                    break;
                  }
                }
                if (!collision) {
                  const icon = L.divIcon({ html: it.html, className: 'area-label-wrapper' });
                  placedMarker = L.marker(cand, { icon: icon, interactive: false });
                  if (this.labelLayerGroup) this.labelLayerGroup.addLayer(placedMarker);
                  placed.push(rect);
                  break;
                }
              } catch (e) {
                /* try next candidate */
              }
            }
            // if none placed, skip label
          } catch (e) {
            /* per-label ignore */
          }
        }
      } catch (e) {
        /* ignore whole placement errors */
      }
    },

    // clean de la légende avant de la reconstruire (évite les doublons à chaque update)
    removeLegend() {
      try {
        if (this.legendControl && this.map) {
          this.map.removeControl(this.legendControl);
        }
      } catch (e) {
        /* ignore */
      }
      this.legendControl = null;
    },

    // supprime le marker de déclaration (centroid) s'il existe, utilisé avant d'en ajouter un nouveau pour éviter les doublons
    removeDeclarationMarker() {
      try {
        if (this.declarationMarker && this.map) {
          this.map.removeLayer(this.declarationMarker);
        }
      } catch (e) {
        /* ignore */
      }
      this.declarationMarker = null;
    },

    updateLegend() {
      // reconstruire la légende en fonction des couches actuellement affichées
      this.removeLegend();
      if (!this.map) return;

      // construire la liste des items à afficher dans la légende en fonction des id_types présents dans les données et de ceux demandés dans les props (via requestedIdTypes/requestedNames)
      const items = [];
      if (
        this.requestedNames &&
        this.requestedNames.size &&
        this.all_areas_geojson &&
        Array.isArray(this.all_areas_geojson.features)
      ) {
        // priorité aux noms (ex: COMMUNES) pour construire la légende, mais on vérifie que les id_types correspondants sont bien présents dans les données avant de les ajouter à la légende
        const presentIds = new Set(
          this.all_areas_geojson.features
            .map((f) => (f && f.properties ? f.properties.id_type : null))
            .filter((v) => v !== null)
        );
        for (const name of this.requestedNames) {
          const cfg = config_layers[name];
          if (!cfg) continue;
          if (!presentIds.has(cfg.id_type)) continue;
          items.push({ name, color: cfg.fillColor, label: cfg.legend || name });
        }
      } else if (
        this.requestedIdTypes &&
        this.requestedIdTypes.size &&
        this.all_areas_geojson &&
        Array.isArray(this.all_areas_geojson.features)
      ) {
        // si pas de noms demandés, on utilise les id_types pour construire la légende, en vérifiant aussi qu'ils sont présents dans les données
        const presentIds = new Set(
          this.all_areas_geojson.features
            .map((f) => (f && f.properties ? f.properties.id_type : null))
            .filter((v) => v !== null)
        );
        for (const id of this.requestedIdTypes) {
          if (!presentIds.has(id)) continue;
          const cfg = this.stylesById[id];
          const name = cfg
            ? Object.keys(config_layers).find(
                (k) => config_layers[k] && config_layers[k].id_type === id
              )
            : null;
          items.push({
            name: name || id,
            color: (cfg && cfg.fillColor) || '#000',
            label: (cfg && cfg.legend) || name || id,
          });
        }
      }

      if (!items.length) return;

      const LegendControl = L.Control.extend({
        options: { position: 'bottomright' },
        onAdd: function () {
          const div = L.DomUtil.create('div', 'map-legend leaflet-bar');
          div.style.padding = '6px';
          div.style.background = 'rgba(255,255,255,0.9)';
          div.style.borderRadius = '4px';
          div.style.maxHeight = '180px';
          div.style.overflow = 'auto';
          return div;
        },
      });

      this.legendControl = new LegendControl();
      this.legendControl.addTo(this.map);

      // remplir la légende avec les items (couleur + label)
      try {
        const container = this.legendControl.getContainer();
        items.forEach((it) => {
          const row = document.createElement('div');
          row.style.display = 'flex';
          row.style.alignItems = 'center';
          row.style.marginBottom = '6px';

          const sw = document.createElement('span');
          sw.style.display = 'inline-block';
          sw.style.width = '18px';
          sw.style.height = '12px';
          sw.style.marginRight = '8px';
          sw.style.background = it.color || '#000';
          sw.style.border = '1px solid rgba(0,0,0,0.2)';
          row.appendChild(sw);

          const lbl = document.createElement('span');
          lbl.innerText = it.label || it.name;
          row.appendChild(lbl);

          container.appendChild(row);
        });
      } catch (e) {
        console.warn('Erreur lors de la construction de la légende :', e);
      }
    },
  },
};
</script>

<style scoped>
#map {
  width: 100%;
}

.area-label-wrapper {
  pointer-events: none;
  white-space: nowrap !important;
}
.area-label {
  pointer-events: none;
  white-space: nowrap !important;
  max-width: none !important;
  overflow: visible !important;
  word-break: normal !important;
  overflow-wrap: normal !important;
  hyphens: none !important;
}

.area-label-box {
  pointer-events: none;
  white-space: nowrap !important;
}
</style>
