<!--
  Carte des communes de la zone OEASC colorées selon la mesure de l'onglet choisi (montant, surface, volume, surface remise en état)
  pour une saison ou cumulée sur toutes les saisons. Au survol : montant indemnisé et nombre de dossiers.
-->
<template>
  <div>
    <div class="carte-wrapper">
      <div
        ref="map"
        class="map-container"
        :style="`height:${height}; width:100%; z-index:0`"
      ></div>
      <div
        v-if="loading"
        class="carte-chargement"
      >
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
        ></v-progress-circular>
      </div>
    </div>
    <div class="options-contours">
      <v-checkbox
        v-model="afficherContourOeasc"
        label="Contour de l'OEASC"
        density="compact"
        hide-details
      ></v-checkbox>
      <v-checkbox
        v-model="afficherContoursUg"
        label="Contours des unités de gestion (secteurs)"
        density="compact"
        hide-details
      ></v-checkbox>
    </div>
    <div class="legende">
      <b>{{ mesureCourante.titre }} :</b>
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
      <span
        v-if="afficherContourOeasc"
        class="legende-item"
      >
        <span class="legende-perimetre"></span>
        Périmètre OEASC
      </span>
      <span
        v-if="afficherContoursUg"
        class="legende-item"
      >
        <span class="legende-ug"></span>
        Unités de gestion
      </span>
    </div>
  </div>
</template>

<script>
import L from 'leaflet';
import { markRaw } from 'vue';
import 'leaflet/dist/leaflet.css';
import { config } from '@/config/config.js';
import { apiRequest } from '@/core/js/data/api.js';
import { fetch_oeasc_perimetre } from '@/modules/declaration/utils/api_request.js';

// Fond de carte servi par le backend (proxy des tuiles IGN), comme map_declaration_simple.vue
const TILE_URL = `${config.URL_APPLICATION.replace(/\/$/, '')}/api/declaration/tiles/v2/{z}/{x}/{y}.png`;
const TILE_ATTRIBUTION = '&copy; <a href="http://www.ign.fr/">IGN</a>';

// contour du périmètre OEASC : sans remplissage pour ne pas fausser les couleurs des communes
const STYLE_UG = { color: '#1e88ff', weight: 2.5, opacity: 1, fill: false };
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

const classeValeur = (valeur, classes) =>
  valeur > 0 ? classes.find((c) => valeur > c.min) || classes[classes.length - 1] : CLASSE_NULLE;

