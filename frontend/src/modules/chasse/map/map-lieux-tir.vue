<!--
  Carte des lieux de tir (page admin « Gestion des lieux de tirs »).
  Affiche uniquement les lieux passés dans `lieux` (ceux cochés dans la liste) et les contours
  passés dans `contours` (commune / zone indicative / zone cynégétique du filtre actif).
  Un clic sur un lieu ouvre un encart avec ses informations et ses synonymes.
-->
<template>
  <div
    ref="map"
    class="map-container"
    :style="`height:${height}; width:100%; z-index:0`"
  ></div>
</template>

<script>
import L from 'leaflet';
import { markRaw } from 'vue';
import 'leaflet/dist/leaflet.css';
import { config } from '@/config/config.js';

// Fond de carte servi par le backend (proxy des tuiles IGN)
const TILE_URL = `${config.URL_APPLICATION.replace(/\/$/, '')}/api/declaration/tiles/v2/{z}/{x}/{y}.png`;
const TILE_ATTRIBUTION = '&copy; <a href="http://www.ign.fr/">IGN</a>';

// styles des contours, sans remplissage
const STYLES_CONTOUR = {
  commune: { color: '#1e88ff', weight: 3, opacity: 1, fill: false },
  zone_indicative: { color: '#e53935', weight: 3, opacity: 1, fill: false },
  zone_cynegetique: { color: '#000000', weight: 3, opacity: 0.9, fill: false },
};
const STYLE_ENVELOPPE = {
  color: '#e53935',
  weight: 2,
  opacity: 0.9,
  fillColor: '#e53935',
  fillOpacity: 0.2,
};
const STYLE_POINT = {
  radius: 7,
  color: '#ffffff',
  weight: 2,
  fillColor: '#e53935',
  fillOpacity: 0.95,
};

// largeur fixe de l'encart (sinon Leaflet l'ajuste au contenu : elle varie d'un lieu à l'autre)
const LARGEUR_POPUP = { minWidth: 300, maxWidth: 300 };

// les noms viennent de la base : à échapper avant insertion dans le HTML du popup
const echappe = (texte) =>
  String(texte ?? '').replace(
    /[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]
  );

const contenuPopup = (p) => {
  const ligne = (label, valeur) =>
    valeur ? `<div><b>${label} :</b> ${echappe(valeur)}</div>` : '';
  const synonymes = p.synonymes && p.synonymes.length
    ? `<div><b>Synonymes (${p.synonymes.length}) :</b><ul style="margin:2px 0 0 18px;padding:0">` +
      p.synonymes.map((s) => `<li>${echappe(s)}</li>`).join('') +
      '</ul></div>'
    : '<div><i>Aucun synonyme</i></div>';
  return (
    `<div style="max-height:260px;overflow:auto;overflow-wrap:anywhere"><b>${echappe(p.nom_lieu_tir)}</b>` +
    ligne('Code', p.code_lieu_tir) +
    ligne('Commune', p.nom_commune) +
    ligne('Zone indicative', p.nom_zone_indicative) +
    ligne('Zone cynégétique', p.nom_zone_cynegetique) +
    synonymes +
    '</div>'
  );
};

