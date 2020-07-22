import { copy } from "@/core/js/util/util.js";
import { config } from "@/config/config.js";
import { formFunctions } from "./functions/form.js";

const configBaseSelect = config.map.configBaseSelect;

const selectMapMethods = {
  initMapConfig: function() {
    const selectRef = this.$refs[`select_map_${this.config.name}`];
    if (selectRef) {
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
      const ruleContainer = v =>
        !(!v || (Array.isArray(v) && v.length != 0)) ||
        `Veuillez ${
          this.config.multiple ? "ajouter un élément suplémentaire et / ou" : ""
        } et appuyer sur "VALIDER LA SELECTION" pour passer à la selection des ${this.config.legend.toLowerCase()}`;
      this.rules = this.config.required
        ? this.config.multiple
          ? [formFunctions.rules.requiredListMultiple, ruleContainer]
          : [formFunctions.rules.requiredListSimple, ruleContainer]
        : [];
      url =
        typeof this.config.containerUrl === "function"
          ? this.config.containerUrl(this.baseModel)
          : this.config.containerUrl;

      this.name = this.config.containerName;
    } else {
      legend = this.config.legend;
      this.description = this.config.description;
      this.rules = this.config.rules;
      url =
        typeof this.config.url === "function"
          ? this.config.url({
              baseModel: this.baseModel,
              areasContainer: this.baseModel[this.config.containerName]
            })
          : this.config.url;
      this.name = this.config.name;
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
    if (this.mapService) {
      this.mapService._config.layers[this.config.name].legend = this.legend;
    }
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
    this.updateLayers(false);
  },

  selectChange: function() {
    this.updateLayers();
  },

  clickOnLayer: function(event) {
    const value = event.detail.id_area;

    if (!this.config.multiple) {
      this.baseModel[this.name] = value;
    } else {
      const index = this.baseModel[this.name].indexOf(value);
      if (index > -1) {
        this.baseModel[this.name].splice(index, 1);
      } else {
        this.baseModel[this.name].push(value);
      }
    }

    this.updateLayers();
  },

  updateLayers: function(bChange = true) {
    // bChange pour ne pas executer la function change à l'initialisation du composant
    bChange &&
      this.config.change &&
      this.config.change({
        baseModel: this.baseModel,
        config: this.config,
        $store: this.$store
      });

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
    let model = copy(this.baseModel[this.name]) || [];
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
