<!--
  Composant VueJS : base-map.vue

  Ce composant représente une carte interactive avec plusieurs fonctionnalités :
  - Affichage de la carte principale dans un conteneur avec une hauteur dynamique.
  - Si la variable 'test' est vraie, la carte est affichée avec des options supplémentaires :
    - Bouton d'exportation d'image de la carte, affiché si 'exportImg' est défini.
    - Ouverture d'un dialogue contenant un formulaire générique pour configurer l'exportation.
    - Affichage de la légende de la carte via le composant 'map-legend', utilisant la configuration du service de carte.
  - Affichage dynamique de formulaires de sélection associés à la carte :
    - Pour chaque élément dans 'configSelects', si la configuration et le modèle de base existent, un formulaire de liste est affiché.
  - Un slot nommé 'aside' permet d'insérer du contenu additionnel à côté de la carte.

  Props et données utilisées :
  - 'computedHeight' : hauteur calculée pour le conteneur de la carte.
  - 'mapId' : identifiant unique pour la carte.
  - 'config' : configuration de la carte.
  - 'test' : condition d'affichage de la carte.
  - 'exportImg' : contrôle la disponibilité de l'exportation d'image.
  - 'bExportMap' : contrôle l'ouverture du dialogue d'exportation.
  - 'configFormExportMap' : configuration du formulaire d'exportation.
  - 'mapService' : service de gestion de la carte, utilisé pour la légende et les formulaires.
  - 'configSelects' : configurations des formulaires de sélection associés à la carte.

  Structure :
  - <div class="map-container"> : conteneur principal de la carte.
    - <div class="map"> : carte interactive et ses options.
    - <map-legend> : composant affichant la légende de la carte.
    - <list-form> : formulaires de sélection dynamiques.
    - <slot name="aside"> : emplacement pour du contenu additionnel.
-->

<template>
  <div>
    <div
      class="map-container"
      :style="`height:${computedHeight}`"
    >
      <div
        v-if="test"
        class="map"
        :ref="mapId"
        :id="mapId"
        :config="config"
        :style="`height:${computedHeight}; z-index:0;`"
      >
        <div
          v-if="exportImg !== undefined"
          class="map-export"
        >
          <v-btn
            icon
            @click="bExportMap = true"
          >
            <v-icon>image</v-icon>
          </v-btn>
          <v-dialog
            max-width="1400px"
            v-model="bExportMap"
          >
            <v-card v-if="bExportMap">
              <generic-form
                class="edit-dialog"
                :config="configFormExportMap"
              ></generic-form>
            </v-card>
          </v-dialog>
        </div>

        <map-legend :config="(mapService && mapService._config) || {}"></map-legend>
      </div>

      <div>
        <div
          v-for="[key, configSelect] of Object.entries(configSelects)"
          :key="key"
        >
          <div
            v-if="configSelect && mapService && mapService.baseModel"
            class="map-select"
          >
            <list-form
              :baseModel="mapService.baseModel"
              :config="configSelect"
            ></list-form>
          </div>
        </div>
        <div>
          <slot name="aside"></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineAsyncComponent } from 'vue';
import { MapService } from '@/components/map/map-service.js';
import listForm from '@/components/form/list-form.vue';
import mapLegend from './map-legend.vue';
import configFormExportMap from './config/form-export-map.js';
// base-map est monté sur toutes les pages carte ; GenericForm n'est affiché que dans le dialogue
// d'export (v-if="bExportMap"), donc chargé à la demande plutôt qu'à chaque affichage de carte.
const GenericForm = defineAsyncComponent(() => import('@/components/form/generic-form.vue'));

