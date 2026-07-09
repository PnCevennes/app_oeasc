<!--


-->
<template>
  <div style="width: 100%; display: flex; flex-direction: row">
    <div
      :id="mapID"
      :ref="mapRef"
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

    mapID: {
      // id optionnel pour le conteneur de la carte, si pas fourni un id unique sera généré automatiquement
      type: String,
      required: false,
      default: null,
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
      mapRef: `ref-${this.mapID}`, // référence pour le conteneur de la carte, générée à partir de mapID
      geom_perimetre_oeasc: null, // geojson du périmètre oeasc, affiché en noir et non selectionnable. Affiché en permanence.
      all_areas_geojson: null, // GeoJSON de toutes les zones disponibles pour le type de carte sélectionné. Sert à afficher les pastilles sur la carte.
      areasLayerGroup: null, // groupe de couches Leaflet pour les différentes zones affichées (communes, forêts, etc), permet de les gérer plus facilement (ajout/suppression)
      requestedIdTypes: new Set(), // set des id_types à afficher, dérivé de liste_layers pour un accès plus facile lors du rendu
      requestedNames: new Set(), // set des noms de couches demandés dans liste_layers, utilisé pour certaines logiques spécifiques (ex: périmètre OEASC)
      stylesById: {}, // mapping id_type → config de style (color, fillColor, etc) pour un accès plus facile lors du rendu
      legendControl: null, // instance du contrôle de légende Leaflet, pour pouvoir le supprimer avant d'en recréer un nouveau à chaque update
      declarationMarker: null, // marker pour le centroid de la déclaration, affiché si declaration_data.centroid existe, mis à jour à chaque changement de déclaration
      labelLayerGroup: null, // groupe de couches pour les labels (noms des zones), permet de les gérer plus facilement et de les placer au dessus des autres couches
      labelItems: [], // liste des items de labels à placer, chaque item contient { feature, center, html } pour la feature à laquelle le label correspond, son centre géographique et le HTML du label à afficher. La placement effectif est fait dans placeLabels() qui résout les chevauchements.
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

  created() {},

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

  beforeUnmount() {
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
      // initialiser la carte Leaflet dans le conteneur spécifié par mapID
      const container = document.getElementById(this.mapID);
      if (!container) {
        setTimeout(() => this.initMap(), 50);
        return;
      }
      // création de la carte avec contrôle de zoom activé
      this.map = L.map(container, { zoomControl: true, preferCanvas: true, renderer: L.canvas() });

      // couche de fond basique
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        crossOrigin: true,
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
                  // this.declarationMarker = L.marker([lat, lng], { zIndexOffset: 1000, preferCanvas: true  });
                  // this.declarationMarker.addTo(this.map);
                  L.circleMarker([lat, lng], {
                    radius: 10,
                    fillColor: '#ff0000',
                    color: '#333333',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.8,
                    pane: 'markerPane',
                  }).addTo(this.map);
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
      // efface l'existant pour repartir sur une base propre (utile notamment quand on change de déclaration ou de liste_layers)
      this.clearAreasLayers();

      // Créé des couches Leaflet pour chaque type d'area présent dans all_areas_geojson, en utilisant les styles définis dans config_layers (ou le style par défaut si pas de config spécifique). Les couches sont filtrées pour ne garder que les features du type correspondant, et ajoutées à areasLayerGroup. Les panes sont utilisés pour gérer l'ordre d'empilement des couches selon leur zIndex.
      const idSet = new Set();
      if (this.all_areas_geojson && Array.isArray(this.all_areas_geojson.features)) {
        this.all_areas_geojson.features.forEach((f) => {
          if (f && f.properties && typeof f.properties.id_type !== 'undefined')
            idSet.add(f.properties.id_type);
        });
      }

      // Ne garde que les id_types qui sont à la fois présents dans les données et demandés dans requestedIdTypes (filtrage nécessaire car il peut y avoir des id_types dans les données pour lesquels on n'a pas de style défini, et qu'on ne veut pas afficher)
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

      // Créé des markers pour les labels (noms des zones) à partir des features de all_areas_geojson, en filtrant pour ne garder que les features des types demandés dans requestedIdTypes. Le HTML du label est stylisé en fonction du style de la couche correspondante (couleur de texte basée sur fillColor ou color), et stocké dans labelItems pour être placé ensuite avec placeLabels() qui gère les chevauchements.
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
            // place le label à son centre géographique, le placement effectif et la résolution des chevauchements seront gérés ensuite dans placeLabels()
            this.labelItems.push({ feature: f, center, html });
          } catch (e) {
            console.warn('Erreur création label pour feature', f, e);
          }
        }
      } catch (e) {
        console.warn('Erreur création des labels', e);
      }

      // place les labels en résolvant les chevauchements pour éviter que les labels ne se chevauchent entre eux ou avec d'autres labels, en utilisant
      this.placeLabels();

      // Mise à jour de la légende après avoir ajouté les couches, pour s'assurer que la légende reflète les couches actuellement affichées
      this.updateLegend();
    },

    clearAreasLayers() {
      if (this.areasLayerGroup) this.areasLayerGroup.clearLayers();
      if (this.labelLayerGroup) this.labelLayerGroup.clearLayers();
      this.labelItems = [];
    },

    resolveLabels() {
      // résout les chevauchements de labels en cachant les labels qui se chevauchent avec d'autres labels prioritaires (priorité donnée à l'ordre dans la liste, le premier est prioritaire sur les suivants)
      try {
        if (!this.map || !this.labelLayerGroup) return;
        const layers = this.labelLayerGroup.getLayers();
        const rects = [];
        for (const m of layers) {
          try {
            const el = m.getElement();
            if (!el) continue;
            // s'assure que le label est affiché pour pouvoir mesurer sa taille et sa position, il sera caché plus tard s'il se chevauche avec un label prioritaire
            el.style.display = '';
            const p = this.map.latLngToContainerPoint(m.getLatLng());
            const w = el.offsetWidth || 60;
            const h = el.offsetHeight || 16;
            const rect = { x: p.x - w / 2, y: p.y - h / 2, w, h, marker: m };
            rects.push(rect);
          } catch (e) {
            console.warn('Erreur mesure label', m, e);
          }
        }

        // vérifies si deux rectangles se chevauchent
        const overlap = (a, b) =>
          !(a.x + a.w < b.x || b.x + b.w < a.x || a.y + a.h < b.y || b.y + b.h < a.y);
        // garde les labels qui ne se chevauchent pas avec des labels prioritaires, en parcourant la liste dans l'ordre et en cachant les labels qui se chevauchent avec un label déjà prioritaire (le premier de la liste est prioritaire sur les suivants)
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
        console.warn('Erreur résolution chevauchement labels', e);
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
        // efface les labels existants pour repartir sur une base propre avant de replacer les labels à leurs nouvelles positions (utile notamment lors du zoom/pan où les positions changent, et pour éviter les doublons)
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
                // console.warn('Erreur placement label candidat', cand, e);
              }
            }
            // si aucun candidat n'a pu être placé sans collision, on place le label à sa position centrale par défaut (même si ça peut générer des chevauchements, au moins le label est affiché)
          } catch (e) {
            console.warn('Erreur création label pour feature', f, e);
          }
        }
      } catch (e) {
        console.warn('Erreur placement des labels', e);
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
        console.warn('Erreur suppression marker déclaration :', e);
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

    // Méthode utilitaire pour obtenir l'instance de la carte depuis l'extérieur du composant,
    // utile pour l'export en pdf par exemple
    getMapInstance() {
      return this.map;
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
