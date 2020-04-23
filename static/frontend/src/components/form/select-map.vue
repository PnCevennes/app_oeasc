<template>
  <div>
    <div>
      <h4>
        Localisation :
        {{ legend }}
      </h4>
      <!-- {{ config.containerName }} {{ baseModel[config.containerName] }} -->
      <div>
        Veuillez selectionner
        {{ description }}
        sur la carte ci-dessous ou dans la liste ci-contre.
        <help code="selection_carte"></help>
      </div>
    </div>

    <base-map v-if="mapConfig" :config="mapConfig" :mapId="config.name">
      <template v-slot:aside>
        <div class="aside-select">
          <div class="btn-pre-select"
              v-if="
                baseModel.b_statut_public === false &&
                  baseModel.b_document === true
              "
          >
            <v-btn
              small
              :block="false"
              color="error"
              @click="baseModel.b_statut_public=false; baseModel.b_document=false"
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
            :chips="config.multiple ? true :false"
            :small-chips="config.multiple ? true :false"
            hide-selected
            :deletable-chips="config.multiple ? true :false"
            clearable
            placeholder="Choisir un element dans la liste"
            @change="selectChange"
          >
          <help slot="append" :code="`form-${config.name}`" v-if="config.help"></help>
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
</template>

<script>
import baseMap from "@/modules/map/base-map";
import { selectMapMethods } from "./select-map.js";
import help from "./help";

export default {
  name: "selectMap",
  components: { baseMap, help },
  data: () => ({
    dataSelect: null,
    mapService: null,
    mapConfig: null,
    selectContainer: null,
    legend: null,
    description: null,
    name: null
  }),
  methods: selectMapMethods,
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
    document
      .getElementById(this.config.name)
      .addEventListener("layer-data", this.initSelect);

    document
      .getElementById(this.config.name)
      .addEventListener("select-map-click", this.clickOnLayer);

    this.mapService = this.$store.getters.mapService(this.config.name);
    this.mapService.addLayerLegend({
      style: this.mapConfig.styles.select,
      legend: "Sélection"
    });
  }
};
</script>
