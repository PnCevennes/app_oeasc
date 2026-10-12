<!--
  Carte des communes de la zone OEASC colorées selon la surface détruite (ha)
  pour une saison. Au survol : montant indemnisé et nombre de dossiers.
-->
<template>
  <div>
    <div
      ref="map"
      class="map-container"
      :style="`height:${height}; width:100%; z-index:0`"
    ></div>
    <div class="legende">
      <b>Surface détruite :</b>
      <span
        v-for="classe of classes"
        :key="classe.label"
        class="legende-item"
      >
        <span
          class="legende-couleur"
          :style="`background-color:${classe.color}`"
        ></span>
        {{ classe.label }}
      </span>
    </div>
  </div>
</template>

<script>
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { config } from '@/config/config.js';

// Fond de carte servi par le backend (proxy des tuiles IGN), comme map_declaration_simple.vue
const TILE_URL = `${config.URL_APPLICATION.replace(/\/$/, '')}/api/declaration/tiles/v2/{z}/{x}/{y}.png`;
const TILE_ATTRIBUTION = '&copy; <a href="http://www.ign.fr/">IGN</a>';

// classes de surface détruite (ha), de la plus forte à la plus faible :
// une commune prend la couleur de la première classe dont elle dépasse le seuil
const CLASSES = [
  { min: 10, color: '#000000', label: 'plus de 10 ha' },
  { min: 5, color: '#e53935', label: '5 à 10 ha' },
  { min: 1, color: '#fb8c00', label: '1 à 5 ha' },
  { min: 0, color: '#43a047', label: 'moins de 1 ha' },
];
const CLASSE_NULLE = { color: '#ffffff', label: '0 ha' };

const classeSurface = (surface) =>
  surface > 0 ? CLASSES.find((c) => surface > c.min) : CLASSE_NULLE;

const nombre = (valeur, decimales = 0) =>
  Number(valeur || 0).toLocaleString('fr-FR', {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  });

export default {
  name: 'map_degats_communes',
  props: {
    // FeatureCollection des communes : properties { nom, surface_detruite, montant_total, nb_dossiers }
    geojson: { default: null },
    height: { default: '600px' },
  },
  data: () => ({
    classes: [...CLASSES, CLASSE_NULLE],
  }),
  watch: {
    geojson() {
      this.afficherCommunes();
    },
  },
  methods: {
    afficherCommunes() {
      if (!this.map) {
        return;
      }
      if (this.layer) {
        this.map.removeLayer(this.layer);
        this.layer = null;
      }
      if (!this.geojson || !this.geojson.features || !this.geojson.features.length) {
        return;
      }
      this.layer = L.geoJSON(this.geojson, {
        style: (feature) => ({
          color: '#555555',
          weight: 1,
          fillColor: classeSurface(feature.properties.surface_detruite).color,
          fillOpacity: 0.75,
        }),
        onEachFeature: (feature, layer) => {
          const p = feature.properties;
          layer.bindTooltip(
            `<b>${p.nom}</b><br/>` +
              `Total indemnisé : <b>${nombre(p.montant_total, 2)} €</b><br/>` +
              `Nombre de dossiers : <b>${nombre(p.nb_dossiers)}</b><br/>` +
              `Surface détruite : <b>${nombre(p.surface_detruite, 2)} ha</b>`,
            { sticky: true }
          );
          layer.on('mouseover', () => layer.setStyle({ weight: 3, color: '#1565c0' }));
          layer.on('mouseout', () => this.layer && this.layer.resetStyle(layer));
        },
      }).addTo(this.map);

      // cadrage sur les communes au premier affichage seulement : changer de
      // saison ne doit pas déplacer la carte
      if (!this.cadre) {
        this.map.fitBounds(this.layer.getBounds());
        this.cadre = true;
      }
    },
  },
  mounted() {
    // la carte et sa couche ne sont volontairement pas réactives (objets Leaflet)
    this.map = L.map(this.$refs.map, { scrollWheelZoom: false }).setView([44.3, 3.7], 9);
    L.tileLayer(TILE_URL, { maxZoom: 18, opacity: 0.7, attribution: TILE_ATTRIBUTION }).addTo(
      this.map
    );
    this.afficherCommunes();
  },
  beforeUnmount() {
    if (this.map) {
      this.map.remove();
      this.map = null;
    }
  },
};
</script>

<style scoped>
.legende {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px 18px;
  margin-top: 8px;
}
.legende-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.legende-couleur {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 1px solid #555555;
}
</style>