// mesures affichables (un onglet chacune) : propriété du geojson, unité, décimales
const MESURES = [
  { cle: 'montant', onglet: 'Par montant', titre: 'Montant indemnisé', propriete: 'montant_total', unite: '€', decimales: 0 },
  { cle: 'surface', onglet: 'Par surface', titre: 'Surface détruite', propriete: 'surface_detruite', unite: 'ha', decimales: 1 },
  { cle: 'volume', onglet: 'Par volume', titre: 'Volume détruit', propriete: 'volume_detruit', unite: 'qtx', decimales: 1 },
  { cle: 'remise', onglet: 'Par surface remise en état', titre: 'Surface remise en état', propriete: 'surface_ressemis', unite: 'ha', decimales: 1 },
];

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
    mesure: { default: 'montant' }, // montant, surface, volume ou remise (onglet de la page)
    // FeatureCollection des communes : properties { nom, surface_detruite, montant_total, nb_dossiers }
    geojson: { default: null },
    height: { default: '600px' },
    loading: { default: false }, // true : spinner par-dessus la carte
    cumul: { default: false }, // true : surfaces cumulées sur toutes les saisons (autres seuils)
  },
  data: () => ({
    afficherContourOeasc: true,
    afficherContoursUg: false,
  }),
  computed: {
    mesureCourante() {
      return MESURES.find((m) => m.cle === this.mesure);
    },
    // Les seuils fixes ne valent que pour la surface détruite d'une saison. Sinon
    // (autres mesures, ou cumul), les seuils sont les quartiles des valeurs non nulles
    // des communes, soit environ un quart de ces communes par classe.
    classesQuantiles() {
      const { propriete, unite, decimales } = this.mesureCourante;
      const valeurs = ((this.geojson && this.geojson.features) || [])
        .map((f) => f.properties[propriete])
        .filter((v) => v > 0)
        .sort((a, b) => a - b);
      if (!valeurs.length) {
        return [];
      }
      // seuils arrondis pour que la légende corresponde exactement au classement ;
      // les doublons (peu de communes, valeurs égales) sont retirés
      const seuils = [0.75, 0.5, 0.25]
        .map((p) => Number(quantile(valeurs, p).toFixed(decimales)))
        .filter((seuil, i, liste) => seuil > 0 && liste.indexOf(seuil) === i);
      const bornes = [...seuils, 0]; // bornes basses, de la plus forte à la plus faible
      return bornes.map((min, i) => {
        const max = bornes[i - 1];
        let label = `${nombre(min, decimales)} à ${nombre(max, decimales)} ${unite}`;
        if (i === 0) {
          label = bornes.length > 1 ? `plus de ${nombre(min, decimales)} ${unite}` : `plus de 0 ${unite}`;
        } else if (min === 0) {
          label = `jusqu'à ${nombre(max, decimales)} ${unite}`;
        }
        return { min, color: COULEURS[i], label };
      });
    },
    classesSurface() {
      return this.mesure === 'surface' && !this.cumul ? CLASSES : this.classesQuantiles;
    },
    classes() {
      return [...this.classesSurface, { ...CLASSE_NULLE, label: `0 ${this.mesureCourante.unite}` }];
    },
  },
  watch: {
    geojson() {
      this.afficherCommunes();
    },
    mesure() {
      this.afficherCommunes();
    },
    afficherContourOeasc() {
      this.majContour('layerPerimetre', this.afficherContourOeasc);
    },
    afficherContoursUg() {
      this.majContour('layerUg', this.afficherContoursUg);
      if (this.afficherContoursUg && !this.layerUg) {
        this.chargerUg();
      }
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
      const { propriete } = this.mesureCourante;
      this.layer = L.geoJSON(this.geojson, {
        style: (feature) => ({
          color: '#555555',
          weight: 1,
          fillColor: classeValeur(feature.properties[propriete], classesSurface).color,
          fillOpacity: 0.75,
        }),
        onEachFeature: (feature, layer) => {
          const p = feature.properties;
          layer.bindTooltip(
            `<b>${p.nom}</b><br/>` +
              `Total indemnisé : <b>${nombre(p.montant_total, 2)} €</b><br/>` +
              `Nombre de dossiers : <b>${nombre(p.nb_dossiers)}</b><br/>` +
              `Surface détruite : <b>${nombre(p.surface_detruite, 2)} ha</b><br/>` +
              `Volume détruit : <b>${nombre(p.volume_detruit, 2)} qtx</b><br/>` +
              `Surface remise en état : <b>${nombre(p.surface_ressemis, 2)} ha</b>`,
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

    // Affiche ou masque une couche de contour déjà chargée
    majContour(nomCouche, visible) {
      const couche = this[nomCouche];
      if (!couche || !this.map) {
        return;
      }
      if (visible) {
        couche.addTo(this.map);
      } else {
        this.map.removeLayer(couche);
      }
    },

    // Crée le pane (au-dessus des communes, non interactif) des contours
    creerPaneContours() {
      if (!this.map.getPane('perimetre-pane')) {
        this.map.createPane('perimetre-pane');
        this.map.getPane('perimetre-pane').style.zIndex = 450;
        this.map.getPane('perimetre-pane').style.pointerEvents = 'none';
      }
    },

    // Charge les contours des unités de gestion, à la première activation de l'option
    async chargerUg() {
      if (this.chargementUg) {
        return;
      }
      this.chargementUg = true;
      try {
        const ug = await apiRequest('GET', 'api/agricole/results/ug');
        if (!ug || !this.map) {
          return;
        }
        this.creerPaneContours();
        this.layerUg = L.geoJSON(ug, {
          style: STYLE_UG,
          pane: 'perimetre-pane',
          interactive: false,
          // nom de l'unité affiché en permanence au centre de son contour
          onEachFeature: (feature, layer) =>
            layer.bindTooltip(feature.properties.nom, {
              permanent: true,
              direction: 'center',
              className: 'etiquette-ug',
            }),
        });
        if (this.afficherContoursUg) {
          this.layerUg.addTo(this.map);
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des unités de gestion', error);
      } finally {
        this.chargementUg = false;
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
      this.creerPaneContours();
      this.layerPerimetre = L.geoJSON(perimetre, {
        style: STYLE_PERIMETRE,
        pane: 'perimetre-pane',
        interactive: false,
      });
      if (this.afficherContourOeasc) {
        this.layerPerimetre.addTo(this.map);
      }
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

<style>
/* non scoped : l'infobulle Leaflet est créée hors du composant */
.leaflet-tooltip.etiquette-ug {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #1e88ff;
  color: #0d47a1;
  font-weight: bold;
  pointer-events: none;
}
</style>

<style scoped>
.carte-wrapper {
  position: relative;
}
.carte-chargement {
  position: absolute;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.6);
}
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
.options-contours {
  display: flex;
  flex-wrap: wrap;
  gap: 0 24px;
  margin-top: 4px;
}
.legende-ug {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2.5px solid #1e88ff;
}
.legende-perimetre {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 3px solid #000000;
}
</style>
