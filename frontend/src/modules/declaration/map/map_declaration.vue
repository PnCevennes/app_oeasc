<!-- carte servant à la creation d'une déclaration de degat.
affiche des layer en fonction de si la foret est public ou privé et si elle a un document de gestions
permet de zoomer dans les zones sélectionnées -->

<!--
  Ce composant Vue représente une interface de sélection sur une carte interactive,
  permettant à l'utilisateur de choisir une parcelle ou une forêt selon le contexte.

  Structure principale :
  - La vue est divisée en deux parties principales :
    1. La carte (70% de la largeur) avec un bouton de retour et une superposition de chargement.
    2. Un panneau latéral (30% de la largeur) pour la sélection et l'affichage des parcelles/forêts.

  Carte :
  - Un bouton "Retour" permet de revenir au type de carte précédent, affichant dynamiquement le nom du type.
  - La carte est affichée dans un div avec l'id "map".
  - Lorsque la carte est en cours de chargement (freeze_map), une superposition semi-transparente apparaît avec un indicateur de progression circulaire et le texte "chargement".

  Panneau latéral :
  - Affiche des instructions contextuelles selon l'état des variables `b_document` et `b_statut_public` :
    - Sélection d'une parcelle cadastrale.
    - Sélection d'une forêt DGD, avec aide si la forêt n'est pas visible.
    - Sélection d'une forêt ONF.
  - Un champ de recherche (v-autocomplete) permet de rechercher une parcelle parmi les couches visibles de la carte.
  - Un groupe de pastilles (v-chip-group) affiche les parcelles sélectionnées, chacune pouvant être retirée individuellement.

  Points techniques :
  - Utilisation de Vuetify pour les composants d'interface (boutons, icônes, autocomplete, chips, progress).
  - Les aides contextuelles sont intégrées via des composants <help> et <helpContent>.
  - Les interactions utilisateur sont gérées par des méthodes (ex: action_button_retour_arriere, action_select_in_liste, action_close_pastille).

  Ce composant est conçu pour guider l'utilisateur dans la sélection géographique, tout en offrant des aides et une expérience fluide lors du chargement des données cartographiques.
-->
<template v-if="initialized">
  <div style="width: 100%; display: flex; flex-direction: row">
    <div style="position: relative; width: 70%">
      <v-btn
        class="v-btn v-btn--elevated v-theme--light"
        style="position: absolute; top: 16px; right: 16px; z-index: 1; border: 1px solid #ccc"
        @click="action_button_retour_arriere"
      >
        <v-icon left>mdi-regular mdi-reply</v-icon>
        {{ typesCarteNames[last_typeCarte] || 'Retour' }}
      </v-btn>
      <div
        id="map"
        style="height: 600px; min-width: 500px; z-index: 0"
      ></div>
      <div
        v-if="freeze_map"
        style="
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          z-index: 10;
          background: rgba(255, 255, 255, 0.3);
          cursor: progress;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        "
      >
        <v-progress-circular
          indeterminate
          color="primary"
          size="150"
          width="10"
        ></v-progress-circular>
        <div style="margin-top: 12px; font-size: 25px; font-weight: bold">chargement</div>
      </div>
    </div>

    <div style="width: 30%; flex-direction: column; padding-left: 20px">
      <div
        style="
          margin: 10px auto 20px auto;
          width: 100%;
          display: flex;
          justify-content: center;
          align-items: center;
        "
      ></div>
      <div v-if="!b_document">
        <h4>
          Selectionner une parcelle
          <help style="margin-left: 2em">
            <helpContent helpID="parcelle_cadastrale"></helpContent>
          </help>
        </h4>
      </div>
      <div v-if="b_document && !b_statut_public">
        <h4>
          Selectionner une forêt DGD
          <help style="margin-left: 2em">
            <helpContent helpID="form_dgestion_durable"></helpContent>
          </help>
        </h4>
        <h6 style="font-weight: normal; font-style: italic; font-size: 0.9em">
          Je ne retrouve pas ma Forêt
          <help style="margin-left: 2em">
            <helpContent helpID="foret_non_visible"></helpContent>
          </help>
        </h6>
      </div>
      <div v-if="b_document && b_statut_public">
        <h4>Selectionner une forêt ONF</h4>
      </div>

      <div style="margin-bottom: 16px">
        <v-autocomplete
          id="liste_select_areas"
          ref="liste_select_areas"
          :items="geojsonVisibleLayers.features"
          item-text="properties.label"
          item-value="properties.id_area"
          label="Rechercher une parcelle"
          clearable
          @change="action_select_in_liste($event)"
        ></v-autocomplete>
      </div>

      <div>
        <v-chip-group
          v-if="areasLocalisationOfThisMap.length"
          column
        >
          <v-chip
            v-for="area in areasLocalisationOfThisMap"
            :key="area.id_area"
            close
            @click:close="action_close_pastille(area)"
            class="ma-1"
          >
            {{ area.area_name }}
          </v-chip>
        </v-chip-group>
      </div>
    </div>
  </div>
</template>

<script>
import { configMap } from '@/config/config-map.js'; // Importez la configuration de la carte
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { styles } from '@/config/config-style.js'; // les styles des couches de la carte
import help from '@/components/form/help_static.vue';
import helpContent from '@/modules/declaration/help-content.vue';
import {
  // certaines api request sont superflues. Il faudra les améliorer.
  fetch_oeasc_perimetre,
  fetch_areas_child_of,
  fetch_areas_group_from_id_type,
  fetch_hierarchy_areas,
  fetch_hierarchy_from_intersect,
} from '@/modules/declaration/utils/api_request.js'; // Importez les fonctions nécessaires si elles existent

const DEFAUT = 0; // uniquement le perimetre oeasc
const COMMUNES = 327; // Type area des communes dans la base de données
const FORETS_ONF = 328; // Type area des forêts ONF dans la bdd
const PARCELLES_ONF = 329; // Type area des parcelles dans la bdd
const UG_ONF = 330; // Type area des unités de gestion ONF dans la bdd
const FORETS_DGD = 331; // Type area des forêts DGD dans la bdd
const CADASTRES = 332; // Type area des parcelles cadastrales dans la bdd
const SECTIONS = 333; // Type area des sections cadastrales dans la bdd

