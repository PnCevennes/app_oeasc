<!--
  Composant Vue.js : select-map.vue

  Ce composant permet à l'utilisateur de sélectionner une localisation soit via une carte interactive, soit via une liste déroulante.
  Il est principalement utilisé pour la sélection d'entités géographiques (ex : forêts, zones, etc.) dans un formulaire.

  Structure du template :
  - Affichage d'un titre et d'une légende dynamique liée à la localisation.
  - Affichage d'une description et d'une aide contextuelle pour guider l'utilisateur dans la sélection.
  - Utilisation du composant <base-map> pour afficher une carte interactive si la configuration de la carte (mapConfig) est présente.
    - Un slot "aside" permet d'afficher des éléments complémentaires à côté de la carte :
      - Bouton spécifique pour le cas où la forêt n'apparaît pas dans la liste, avec gestion de l'état du modèle.
      - Champ d'autocomplétion (<v-autocomplete>) pour sélectionner un élément dans une liste, avec gestion des règles de validation, du mode multiple, des chips, et de l'aide contextuelle.
      - Gestion de la validation ou de la réinitialisation de la sélection du conteneur via des boutons, selon la configuration.
  - Les différentes conditions d'affichage permettent d'adapter l'interface selon le contexte et les données du modèle.

  Points importants :
  - Les props et variables utilisées (legend, config, baseModel, mapConfig, dataSelect, etc.) doivent être définies dans la partie script du composant.
  - L'intégration de composants d'aide (<help>) permet d'améliorer l'expérience utilisateur en fournissant des explications contextuelles.
  - La logique métier (ex : gestion du statut public, validation de la sélection) est directement liée à l'état du modèle (baseModel).

  Ce composant est conçu pour être réutilisable et adaptable à différents types de sélections géographiques dans l'application.
-->
<!-- 
<template>
  <div>
    <div>
      <h4>
        Localisation :
        {{ legend }}
      </h4>
      <!-- {{ config.containerName }} {{ baseModel[config.containerName] }} -->
<!-- <div>
        Sélectionnez sur la carte ou dans la liste
        {{ description }}.
        <help code="selection_carte"></help>
      </div>
    </div>

    <base-map v-if="mapConfig" :config="mapConfig" :mapId="config.name">
      <template v-slot:aside>

        <div class="aside-select"> 
          <div
            class="btn-pre-select"
            v-if="
              baseModel.b_statut_public === false &&
                baseModel.b_document === true &&
                name == 'areas_foret_dgd'
            "
          >
            <v-btn
              small
              :block="false"
              color="error"
              @click="
                baseModel.b_statut_public = false;
                baseModel.b_document = false;
              "
            >
              Ma forêt n'apparait pas sur la liste
            </v-btn>
            <help code="foret_apparait_pas"></help>
          </div>

          <v-autocomplete
            :ref="`select_map_${config.name}`"
            v-model="baseModel[name]"
            v-if="dataSelect"
            :items="dataSelect"
            :label="`Liste des ${legend.toLowerCase()}`"
            :multiple="
              (selectChange && config.containerMultiple) || config.multiple
                ? true
                : false
            "
            :rules="rules"
            dense
            :chips="config.multiple ? true : false"
            hide-selected
            :closable-chips="config.multiple ? true : false"
            clearable
            placeholder="Choisir un element dans la liste"
            @change="selectChange"
          >
            <help
              slot="append"
              :code="`form-${config.name}`"
              v-if="config.help"
            ></help>
          </v-autocomplete>
          <div v-if="config.containerUrl">
            <v-btn
              v-if="selectContainer"
              @click="validerContainer()"
              :disabled="
                !(
                  baseModel[config.containerName] &&
                  baseModel[config.containerName].length
                )
              "
            >
              Valider la selection
            </v-btn>
            <v-btn small color="error" v-else @click="reinitContainer()">
              Retourner aux choix des {{ config.containerLegend }}
            </v-btn>
          </div>
        </div>
      </template>
    </base-map>
  </div>
</template> -->

<script>
// Composant vidé de son template/script par un commit précédent ("menage et commentaires dans le code")
// mais toujours importé et rendu (en no-op) par dynamic-form.vue. Ce stub minimal préserve ce comportement ;
// webpack tolérait un SFC sans <template> ni <script>, le compilateur SFC de Vite/Vue 3 non.
export default { name: 'selectMap' };
</script>

<!-- <script>

import { selectMapMethods } from "./select-map.js";
import help from "./help.vue";

export default {
  name: "selectMap",
  components: { baseMap: () => import("@/components/map/base-map.vue"), help },
  data: () => ({
    dataSelect: null,
    mapService: null,
    mapConfig: null,
    selectContainer: null,
    legend: null,
    description: null,
    name: null
  }),
  methods: selectMapMethods, // intégre toutes les méthodes du fichier select-map.js
  props: ["config", "baseModel"],
  created: function() {
    // add event on map-data-loaded

    this.selectContainer =
      this.config.containerUrl &&
      !(this.config.multiple
        ? this.baseModel[this.config.name].length
        : this.baseModel[this.config.name]);
    this.initMapConfig();
  },
  mounted: function() {
    setTimeout(() => {
      document
        .getElementById(this.config.name)
        .addEventListener("layer-data", this.initSelect);

      document
        .getElementById(this.config.name)
        .addEventListener("select-map-click", this.clickOnLayer);

      this.mapService = this.$store.getters.mapService(this.config.name);
      this.mapService._config.layers["selection"] = {
        style: this.mapConfig.styles.select,
        legend: "Sélection"
      };
    }, 300);


</script> -->
