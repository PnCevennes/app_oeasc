<!--
  Carte des communes de la zone OEASC colorées selon la surface détruite (ha)
  pour une saison ou cumulée sur toutes les saisons. Au survol : montant indemnisé et nombre de dossiers.
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
      <span class="legende-item">
        <span class="legende-perimetre"></span>
        Périmètre OEASC
      </span>
    </div>
  </div>
</template>

<script>
import L from 'leaflet';
import { markRaw } from 'vue';
import 'leaflet/dist/leaflet.css';
import { config } from '@/config/config.js';
import { fetch_oeasc_perimetre } from '@/modules/declaration/utils/api_request.js';

// Fond de carte servi par le backend (proxy des tuiles IGN), comme map_declaration_simple.vue
const TILE_URL = `${config.URL_APPLICATION.replace(/\/$/, '')}/api/declaration/tiles/v2/{z}/{x}/{y}.png`;
const TILE_ATTRIBUTION = '&copy; <a href="http://www.ign.fr/">IGN</a>';

// contour du périmètre OEASC : sans remplissage pour ne pas fausser les couleurs des communes
const STYLE_PERIMETRE = { color: '#000000', weight: 3, opacity: 0.9, fill: false };

// classes de surface détruite (ha), de la plus forte à la plus faible :
// une commune prend la couleur de la première classe dont elle dépasse le seuil
const CLASSES = [
  { min: 10, color: '#000000', label: 'plus de 10 ha' },
  { min: 5, color: '#e53935', label: '5 à 10 ha' },
  { min: 1, color: '#fb8c00', label: '1 à 5 ha' },
  { min: 0, color: '#43a047', label: 'moins de 1 ha' },
];
// couleurs des classes, de la plus forte surface à la plus faible
const COULEURS = CLASSES.map((c) => c.color);
const CLASSE_NULLE = { color: '#ffffff', label: '0 ha' };

const classeSurface = (surface, classes) =>
  surface > 0 ? classes.find((c) => surface > c.min) : CLASSE_NULLE;

// quantile d'ordre p (0 à 1) d'une liste triée, par interpolation linéaire
const quantile = (valeursTriees, p) => {
  const position = (valeursTriees.length - 1) * p;
  const bas = Math.floor(position);
  const haut = Math.ceil(position);
  return valeursTriees[bas] + (valeursTriees[haut] - valeursTriees[bas]) * (position - bas);
};

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
    cumul: { default: false }, // true : surfaces cumulées sur toutes les saisons (autres seuils)
  },
  computed: {
    // En cumul, les seuils fixes d'une saison ne conviennent plus (presque toutes les
    // communes touchées dépassent 10 ha) : les seuils sont les quartiles des surfaces
    // cumulées des communes touchées, soit environ un quart de ces communes par classe.
    classesCumul() {
      const surfaces = ((this.geojson && this.geojson.features) || [])
        .map((f) => f.properties.surface_detruite)
        .filter((surface) => surface > 0)
        .sort((a, b) => a - b);
      if (!surfaces.length) {
        return [];
      }
      // seuils arrondis au dixième d'hectare pour que la légende corresponde exactement
      // au classement ; les doublons (peu de communes, valeurs égales) sont retirés
      const seuils = [0.75, 0.5, 0.25]
        .map((p) => Number(quantile(surfaces, p).toFixed(1)))
        .filter((seuil, i, liste) => seuil > 0 && liste.indexOf(seuil) === i);
      const bornes = [...seuils, 0]; // bornes basses, de la plus forte à la plus faible
      // les couleurs les plus fortes restent sur les classes les plus hautes
      return bornes.map((min, i) => {
        const max = bornes[i - 1];
        let label = `${nombre(min, 1)} à ${nombre(max, 1)} ha`;
        if (i === 0) {
          label = bornes.length > 1 ? `plus de ${nombre(min, 1)} ha` : 'plus de 0 ha';
        } else if (min === 0) {
          label = `jusqu'à ${nombre(max, 1)} ha`;
        }
        return { min, color: COULEURS[i], label };
      });
    },
    classesSurface() {
      return this.cumul ? this.classesCumul : CLASSES;
    },
    classes() {
      return [...this.classesSurface, CLASSE_NULLE];
    },
  },
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
      const classesSurface = this.classesSurface;
      this.layer = L.geoJSON(this.geojson, {
        style: (feature) => ({
          color: '#555555',
          weight: 1,
          fillColor: classeSurface(feature.properties.surface_detruite, classesSurface).color,
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

    // Ajoute le contour du périmètre OEASC, au-dessus des communes et non interactif
    // (il ne doit pas masquer les infobulles des communes)
    async afficherPerimetre() {
      const perimetre = await fetch_oeasc_perimetre();
      // la carte peut avoir été détruite pendant le chargement
      if (!perimetre || !this.map) {
        return;
      }
      this.map.createPane('perimetre-pane');
      this.map.getPane('perimetre-pane').style.zIndex = 450;
      this.map.getPane('perimetre-pane').style.pointerEvents = 'none';
      this.layerPerimetre = L.geoJSON(perimetre, {
        style: STYLE_PERIMETRE,
        pane: 'perimetre-pane',
        interactive: false,
      }).addTo(this.map);
    },
  },
  mounted() {
    // la carte et sa couche ne sont volontairement pas réactives (objets Leaflet)
    this.map = markRaw(L.map(this.$refs.map).setView([44.3, 3.7], 9));
    L.tileLayer(TILE_URL, { maxZoom: 18, opacity: 0.7, attribution: TILE_ATTRIBUTION }).addTo(
      this.map
    );
    this.afficherCommunes();
    this.afficherPerimetre();
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
.legende-perimetre {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 3px solid #000000;
}
</style>