// Noms à afficher sur le bouton de retour en arrière
const NOM_TYPECARTE = {
  [DEFAUT]: 'Retour',
  [COMMUNES]: 'Communes',
  [SECTIONS]: 'Sections',
  [FORETS_DGD]: 'Forêts DGD',
  [FORETS_ONF]: 'Forêts ONF',
  [CADASTRES]: 'Cadastres',
  [PARCELLES_ONF]: 'Parcelles ONF',
  [UG_ONF]: 'Unités de gestion ONF',
};

export default {
  name: 'MapDeclaration',
  props: {
    b_statut_public: {
      type: Boolean,
    },
    b_document: {
      type: Boolean,
    },

    declaration_data: {
      // toutes les données de déclaration récupérées depuis la bdd
      type: Object,
      required: true,
    },
  },

  components: {
    help,
    helpContent,
  },

  data() {
    return {
      map: null, // Instance de la carte Leaflet. Sera activé dans monted() avec initMap()
      typeCarte: this.defineTypeCarte(), // Type de carte par défaut affiche uniquement les perimetres selectionnés
      id_area_visible: null, // Id de la zone visible sur la carte. Sert à savoir si on affiche les sections ou les cadastres
      last_typeCarte: this.typeCarte, // Dernier type de carte affiché pour le retour en arriere
      last_id_section_visible: null, // dernier id de la section visité( la section cadastrale ou la forêt DGD)
      geojsonVisibleLayers: {}, // données GeoJSON à afficher sur la carte
      layerIndex: {}, // index id_area → layer Leaflet pour éviter les scans eachLayer
      layers_groupe_cache: {}, // contient les geojson des couches déja chargées de communes, section, forêts DGD et ONF.
      // Pour eviter de relancer une requête dans le retour en arrière

      actual_foret_onf: null, // Forêt ONF sélectionnée pour les forêts ONF
      actual_foret_onf_parcelle: null, // Forêt ONF PRF sélectionnée pour les forêts ONF
      actual_foret_dgd: null, // Forêt DGD sélectionnée pour les forêts DGD
      actual_commune: null, // Commune sélectionnée pour les sections cadastrales
      actual_section: null, // Section cadastrale sélectionnée pour les parcelles cadastrales

      list_selected_areas: [], // id des layers sélectionnés (Set pour éviter les doublons)

      liste_areas_selected: {}, // Liste des zones sélectionnées pour la déclaration

      geom_perimetre_oeasc: null, // geojson du périmètre oeasc, affiché en noir et non selectionnable. Affiché en permanence.
      configMap: configMap, // Configuration de la carte importée depuis config-map.js
      typesCarteNames: NOM_TYPECARTE, // Noms des types de carte pour l'affichage

      freeze_map: false, // Permet de geler la carte pour éviter les interactions pendant le chargement des données
      // information_foret: null, // Forêt sélectionnée pour les forêts DGD et ONF
      initialized: false, // Indique si le composant est initialisé et prêt à être affiché
    };
  },

  computed: {
    areasLocalisationOfThisMap() {
      const leafIds = new Set([
        ...(this.declaration_data.areas_localisation_cadastre || []),
        ...(this.declaration_data.areas_localisation_onf_ug || []),
      ]);
      return (this.declaration_data.areas_localisation || []).filter(
        (area) => area && leafIds.has(area.id_area)
      );
    },
  },
  watch: {
    // Lorsque les layers à afficher changent, on met à jour la carte
    geojsonVisibleLayers(newVal) {
      // Lorsque les données GeoJSON changent, on met à jour les couches de la carte
      this.add_layers_on_map();
    },

    // Lorsque les zones sélectionnées changent, on re-rend la carte pour mettre à jour les couleurs
    'declaration_data.areas_localisation'() {
      if (this.map && this.geojsonVisibleLayers?.features?.length) {
        this.add_layers_on_map();
      }
    },

    // Lorsque le statut du document change dans le formulaire principal, on met à jour le type de carte
    b_document(newVal, oldVal) {
      if (oldVal === undefined) return;
      this.typeCarte = this.defineTypeCarte();
      this.fetch_new_geojson_data(this.typeCarte);
      if (newVal == false) {
        this.declaration_data.label_foret = ''; // Réinitialise le label de la forêt si le document n'est pas requis
        this.declaration_data.surface_renseignee = null; // Réinitialise la surface renseignée si le document n'est pas requis
        this.declaration_data.code_foret = null; // Réinitialise le code de la forêt si le document n'est pas requis
        this.reset_areas(); // Réinitialise les zones sélectionnées
      }
    },

    // Lorsque le statut public change dans le formulaire principal, on met à jour le type de carte
    b_statut_public(newVal, oldVal) {
      // Ne fait rien au démarrage (oldVal === undefined)
      if (oldVal === undefined) return;
      this.typeCarte = this.defineTypeCarte();
      this.reset_areas(); // Réinitialise les zones sélectionnées
      this.fetch_new_geojson_data(this.typeCarte);
    },
  },

  async created() {},

  async mounted() {
    this.geom_perimetre_oeasc = await fetch_oeasc_perimetre();
    this.typeCarte = this.defineTypeCarte();
    this.initMap();
    this.add_layer_perimetre_oeasc();
    await this.initialise_areas(); // Initialise les zones avant le rendu de la carte
    this.fetch_new_geojson_data(this.typeCarte); // recupère les contours des layers à afficher
    this.initialized = true; // Indique que le composant est prêt à être affiché
  },

  methods: {
    /**
     * vide toutes les zones sélectionnées dans la déclaration. Sert à réinitialiser la carte lorsque l'on change de type de carte.
     *
     */
    reset_areas() {
      this.declaration_data.areas_localisation = []; // Réinitialise la liste des zones sélectionnées
      this.declaration_data.areas_localisation_onf_prf = []; // Réinitialise la liste des zones ONF PRF sélectionnées
      this.declaration_data.areas_localisation_onf_ug = []; // Réinitialise la liste des zones ONF UG sélectionnées
      this.declaration_data.areas_foret = []; // Réinitialise la liste des forêts sélectionnées
      this.declaration_data.areas_foret_communes = [];
      this.declaration_data.areas_foret_sections = []; // Réinitialise la liste des sections sélectionnées
      this.declaration_data.areas_localisation_cadastre = [];
      this.declaration_data.areas_foret_onf = null; // Réinitialise la liste des zones ONF PRF sélectionnées
      this.declaration_data.areas_foret_dgd = null;
    },

    /**
     * Définit le type de carte à afficher apres que l'utilisateur ait cliqué sur un layer.
     * par exemple si il click sur une commune, on affiche les sections de cette commune.
     * @returns {number} Le type de carte à afficher.
     */
    change_type_carte_after_click() {
      // Change le type de carte à afficher apres un clic sur une couche
      if (this.typeCarte === COMMUNES) {
        // on était sur les communes, on a donc cliqué sur une section
        this.last_typeCarte = COMMUNES;
        this.typeCarte = SECTIONS;
      } else if (this.typeCarte === SECTIONS) {
        this.last_typeCarte = SECTIONS;
        this.typeCarte = CADASTRES;
      } else if (this.typeCarte === FORETS_DGD) {
        this.last_typeCarte = FORETS_DGD;
        this.typeCarte = CADASTRES;
      } else if (this.typeCarte === FORETS_ONF) {
        this.last_typeCarte = FORETS_ONF;
        this.typeCarte = PARCELLES_ONF;
      } else if (this.typeCarte === PARCELLES_ONF) {
        this.last_typeCarte = PARCELLES_ONF;
        this.typeCarte = UG_ONF;
      } else if (this.typeCarte === UG_ONF) {
        this.last_typeCarte = UG_ONF;
        this.typeCarte = FORETS_ONF;
      } else if (this.typeCarte === CADASTRES) {
        this.last_typeCarte = CADASTRES;
        this.typeCarte = FORETS_DGD; // on revient aux forêts DGD
      }
    },

    /**
     * Réinitialise les layers de la carte et ajoute les nouveaux layen du nouveau type de carte.
     */
    async add_layers_on_map() {
      if (!this.map) return;

      this.layerIndex = {}; // reset de l'index à chaque rechargement
      this.map.eachLayer((layer) => {
        if (layer instanceof L.GeoJSON) {
          this.map.removeLayer(layer);
        }
      });
      this.add_layer_perimetre_oeasc();

      // Canvas renderer : toutes les features partagent un seul <canvas> au lieu d'un SVG par feature
      const renderer = L.canvas({ padding: 0.5 });

      if (this.typeCarte === CADASTRES || this.typeCarte === UG_ONF || this.typeCarte == DEFAUT) {
        this.render_selectable_layers(renderer);
      } else {
        this.render_clickable_layers(renderer);
      }
    },

    /**
     * Affiche les layers de regroupement (communes, sections, forêts DGD et ONF) sur la carte.
     * ceux qui amènent à des sous sections lorsqu'on clique dessus. (donc tous saufs les cadastres)
     * le geojson affiché sera celui contenu dans this.geojsonVisibleLayers
     */
    render_clickable_layers(renderer) {
      const vm = this;
      const map_layers = L.geoJSON(this.geojsonVisibleLayers, {
        renderer,
        style: styles.normal,
        onEachFeature: (feature, layer) => {
          vm.layerIndex[feature.properties.id_area] = layer;
          layer.bindTooltip(feature.properties.area_name || '', {
            direction: 'top',
            offset: [0, -20],
            className: 'anim-tooltip',
          });
          const isSelected = () =>
            vm.declaration_data.areas_localisation.some(
              (area) => area.id_area === feature.properties.id_area
            );
          layer.on('mouseover', function () {
            layer.setStyle(styles.hover);
          });
          layer.on('mouseout', function () {
            layer.setStyle(isSelected() ? styles.select : styles.normal);
          });
          layer.on('click', () => {
            vm.action_click_on_layer(feature, layer);
          });
          layer.setStyle(isSelected() ? styles.select : styles.normal);
        },
      }).addTo(this.map);

      // Zoom sur l'ensemble des communes affichées
      if (map_layers.getLayers().length > 0) {
        this.map.fitBounds(map_layers.getBounds(), { maxZoom: 30 });
      }
    },

    /**
     * Toutes les actions à effectuer lorsqu'on clique sur un layer de la carte.
     * Un layer cliquable est non un layer selectionnable. C'est à dire les COMMUNES, SECTIONS, FORETS_DGD, FORETS_ONF.PARCELLES_ONF
     * @param {Object} feature - Les feature geojson du layer cliqué sur la carte.
     * @param {Object} layer - Le layer leaflet cliqué. Pas utilisé mais pourrait l'être pour de améliorations futures.
     */
    action_click_on_layer(feature, layer) {
      // sauvegarde des infos concernant la zone cliquée pour l'ajouter plus tard
      this.liste_areas_selected[feature.properties.id_area] = feature.properties;

      if (this.typeCarte == COMMUNES) {
        // Pour sauvegarder l'id de la commune visible avant de changer de type de carte.
        this.actual_commune = feature.properties.id_area; // Met à jour l'id de la commune
      } else if (this.typeCarte == SECTIONS) {
        // Pour sauvegarder l'id de la section visible avant de changer de type de carte.
        this.actual_section = feature.properties.id_area; // Met à jour l'id de la section
        this.last_id_section_visible = this.id_area_visible;
      } else if (this.typeCarte == FORETS_ONF) {
        // Pour sauvegarder l'id de la forêt ONF visible avant de changer de type de carte.
        this.actual_foret_onf = feature.properties.id_area; // Met à jour l'id de la forêt ONF
      } else if (this.typeCarte == PARCELLES_ONF) {
        // Pour sauvegarder l'id de la forêt ONF PRF visible avant de changer de type de carte.
        this.actual_foret_onf_parcelle = feature.properties.id_area; // Met à jour l'id de la forêt ONF PRF
        this.last_id_section_visible = this.id_area_visible;
      } else if (this.typeCarte == FORETS_DGD) {
        // Pour sauvegarder l'id de la forêt DGD visible avant de changer de type de carte.
        this.actual_foret_dgd = feature.properties.id_area; // Met à jour l'id de la forêt DGD
      }

      this.id_area_visible = feature.properties.id_area;
      this.fetch_new_geojson_data(this.typeCarte, this.id_area_visible);
      // passe le type de carte à un niveau en dessous et enregistre ce type de carte dans last_id_type
      this.change_type_carte_after_click();
    },

    /**
     * Pour les pages CADASTRES, UG_ONF et DEFAUT, affiche les layers que l'on peut sélectionner. et qui modifie la liste des périmètres sélectionnés.
     * affichera les donnée dans this.geojsonVisibleLayers.
     */
    render_selectable_layers(renderer) {
      const vm = this;
      const map_layers = L.geoJSON(this.geojsonVisibleLayers, {
        renderer,
        style: styles.normal,
        onEachFeature: (feature, layer) => {
          vm.layerIndex[feature.properties.id_area] = layer;
          layer.bindTooltip(feature.properties.area_name || '', {
            direction: 'top',
            offset: [0, -20],
            className: 'anim-tooltip',
          });
          const isSelected = () =>
            vm.declaration_data.areas_localisation.some(
              (area) => area.id_area === feature.properties.id_area
            );
          layer.on('mouseover', function () {
            layer.setStyle(styles.hover);
          });
          layer.on('mouseout', function () {
            layer.setStyle(isSelected() ? styles.select : styles.normal);
          });
          layer.on('click', () => {
            vm.action_selection_area(feature);
          });
          // Le style par défaut est déjà styles.normal (option L.geoJSON), on ne surcharge que si sélectionné
          if (isSelected()) layer.setStyle(styles.select);
        },
      }).addTo(this.map);

      if (map_layers.getLayers().length > 0) {
        this.map.fitBounds(map_layers.getBounds(), { maxZoom: 30 });
      }
    },

    /**
     * actions effectuées lorsque l'utilisateur sélectionne une zone sur la carte. Gère l'enregistrement des areas en fonction des cas
     * particuliers (forêts ONF, foret DGD ou communes).
     * declaration_data.areas_localisation contient toutes les zones (parents et enfants) et sert à l'affichage des zones sélectionnées en orange sur la carte.
     * area_localisation peut contenir plusieus fois le meme element pour garder une zone parent en orange si une zone enfant est deselectionnée mais elle en contient d'autres.
     * les autres enregistrement d'areas_localisation_(onf_ug, onf_prf, cadastre, section) sont utilisés pour l'enregistrement en base de données.
     * @param feature les informations sur la zone sélectionnée issues du geojson.
     */
    action_selection_area(feature) {
      // Gère la sélection d'une zone sur la carte
      if (feature) {
        const index = this.declaration_data.areas_localisation.findIndex(
          (area) => area.id_area === feature.properties.id_area
        );
        // ########## Cette area est déja selectionnée, on cherche donc à la retirer #################
        if (index > -1) {
          // On utilise l'entrée déjà enregistrée dans areas_localisation (qui contient id_parent)
          // plutôt que feature.properties (issu du geojson brut, sans id_parent) pour que la
          // cascade de nettoyage des parents (commune, section, forêt) fonctionne correctement.
          this.unselect_area(this.declaration_data.areas_localisation[index]); // Retire la zone de la déclaration
        } else {
          // ######### Cette area n'est pas déja selectionnée, on cherche donc à l'ajouter #############
          this.select_area(feature.properties);
          // on change le style du layer pour le mettre en orange
          // Find the layer by id_area from all layers on the map
          this.change_style_layer(feature.properties, styles.select);
        }
      }
    },

    /**
     * Change le style du layer selectionné. Utilisé lors de la selection dans menu déroulant ou lorsque
     * l'on deselectionne une zone en cliquant sur la pastille
     * @returns {number} Le type de carte à afficher.
     * @param {Object} properties_layer - Les propriétés de la zone à mettre à jour issue du geojson
     * @param {Object} style - Le style à appliquer au layer
     */
    change_style_layer(properties_layer, style) {
      const layer = this.layerIndex[properties_layer.id_area];
      if (layer) {
        layer.setStyle(style);
      }
    },

    /**
     * Gère la sélection d'une zone dans la liste déroulante
     * @param id_area l'id de la zone sélectionnée dans la liste déroulante
     */
    action_select_in_liste(id_area) {
      // Gère la sélection d'une zone dans la liste déroulante
      const properties_area = this.geojsonVisibleLayers.features.find(
        (f) => f.properties.id_area === id_area
      );
      this.$refs.liste_select_areas.blur(); // Retire le focus de la liste déroulante
      if (this.typeCarte == UG_ONF || this.typeCarte == CADASTRES) {
        this.action_selection_area(properties_area); // Appelle la fonction de sélection de zone
      } else {
        this.action_click_on_layer(properties_area, null); // Appelle la fonction de clic sur la couche
      }
    },

    /**
     * Cloture d'une pastille à droite de la carte.
     * @param area l'area à retirer de la déclaration. C'est à dire l'area sélectionnée dans la liste déroulante ou sur la carte.
     */
    action_close_pastille(area) {
      this.unselect_area(area); // Retire la zone de la déclaration
      this.change_style_layer(area, styles.normal);
    },

    /**
     * Remplit les liste areas_localisation, areas_localisation_onf_ug, areas_localisation_onf_prf, areas_foret_communes, areas_foret_sections et areas_foret_dgd
     * lorsque une zone est selectionnée sur la carte ou dans le menu
     * area_localisation sert uniquement à afficher les zones sélectionnées en orange sur la carte.
     * @param feature les information sur une area issue du geojson.feature ou de list_selected_areas[id_area]
     */
    select_area(feature) {
      if (this.declaration_data.b_document == false) {
        // ################## CAS DES SECTIONS ET COMMUNES ##################

        console.log(
          'areas_foret_communes avant ajout : ',
          this.declaration_data.areas_foret_communes
        );
        console.log('actual_commune : ', this.actual_commune);
        if (this.declaration_data.areas_foret_communes.includes(this.actual_commune) == false) {
          this.declaration_data.areas_foret_communes.push(this.actual_commune); // Ajoute la commune à la liste des zones sélectionnées
        }

        if (this.declaration_data.areas_foret_sections.includes(this.actual_section) == false) {
          this.declaration_data.areas_foret_sections.push(this.actual_section); // Ajoute la section à la liste des zones sélectionnées
        }
        this.declaration_data.areas_localisation_cadastre.push(feature.id_area); //

        let area_commune = this.liste_areas_selected[this.actual_commune];
        area_commune['id_parent'] = null;
        let area_section = this.liste_areas_selected[this.actual_section];
        area_section['id_parent'] = this.actual_commune; // Ajoute l'id de la commune à la section
        if (
          !this.declaration_data.areas_localisation.some(
            (area) => area.id_area === area_commune.id_area
          )
        ) {
          this.declaration_data.areas_localisation.push(area_commune);
        }
        if (
          !this.declaration_data.areas_localisation.some(
            (area) => area.id_area === area_section.id_area
          )
        ) {
          this.declaration_data.areas_localisation.push(area_section);
        }

        // On ajoute la zone cadastrale à la déclaration
        this.declaration_data.areas_localisation.push({
          ...feature,
          id_parent: this.actual_section,
        });
      } else if (this.declaration_data.b_document == true) {
        // ################## CAS DES FORET DGD ##############################
        if (this.declaration_data.b_statut_public == false) {
          if (this.declaration_data.areas_foret_dgd !== this.actual_foret_dgd) {
            // Si la forêt DGD sélectionnée est différente de celle déjà sélectionnée, on efface tout car il ne peut y avoir qu'une foret selectionné
            this.reset_areas(); // Réinitialise les zones sélectionnées
            this.declaration_data.areas_foret_dgd = this.actual_foret_dgd; // Réinitialise la forêt DGD sélectionnée
            this.declaration_data.nom_foret =
              this.liste_areas_selected[this.actual_foret_dgd].area_name; // Met à jour le label de la forêt DGD
            this.declaration_data.label_foret =
              this.liste_areas_selected[this.actual_foret_dgd].label; // Met à jour le label de la forêt DGD
            this.declaration_data.code_foret =
              this.liste_areas_selected[this.actual_foret_dgd].area_code;
            this.declaration_data.surface_renseignee =
              this.liste_areas_selected[this.actual_foret_dgd].surface_renseignee;
            this.declaration_data.surface_calculee =
              this.liste_areas_selected[this.actual_foret_dgd].surface_calculee;
          }
          this.declaration_data.areas_localisation_cadastre.push(feature.id_area);
          let area_dgd = this.liste_areas_selected[this.actual_foret_dgd];
          area_dgd['id_parent'] = null;
          if (
            !this.declaration_data.areas_localisation.some(
              (area) => area.id_area === area_dgd.id_area
            )
          ) {
            this.declaration_data.areas_localisation.push(area_dgd);
          }
          this.declaration_data.areas_localisation.push({
            ...feature,
            id_parent: this.actual_foret_dgd,
          });
        } else {
          // ################### CAS DES FORETS ONF ##############################
          // Si la forêt ONF sélectionnée est différente de celle déjà sélectionnée, on efface tout car il ne peut y avoir qu'une foret selectionné
          if (this.declaration_data.areas_foret_onf !== this.actual_foret_onf) {
            this.reset_areas();
            this.declaration_data.areas_foret_onf = this.actual_foret_onf; // Réinitialise la forêt ONF sélectionnée
            this.declaration_data.nom_foret =
              this.liste_areas_selected[this.actual_foret_onf].area_name; // Met à jour le label de la forêt ONF
            this.declaration_data.label_foret =
              this.liste_areas_selected[this.actual_foret_onf].label; // Met à jour le label de la forêt ONF
            this.declaration_data.code_foret =
              this.liste_areas_selected[this.actual_foret_onf].area_code;
            this.declaration_data.surface_renseignee =
              this.liste_areas_selected[this.actual_foret_onf].surface_renseignee;
            this.declaration_data.surface_calculee =
              this.liste_areas_selected[this.actual_foret_onf].surface_calculee;
          }

          // On remplit les aire de la parcelle et de l'ug pour l'enregistrement en bdd
          this.declaration_data.areas_localisation_onf_ug.push(feature.id_area);
          this.declaration_data.areas_localisation_onf_prf.push(this.actual_foret_onf_parcelle);

          let area_onf = this.liste_areas_selected[this.actual_foret_onf];
          area_onf['id_parent'] = null;
          let area_onf_parcelle = this.liste_areas_selected[this.actual_foret_onf_parcelle];
          area_onf_parcelle['id_parent'] = this.actual_foret_onf;
          let area_onf_ug = { ...feature, id_parent: this.actual_foret_onf_parcelle }; // Ajoute l'id de la parcelle ONF à la déclaration
          if (
            !this.declaration_data.areas_localisation.some(
              (area) => area.id_area === area_onf.id_area
            )
          ) {
            this.declaration_data.areas_localisation.push(area_onf);
          }
          if (
            !this.declaration_data.areas_localisation.some(
              (area) => area.id_area === area_onf_parcelle.id_area
            )
          ) {
            this.declaration_data.areas_localisation.push(area_onf_parcelle);
          }
          if (
            !this.declaration_data.areas_localisation.some(
              (area) => area.id_area === area_onf_ug.id_area
            )
          ) {
            this.declaration_data.areas_localisation.push(area_onf_ug);
          }
        }
      }
    },

    /**
     * retire la zone selectionnée des areas_localisation, areas_localisation_onf_ug, areas_localisation_onf_prf, areas_foret_communes, areas_foret_sections et areas_foret_dgd
     * lorsque une zone est deselectionnée sur la carte ou dans le menu
     * area_localisation sert uniquement à afficher les zones sélectionnées en orange sur la carte.
     * @param feature les information sur une area issue du geojson.feature ou de list_selected_areas[id_area]
     */
    unselect_area(feature) {
      let this_parent = feature.id_parent || null; // Récupère l'id du parent de la zone sélectionnée
      this.declaration_data.areas_localisation = this.declaration_data.areas_localisation.filter(
        (area) => area.id_area !== feature.id_area
      );

      if (this.declaration_data.b_document == false) {
        // Si le statut public est faux, on est en mode DGD ou sections
        // ################## CAS DES SECTIONS ET COMMUNES ##################
        this.declaration_data.areas_localisation_cadastre =
          this.declaration_data.areas_localisation_cadastre.filter((id) => id !== feature.id_area);

        // si l'actual_section n'est dans aucun id_parent des elements de areas_localisation, on le retire
        if (
          !this.declaration_data.areas_localisation.some((area) => area.id_parent === this_parent)
        ) {
          // Récupère l'id de la commune parente de la section avant de retirer la section
          const section_entry = this.declaration_data.areas_localisation.find(
            (area) => area.id_area === this_parent
          );
          const id_commune_parente = section_entry ? section_entry.id_parent : null;

          this.declaration_data.areas_foret_sections =
            this.declaration_data.areas_foret_sections.filter((id) => id !== this_parent);

          this.declaration_data.areas_localisation =
            this.declaration_data.areas_localisation.filter((area) => area.id_area !== this_parent);

          // si la commune n'est dans aucun id_parent des elements restants de areas_localisation, on la retire
          if (
            id_commune_parente !== null &&
            !this.declaration_data.areas_localisation.some(
              (area) => area.id_parent === id_commune_parente
            )
          ) {
            this.declaration_data.areas_localisation =
              this.declaration_data.areas_localisation.filter(
                (area) => area.id_area !== id_commune_parente
              );
            this.declaration_data.areas_foret_communes =
              this.declaration_data.areas_foret_communes.filter((id) => id !== id_commune_parente);
          }
        }
      } else if (this.declaration_data.b_document == true) {
        // ################## CAS DES FORET DGD ##############################
        if (this.declaration_data.b_statut_public == false) {
          this.declaration_data.areas_localisation_cadastre =
            this.declaration_data.areas_localisation_cadastre.filter(
              (id) => id !== feature.id_area
            );
          // si l'actual_foret_dgd n'est pas dans aucun id_parent des elements de areas_localisation, on le retire
          if (
            !this.declaration_data.areas_localisation.some((area) => area.id_parent === this_parent)
          ) {
            this.declaration_data.areas_localisation =
              this.declaration_data.areas_localisation.filter(
                (area) => area.id_area !== this_parent
              );
            this.declaration_data.areas_foret_dgd = null; // Réinitialise la forêt DGD sélectionnée
          }
        } else {
          // ################## CAS DES FORET ONF ##################
          this.declaration_data.areas_localisation_onf_ug =
            this.declaration_data.areas_localisation_onf_ug.filter((id) => id !== feature.id_area);
          if (
            !this.declaration_data.areas_localisation.some((area) => area.id_parent === this_parent)
          ) {
            this.declaration_data.areas_localisation_onf_prf =
              this.declaration_data.areas_localisation_onf_prf.filter((id) => id !== this_parent);
            this.declaration_data.areas_localisation =
              this.declaration_data.areas_localisation.filter(
                (area) => area.id_area !== this_parent
              );
            if (
              !this.declaration_data.areas_localisation.some(
                (area) => area.id_parent === this.declaration_data.areas_foret_onf
              )
            ) {
              this.declaration_data.areas_localisation =
                this.declaration_data.areas_localisation.filter(
                  (area) => area.id_area !== this.declaration_data.areas_foret_onf
                );
              this.declaration_data.areas_foret_onf = null; // Réinitialise la forêt ONF sélectionnée
            }
          }
        }
      }
    },

    /**
     * Gère quelle page doit être affichée lorsque l'utilisateur clique sur le bouton de retour en arrière.
     */
    action_button_retour_arriere() {
      // Retourne en arrière dans le type de carte

      if (this.typeCarte == CADASTRES) {
        if (this.last_typeCarte == SECTIONS) {
          this.last_typeCarte = COMMUNES;
          this.typeCarte = SECTIONS;
          this.id_area_visible = this.last_id_section_visible;
          this.fetch_new_geojson_data(COMMUNES, this.id_area_visible);
        } else if (this.last_typeCarte == FORETS_DGD) {
          // on était des cadastres de forêts DGD on retourne vers la foret
          this.typeCarte = FORETS_DGD; // On revient au mode forêts DGD
          this.last_typeCarte = DEFAUT; // On revient au mode par défaut
          this.fetch_new_geojson_data(FORETS_DGD);
        }
      } else if (this.typeCarte == SECTIONS) {
        this.typeCarte = COMMUNES;
        this.last_typeCarte = DEFAUT; // On revient au mode communes
        this.fetch_new_geojson_data(COMMUNES); // Recharge les données GeoJSON pour le type de carte communes
      } else if (this.typeCarte == PARCELLES_ONF) {
        // Si on est en mode parcelles ONF ou unités de gestion ONF, on revient au mode forêts ONF
        this.typeCarte = FORETS_ONF;
        this.last_typeCarte = DEFAUT; // On revient au mode forêts ONF
        this.fetch_new_geojson_data(FORETS_ONF); // Recharge les données GeoJSON pour le type de carte forêts ONF
      } else if (this.typeCarte == UG_ONF) {
        // Si on est en mode unités de gestion ONF, on revient au mode parcelles ONF
        this.typeCarte = PARCELLES_ONF;
        this.last_typeCarte = FORETS_ONF; // On revient au mode forêts ONF
        this.id_area_visible = this.last_id_section_visible; // On remet l'id de la zone visible à celui de la section
        this.fetch_new_geojson_data(FORETS_ONF, this.last_id_section_visible); // Recharge les données GeoJSON pour le type de carte forêts ONF
      } else if (
        this.typeCarte == FORETS_DGD ||
        this.typeCarte == FORETS_ONF ||
        this.typeCarte == COMMUNES
      ) {
        this.last_typeCarte = DEFAUT; // On revient au mode par défaut
      } else {
        // Si on est en mode par défaut, on ne fait rien
        this.typeCarte = this.defineTypeCarte(); // On reste en mode par défaut; // On reste en mode par défaut
        this.last_typeCarte = DEFAUT; // On reste en mode par défaut
        this.fetch_new_geojson_data(this.typeCarte);
      }
    },

    /**
     * Initialise la carte Leaflet avec les paramètres de configuration.
     * Définit la vue initiale, le niveau de zoom et le fond de carte.
     * Les paramètres de configuration sont importés depuis config-map.js et config-style.js.
     * @returns {void}
     * @see configMap pour les paramètres de configuration importés depuis config-map.js
     * @see styles pour les styles importés depuis config-style.js
     *
     */
    initMap() {
      const {
        INIT_VIEW,
        INIT_ZOOM,
        INIT_TILE,
        styles,
        baseTilesConfig,
        tileList,
        layers,
        configBaseSelect,
      } = configMap;
      // creation de la carte Leaflet
      this.map = L.map('map').setView(INIT_VIEW, INIT_ZOOM);

      // Pane dédié au périmètre OEASC, en dessous de l'overlayPane (z-index 400)
      this.map.createPane('perimetre-pane');
      this.map.getPane('perimetre-pane').style.zIndex = 350;
      this.map.getPane('perimetre-pane').style.pointerEvents = 'none';

      // #################### FOND DE CARTE ##############################
      // trouve la clé du fond de carte par défaut (normalement mapbox)
      const defaultTileKey = Object.keys(baseTilesConfig).find(
        (key) => tileList[key].default || baseTilesConfig[key]?.label === INIT_TILE
      );
      // récupère la configuration du fond de carte par défaut (url, attribution, id et label)
      const tileConf = baseTilesConfig[defaultTileKey];
      this.baseLayer = L.tileLayer(tileConf.url, {
        attribution: tileConf.attribution,
      }).addTo(this.map);
      // this.add_buttom_precedent_on_map();
    },

    /**
     * Récupère les données le geometrie GeoJSON à afficher sur la carte en fonction du type de carte sélectionné.
     * Si un id_area_parent est fourni, on récupère les zones enfants de cet id_area_parent.
     * Si aucun id_area_parent n'est fourni, on récupère les zones du type de carte
     * Cette fonction vérifie si les données sont déjà dans le cache avant de faire une requête.
     * @param id_type_carte int - Type de carte à charger (COMMUNES, SECTIONS, FORETS_DGD, FORETS_ONF, CADASTRES)
     * @param id_area_parent int ou null - si on veut les sections ou les cadastres, id_area_parent est l'id de la commune ou de la section concernée.
     */
    async fetch_new_geojson_data(id_type_carte, id_area_parent = null) {
      if (id_type_carte !== DEFAUT) {
        this.freeze_map = true; // Gèle la carte pour éviter les interactions pendant le chargement des données
        let geojson = { type: 'FeatureCollection', features: [] };
        // Charge les données GeoJSON en fonction du type de carte
        if (id_area_parent && id_type_carte) {
          // Si il y a un id_area_parent, cela concerne l' affichage des sections ou des cadastres
          if (this.is_layer_in_cache(id_type_carte, id_area_parent)) {
            geojson = this.get_layer_from_cache(id_type_carte, id_area_parent);
          } else {
            const fetched = await fetch_areas_child_of(id_area_parent, id_type_carte);
            this.save_layer_in_cache(id_type_carte, id_area_parent, fetched);
            geojson = fetched;
          }
        } else if (id_type_carte) {
          if (this.is_layer_in_cache(id_type_carte)) {
            geojson = this.get_layer_from_cache(id_type_carte);
          } else {
            const fetched = await fetch_areas_group_from_id_type(id_type_carte);
            this.save_layer_in_cache(id_type_carte, null, fetched);
            geojson = fetched;
          }
        }
        // Always ensure geojsonVisibleLayers is a valid FeatureCollection
        if (!geojson || !geojson.features) {
          geojson = { type: 'FeatureCollection', features: [] };
        }
        this.geojsonVisibleLayers = geojson;
        this.freeze_map = false; // Dé-gèle la carte après le chargement des données
      }
    },

    /**
     * retourne true si la couche de type id_type_carte est déjà dans le cache.
     * @param id_type_carte COMMUNES, SECTIONS, FORETS_DGD, FORETS_ONF ou CADASTRES
     * @param id_area peut etre null si on veut les couches de type communes, sections, forêts DGD et ONF.
     */
    is_layer_in_cache(id_type_carte, id_area = null) {
      // Vérifie si les données GeoJSON sont déjà dans le cache
      if (id_area) {
        return (
          this.layers_groupe_cache[id_type_carte] &&
          this.layers_groupe_cache[id_type_carte][id_area]
        );
      } else {
        return this.layers_groupe_cache[id_type_carte];
      }
    },

    /**
     * retourne le cache qui est dans la variable layers_groupe_cache
     * @param id_type_carte COMMUNES, SECTIONS, FORETS_DGD, FORETS_ONF ou CADASTRES
     * @param id_area peut etre null si on veut les couches de type communes, sections, forêts DGD et ONF.
     */
    get_layer_from_cache(id_type_carte, id_area = null) {
      // Récupère les données GeoJSON du cache
      if (id_area) {
        // Si un id_area est fourni, on récupère dans un sous-objet
        return this.layers_groupe_cache[id_type_carte]
          ? this.layers_groupe_cache[id_type_carte][id_area]
          : {};
      } else {
        // Sinon, on récupère directement
        return this.layers_groupe_cache[id_type_carte] || {};
      }
    },

    /**
     * Enregistre les données GeoJSON dans le cache. C'est dans la variable layers_groupe_cache
     * @param id_type_carte COMMUNES, SECTIONS, FORETS_DGD, FORETS_ONF ou CADASTRES
     * @param id_area peut etre null si on veut les couches de type communes, sections, forêts DGD et ONF.
     * @param geojson Les données GeoJSON à enregistrer dans le cache
     */
    save_layer_in_cache(id_type_carte, id_area = null, geojson) {
      // Enregistre les données GeoJSON dans le cache
      if (id_area) {
        // Si un id_area est fourni, on enregistre dans un sous-objet
        if (!this.layers_groupe_cache[id_type_carte]) {
          this.layers_groupe_cache[id_type_carte] = {};
        }
        this.layers_groupe_cache[id_type_carte][id_area] = geojson;
        return;
      } else {
        // Sinon, on enregistre directement
        this.layers_groupe_cache[id_type_carte] = geojson;
      }
    },

    /**
     * Ajoute le périmètre oeasc à la carte.
     * Le périmètre oeasc est affiché en noir et non sélectionnable.
     */
    add_layer_perimetre_oeasc() {
      if (!this.geom_perimetre_oeasc) return;

      const layer = L.geoJSON(this.geom_perimetre_oeasc, {
        style: styles.po,
        pane: 'perimetre-pane',
        interactive: false,
      }).addTo(this.map);
    },

    /**
     * foncion appelée lorsque l'utilisateur sélectionne une parcelle dans l'autocomplétion.
     * Si le type de carte est CADASTRES, on ajoute la parcelle à la liste des périmètres sélectionnés.
     * @param selectedId l'id_area de la parcelle selectionnée. Correspond à l'id_area dans le geojson de geojsonVisibleLayers.
     */
    onAutocompleteSelect(selectedId) {
      if (this.typeCarte == CADASTRES) {
        if (Array.isArray(selectedId)) {
          selectedId.forEach((id) => {
            if (!this.list_selected_areas.includes(id)) {
              this.list_selected_areas.push(id);
            }
          });
        } else if (selectedId && !this.list_selected_areas.includes(selectedId)) {
          this.list_selected_areas.push(selectedId);
        }
      }
    },

    /**
     * Definie le type de carte à afficher en fonction de ce qui à été selectionné dans le formulaire de déclaration.
     * si c'est une foret privée ou publique, avec ou sans document. Sert donc à initialiser ou réinitialiser l'affichage de la carte.
     */
    defineTypeCarte() {
      // Si le formulaire n'est pas encore rempli, on affiche la carte par défaut
      if (this.b_statut_public === null || this.b_document === null) {
        return DEFAUT; // Affiche la carte par défaut
      }

      if (this.b_document === true) {
        if (this.b_statut_public) {
          return FORETS_ONF; // public et avec document. On affiche les forêts ONF
        } else {
          return FORETS_DGD; // Privé et avec document. On affiche les forêts DGD
        }
      } else {
        return COMMUNES; // Si pas de document, on selectionne une zone via les communes
      }
    },

    /**
     * Initialise les zones sélectionnées en fonction des données de la déclaration.
     *
     * 1. Si des zones sont déjà sélectionnées dans `declaration_data.areas_localisation`,
     *    - Récupère les identifiants des zones sélectionnées.
     *    - Récupère la hiérarchie complète de ces zones via `fetch_hierarchy_areas`.
     *    - Réinitialise la liste des zones sélectionnées pour la remplir à nouveau selon la logique métier.
     * 2. Si aucune zone n'est sélectionnée, initialise la hiérarchie à une liste vide.
     *
     * Ensuite, selon le type de forêt ou de commune (déterminé par les propriétés `b_document` et `b_statut_public`),
     * remplit la liste des zones sélectionnées :
     *
     * - Si c'est une forêt ONF publique (`b_document` et `b_statut_public` à true) :
     *    - Ajoute la forêt ONF, ses parcelles ONF, et leurs unités de gestion (UG ONF) à la liste.
     * - Si c'est une forêt DGD privée (`b_document` à true et `b_statut_public` à false) :
     *    - Ajoute la forêt DGD et ses cadastres à la liste.
     * - Si ce n'est pas une forêt (`b_document` à false) :
     *    - Ajoute la commune, ses sections, et les cadastres enfants à la liste.
     *
     * Cette fonction permet donc de reconstruire la liste des zones sélectionnées selon la structure hiérarchique
     * et le type de déclaration, afin de garantir la cohérence des données pour la suite du traitement.
     */
    async initialise_areas() {
      const initialAreas = (this.declaration_data.areas_localisation || []).filter(
        (a) => a && a.id_area
      );

      if (initialAreas.length > 0) {
        // Collecte tous les id_area disponibles: feuilles (cor_areas_declarations) + niveaux
        // parents connus depuis les champs foret du backend (areas_foret_communes, etc.)
        // Cela permet à build_area_hierarchy de trouver les parents dans data_map.
        const allAreaIds = new Set(initialAreas.map((a) => a.id_area));
        [
          ...(this.declaration_data.areas_foret_communes || []),
          ...(this.declaration_data.areas_foret_sections || []),
          ...(this.declaration_data.areas_localisation_onf_prf || []),
          this.declaration_data.areas_foret_onf,
          this.declaration_data.areas_foret_dgd,
        ]
          .filter((id) => id !== null && id !== undefined)
          .forEach((id) => allAreaIds.add(id));

        this.list_selected_areas = [...allAreaIds];
        this.hierarchy_areas = await fetch_hierarchy_from_intersect(this.declaration_data);
        // Si la hiérarchie est indisponible, on conserve les données initiales du backend
        if (!this.hierarchy_areas?.length) {
          this.hierarchy_areas = [];
          return;
        }
        this.declaration_data.areas_localisation = []; // Reset seulement si hiérarchie valide
      } else {
        // Nouvelle déclaration ou état vide — initialiser les structures nécessaires
        this.hierarchy_areas = [];
        this.reset_areas();
        return;
      }

      // Traversée de la hiérarchie basée sur les types réels des nœuds (pas sur b_document)
      // afin de gérer les incohérences de données (ex: b_document incorrect par rapport aux areas stockées)
      this.hierarchy_areas.forEach((root) => {
        this.declaration_data.areas_localisation.push({ ...root, id_parent: null });
        (root.areas_enfant || []).forEach((child) => {
          this.declaration_data.areas_localisation.push({
            ...child,
            id_parent: root.id_area,
          });
          (child.areas_enfant || []).forEach((grandchild) => {
            this.declaration_data.areas_localisation.push({
              ...grandchild,
              id_parent: child.id_area,
            });
          });
        });
      });
    },
  },
};
</script>

<style scoped>
#map {
  width: 100%;
}

#button_retour {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1000;
}
</style>
