<template>
  <div>
    <div>
      <h4>
        Localisation :
        {{ legend }}
      </h4>
      <div>
        Veuillez selectionner
        {{
          description
        }}
        sur la carte ci-dessous ou dans la liste ci-contre.
      </div>
    </div>
    <base-map v-if="mapConfig" :config="mapConfig" :mapId="config.name">
      <template v-slot:aside>
        <div style="width:400px">
          <v-autocomplete
            :ref="`select_map_${config.name}`"
            v-model="model[config.name]"
            v-if="dataSelect"
            :items="dataSelect"
            :label="
              `Liste des ${legend.toLowerCase()}`
            "
            :multiple="
              (selectChange && config.containerMultiple) || config.multiple
                ? true
                : false
            "
            :rules="rules"
            dense
            small-chips
            hide-selected
            deletable-chips
            clearable
            placeholder="Choisir un element dans la liste"
            @change="selectChange"
          ></v-autocomplete>
          <div v-if="config.containerUrl">
            <v-btn
              v-if="selectContainer"
              @click="validerContainer()"
              :disabled="
                !(
                  containerModel[config.name] &&
                  containerModel[config.name].length
                )
              "
            >
              Valider la selection
            </v-btn>
            <v-btn v-else @click="reinitContainer()">
              Retourner aux choix des {{ config.containerLegend }}
            </v-btn>
          </div>
        </div>
      </template>
    </base-map>
  </div>
</template>

<script>
import baseMap from "@/components/map/base-map";
import { selectMapMethods } from "./select-map.js";

export default {
  name: "selectMap",
  components: { baseMap },
  data: () => ({
    dataSelect: null,
    mapService: null,
    model: null,
    containerModel: {},
    mapConfig: null,
    selectContainer: null,
    legend:null,
    description:null
  }),
  methods: selectMapMethods,
  props: ["config", "baseModel"],
  created: function() {
    // add event on map-data-loaded

    this.containerModel[this.config.name] = this.config.containerMultiple
      ? []
      : null;
    this.selectContainer = this.config.containerUrl;

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
      legend: "Selection"
    });
  }
};
</script>