export default {
  name: 'MapLieuxTir',
  props: {
    // liste de Features (lieux de tir) à afficher
    lieux: { type: Array, default: () => [] },
    // liste de Features (contours) ; properties.type = commune | zone_indicative | zone_cynegetique
    contours: { type: Array, default: () => [] },
    // id_lieu_tir à mettre en avant (ouvre son encart)
    lieuActif: { type: Number, default: null },
    height: { type: String, default: '650px' },
    // mode édition : { points: [[lng, lat], ...] } ; les points sont déplaçables (glisser),
    // ajoutés (clic sur la carte) et supprimés (clic droit ou double-clic sur un point).
    // Les modifications sont émises par l'évènement `update:points`.
    edition: { type: Object, default: null },
  },
  emits: ['update:points'],
  watch: {
    edition: {
      deep: true,
      handler() {
        this.majEdition();
      },
    },
    lieux() {
      this.majLieux();
    },
    contours() {
      this.majContours();
    },
    lieuActif(id) {
      const couche = id != null && this.couchesLieux.get(id);
      if (couche) {
        couche.openPopup();
      }
    },
  },
  methods: {
    // Ajoute / retire les couches pour correspondre à `lieux`, sans tout redessiner
    majLieux() {
      if (!this.map) {
        return;
      }
      const voulus = new Map(this.lieux.map((f) => [f.properties.id_lieu_tir, f]));
      for (const [id, couche] of this.couchesLieux) {
        // lieu retiré, ou rechargé depuis le serveur (nouvel objet) : on redessine
        if (!voulus.has(id) || this.featuresLieux.get(id) !== voulus.get(id)) {
          this.groupeLieux.removeLayer(couche);
          this.couchesLieux.delete(id);
          this.featuresLieux.delete(id);
        }
      }
      const ajoutes = [];
      for (const [id, feature] of voulus) {
        if (this.couchesLieux.has(id)) {
          continue;
        }
        // enveloppe (zone tampon pour 1-2 points, enveloppe convexe au-delà) sous les points
        const enveloppe = L.geoJSON(
          { type: 'Feature', geometry: feature.properties.enveloppe },
          { style: STYLE_ENVELOPPE }
        );
        const points = L.geoJSON(feature, {
          pointToLayer: (_, latlng) => L.circleMarker(latlng, STYLE_POINT),
        });
        const couche = L.featureGroup([enveloppe, points]);
        couche.bindPopup(contenuPopup(feature.properties), LARGEUR_POPUP);
        this.couchesLieux.set(id, couche);
        this.featuresLieux.set(id, feature);
        this.groupeLieux.addLayer(couche);
        ajoutes.push(couche);
      }
      // cadrage sur l'ensemble des lieux affichés dès qu'un lieu est ajouté (et non sur le seul
      // dernier coché) ; retirer un lieu ne déplace pas la carte
      if (ajoutes.length) {
        const bounds = this.groupeLieux.getBounds();
        if (bounds.isValid()) {
          this.map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
        }
      }
    },

    // Mode édition : les lieux « normaux » sont masqués, seuls les points édités sont affichés
    majEdition() {
      if (!this.map) {
        return;
      }
      const points = this.edition ? this.edition.points : null;
      this.groupeEdition.clearLayers();
      if (!points) {
        if (!this.map.hasLayer(this.groupeLieux)) {
          this.map.addLayer(this.groupeLieux);
        }
        this.map.getContainer().style.cursor = '';
        return;
      }
      this.map.removeLayer(this.groupeLieux);
      this.map.closePopup();
      this.map.getContainer().style.cursor = 'crosshair';
      if (points.length >= 2) {
        const hull = L.polygon(
          points.map(([lng, lat]) => [lat, lng]),
          { ...STYLE_ENVELOPPE, interactive: false }
        );
        this.groupeEdition.addLayer(hull);
      }
      points.forEach(([lng, lat], i) => {
        const marker = L.marker([lat, lng], {
          draggable: true,
          icon: L.divIcon({
            className: 'point-edition',
            iconSize: [18, 18],
            iconAnchor: [9, 9],
          }),
        });
        marker.bindTooltip('Glisser pour déplacer · clic droit pour supprimer', {
          direction: 'top',
          offset: [0, -8],
        });
        marker.on('dragend', () => {
          const { lat: la, lng: ln } = marker.getLatLng();
          this.emettre(points.map((p, j) => (j === i ? [ln, la] : p)));
        });
        marker.on('contextmenu', () => this.emettre(points.filter((_, j) => j !== i)));
        marker.on('dblclick', (e) => {
          L.DomEvent.stop(e);
          this.emettre(points.filter((_, j) => j !== i));
        });
        this.groupeEdition.addLayer(marker);
      });
    },
    emettre(points) {
      this.$emit('update:points', points);
    },
    // cadre la carte sur les points en cours d'édition
    cadrerEdition() {
      const points = this.edition && this.edition.points;
      if (this.map && points && points.length) {
        this.map.fitBounds(
          L.latLngBounds(points.map(([lng, lat]) => [lat, lng])),
          { padding: [60, 60], maxZoom: 16 }
        );
      }
    },

    majContours() {
      if (!this.map) {
        return;
      }
      this.groupeContours.clearLayers();
      for (const feature of this.contours) {
        this.groupeContours.addLayer(
          L.geoJSON(feature, {
            style: STYLES_CONTOUR[feature.properties.type],
            pane: 'contours-pane',
            interactive: false,
          })
        );
      }
      const bounds = this.groupeContours.getBounds();
      if (this.contours.length && bounds.isValid()) {
        this.map.fitBounds(bounds, { padding: [20, 20] });
      }
    },
  },
  mounted() {
    // objets Leaflet volontairement non réactifs
    this.map = markRaw(L.map(this.$refs.map).setView([44.3, 3.7], 9));
    L.tileLayer(TILE_URL, { maxZoom: 18, opacity: 0.7, attribution: TILE_ATTRIBUTION }).addTo(
      this.map
    );
    // contours sous les lieux et non interactifs (ne masquent pas les clics)
    this.map.createPane('contours-pane');
    this.map.getPane('contours-pane').style.zIndex = 450;
    this.map.getPane('contours-pane').style.pointerEvents = 'none';

    this.couchesLieux = new Map();
    this.featuresLieux = new Map();
    this.groupeEdition = L.featureGroup().addTo(this.map);
    // clic sur la carte en mode édition : ajoute un point
    this.map.on('click', (e) => {
      if (this.edition && this.edition.points) {
        this.emettre([...this.edition.points, [e.latlng.lng, e.latlng.lat]]);
      }
    });
    this.map.doubleClickZoom.disable();
    this.groupeContours = L.featureGroup().addTo(this.map);
    this.groupeLieux = L.featureGroup().addTo(this.map);
    this.majContours();
    this.majLieux();
    this.majEdition();
    this.cadrerEdition();

    // la taille du conteneur change après l'initialisation (mise en page Vuetify, redimensionnement
    // de la fenêtre) : sans recalcul, seule une partie de la carte reçoit des tuiles (reste grise)
    this.$nextTick(() => this.map && this.map.invalidateSize());
    if (typeof ResizeObserver !== 'undefined') {
      this.observateur = new ResizeObserver(() => this.map && this.map.invalidateSize());
      this.observateur.observe(this.$refs.map);
    }
  },
  beforeUnmount() {
    if (this.observateur) {
      this.observateur.disconnect();
      this.observateur = null;
    }
    if (this.map) {
      this.map.remove();
      this.map = null;
    }
  },
};
</script>

<style>
/* point déplaçable du mode édition (non scoped : l'icône est créée par Leaflet) */
.point-edition {
  background: #e53935;
  border: 3px solid #fff;
  border-radius: 50%;
  box-shadow: 0 0 0 1px #555;
  cursor: move;
}
</style>