export default {
  name: 'baseMap',
  components: { listForm, mapLegend, GenericForm },
  data: () => ({
    bInit: false, // Indique si la carte a été initialisée ou non (booléen) bInit: false, // true si la carte est initialisée, false sinon
    mapService: null, // Référence au service de gestion de la carte mapService: null, // objet du service de la carte, initialisé plus tard
    configSelects: {}, // Configuration des éléments de sélection sur la carte configSelects: {}, // objet contenant les configurations des sélections
    bExportMap: false, // Indique si l'export de la carte est activé bExportMap: false, // true si l'export est activé, false sinon
    test: true, // Variable de test pour le développement test: true // utilisé pour les tests ou le débogage
  }),
  props: ['config', 'mapId', 'preConfigName', 'height', 'fillHeight', 'exportImg'],
  watch: {
    height() {
      this.test = false;
      setTimeout(() => {
        this.test = true;
        setTimeout(() => {
          this.mapService.init();
        }, 100);
      });
    },
  },
  methods: {
    /**
     * Initialise la sélection d'un layer sur la carte.
     *
     * Cette méthode est appelée lorsqu'un layer est sélectionné par l'utilisateur.
     * Elle effectue les opérations suivantes :
     * 1. Récupère la clé du layer sélectionné à partir de l'événement.
     * 2. Configure le layer sélectionné via le service `mapService` en appelant la méthode `configSelect`.
     * 3. Met à jour l'objet `configSelects` avec la nouvelle configuration du layer sélectionné.
     * 4. Force la réactivité de l'objet `configSelects` en créant une nouvelle référence.
     *
     * @param {Object} $event - L'événement contenant les détails de la sélection, notamment la clé du layer.
     */
    initSelect($event) {
      const key = $event.detail.key;
      this.configSelects[key] = this.mapService.configSelect(key);
      this.configSelects = { ...this.configSelects };
    },
  },
  computed: {
    /**
     * Configure le formulaire d'exportation de la carte.
     *
     * Cette méthode retourne un objet de configuration pour le formulaire d'export de la carte.
     * - Elle fusionne la configuration existante `configFormExportMap` avec des propriétés spécifiques à l'export.
     * - La propriété `action.process` définit la logique d'exportation :
     *    - Récupère les données du formulaire (`postData`) pour le nom de fichier, la hauteur et la largeur.
     *    - Détermine le format d'image à exporter (jpg ou png) selon l'extension du nom de fichier.
     *    - Utilise le service `mapService.toImgFile` pour générer le fichier image de la carte.
     *    - Ferme le dialogue d'exportation (`bExportMap = false`) une fois l'export terminé.
     * - La propriété `value` initialise les valeurs du formulaire :
     *    - `filename` : nom de fichier par défaut pour l'export.
     *    - `width` et `height` : dimensions de la carte récupérées dynamiquement via les références du composant.
     *
     * @returns {Object} Objet de configuration du formulaire d'exportation de la carte.
     */
    configFormExportMap() {
      const out = {
        ...configFormExportMap,
        action: {
          process: ({ postData }) => {
            return new Promise((resolve) => {
              const options = {
                filename: postData.filename,
                height: postData.height,
                width: postData.width,
                format: postData.filename.endsWith('.jpg') ? 'jpg' : 'png',
              };

              this.mapService.toImgFile(options).then(() => {
                this.bExportMap = false; // ferme le dialogue
                resolve();
              });
            });
          },
        },
        value: {
          filename: 'export_carte_oeasc.png',
          // width: 1000,
          width: this.$refs[this.mapId].clientWidth,
          height: this.$refs[this.mapId].clientHeight,
        },
      };
      return out;
    },

    /**
     * Calcule dynamiquement la hauteur du composant de la carte.
     * - Si la propriété 'bInit' est fausse, retourne "0px" (la carte n'est pas initialisée).
     * - Si la propriété 'height' est définie, retourne cette valeur (hauteur personnalisée).
     * - Si la propriété 'fillHeight' existe dans les props et que l'élément est monté,
     *   calcule la hauteur disponible dans la fenêtre en soustrayant la position verticale
     *   du composant et une marge de 40px à la hauteur totale du document.
     * - Sinon, retourne une hauteur par défaut de "600px".
     */
    computedHeight() {
      const computedHeight = !this.bInit
        ? '0px'
        : this.height
          ? this.height
          : 'fillHeight' in this.$props && this.$el
            ? `${document.documentElement.clientHeight - this.$el.offsetTop - 40}px`
            : '600px';
      return computedHeight;
    },
  },

  mounted: function () {
    // Vérifie si la configuration de la carte est définie.
    // Si elle ne l'est pas, récupère la configuration prédéfinie via le nom passé en prop.
    if (!this.config) {
      this.config = MapService.getPreConfigMap(this.preConfigName);
    }

    // Indique que l'initialisation du composant est terminée.
    this.bInit = true;

    // Instancie le service de gestion de la carte avec l'identifiant et la configuration.
    this.mapService = new MapService(this.mapId, this.config);

    // Enregistre ce service de carte dans le store Vuex pour qu'il soit accessible globalement.
    // Le service sera stocké dans state._mapServices.
    this.$store.commit('setMapService', this.mapService);

    // Initialise les couches, tuiles et marqueurs de la carte, une fois que Vue a appliqué au DOM
    // la vraie hauteur du conteneur (computedHeight passe de "0px" à sa valeur réelle avec bInit).
    // Sans ce $nextTick, L.map() est créée sur un conteneur de hauteur 0 : le fond de carte ne
    // couvre pas toute la zone visible (grisé en bas) et l'ajout des marqueurs plante (le rendu SVG
    // de Leaflet n'a pas encore de bounds valides), ce qui empêche aussi les marqueurs suivants de
    // s'afficher.
    this.$nextTick(() => {
      this.mapService.init();
    });

    // Ajoute un écouteur d'événement sur l'élément DOM de la carte.
    // Cet événement "layer-data" permet de gérer la sélection dynamique des couches.
    document.getElementById(this.mapId).addEventListener('layer-data', this.initSelect);
  },

  // Détruit la carte Leaflet et retire l'instance du store quand le composant est démonté
  // (changement de page). Sans ça, Leaflet garde des références vivantes (tuiles, couches,
  // listeners window/document) qui s'accumulent au fil des navigations et finissent par
  // faire ramer puis planter le navigateur.
  unmounted: function () {
    const elem = document.getElementById(this.mapId);
    if (elem) {
      elem.removeEventListener('layer-data', this.initSelect);
    }
    if (this.mapService) {
      this.mapService.destroy();
    }
    this.$store.commit('removeMapService', this.mapId);
  },
};
</script>
