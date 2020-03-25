import { copy } from "@/core/js/util/util.js";
import { config } from "@/config/config.js";
import { formFunctions } from "./functions";

const configBaseSelect = config.map.configBaseSelect;

const selectMapMethods = {
  initMapConfig: function() {
    const selectRef = this.$refs[`select_map_${this.config.name}`]
    if(selectRef) {
      this.$refs[`select_map_${this.config.name}`].resetValidation();
    }
    const layerList = {
      po: {}
    };

    let legend = "",
      url = "";

    if (this.selectContainer) {
      legend = this.config.containerLegend;
      this.description = this.config.containerDescription;
      this.rules = this.config.required
        ? this.config.multiple
          ? [formFunctions.rules.requiredListMultiple]
          : [formFunctions.rules.requiredListSimple]
        : [];
      url =
        typeof this.config.containerUrl === "function"
          ? this.config.containerUrl(this.baseModel)
          : this.config.containerUrl;
      this.model = this.containerModel;
    } else {
      legend = this.config.legend;
      this.description = this.config.description;
      this.rules = this.config.rules;
      url =
        typeof this.config.url === "function"
          ? this.config.url({baseModel: this.baseModel, areasContainer: this.containerModel[this.config.name]})
          : this.config.url;
      this.model = this.baseModel;
    }

    this.legend = legend;
    const selectLayerConfig = {
      ...configBaseSelect,
      ...{
        legend,
        url
      }
    };

    layerList[this.config.name] = selectLayerConfig;

    this.mapConfig = {
      layerList
    };

    // swap legend
    this.mapService && this.mapService.setLayerLegendText(this.config.name, this.legend);

  },

  initSelect: function(event) {
    if (event.detail.key === this.config.name) {
      this.dataSelect = this.mapService
        .findLayers("key", this.config.name)
        .map(layer => {
          const properties = layer.feature.properties;
          const elem = {};
          for (const [key, fieldName] of Object.entries(
            this.config.dataFieldNames
          )) {
            elem[key] = properties[fieldName];
          }
          return elem;
        });
    }
    this.updateLayers();
  },

  selectChange: function() {
    this.updateLayers();
  },

  clickOnLayer: function(event) {
    const value = event.detail.id_area;

    if (!this.config.multiple) {
      this.model[this.config.name] = value;
    } else {
      const index = this.model[this.config.name].indexOf(value);
      if (index > -1) {
        this.model[this.config.name].splice(index, 1);
      } else {
        this.model[this.config.name].push(value);
      }
    }

    this.updateLayers();
  },

  updateLayers: function() {
    // for()
    const layerConfig = this.mapConfig.layerList[this.config.name];

    const styles = {
      normal: layerConfig.style,
      select: layerConfig.select.style
    };

    // selected => normal
    const layers = this.mapService.findLayers("selected", true);
    for (const layer of layers) {
      layer.feature.properties.selected = false;
      layer.curStyle = styles.normal;
      layer.setStyle(layer.curStyle);
    }

    // model => selected
    let model = copy(this.model[this.config.name]) || [];
    if (!Array.isArray(model)) {
      model = [model];
    }

    for (const id_area of model) {
      const layer = this.mapService.findLayer("id_area", id_area);
      if (!layer) {
        continue;
      }
      layer.feature.properties.selected = true;
      layer.curStyle = styles.select;
      layer.setStyle(layer.curStyle);
    }
  },

  reinitContainer: function() {
    this.selectContainer = true;
    this.baseModel[this.config.name] = this.config.multiple ? [] : null;

    let layers = null;

    layers = this.mapService.findLayers("key", this.config.name);
    this.mapService.removeLayers(layers);

    // load new layer + select
    this.initMapConfig();

    this.mapService.addLayer({
      ...this.mapConfig.layerList[this.config.name],
      key: this.config.name
    });
  },

  validerContainer: function() {
    this.selectContainer = false;
    let layers = null;
    // zoom on layer selected
    layers = this.mapService.findLayers("selected", true);
    this.mapService.zoomOnLayers(layers);

    // remove layer container
    layers = this.mapService.findLayers("key", this.config.name);
    this.mapService.removeLayers(layers);

    // load new layer + select
    this.initMapConfig();

    this.mapService.addLayer({
      ...this.mapConfig.layerList[this.config.name],
      key: this.config.name
    });

    //
  }
};

export { selectMapMethods };
