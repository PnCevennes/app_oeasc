import { config as mainConfig} from '@/config/config.js';

// configuration principale pour les cartes
const mainMapConfig = mainConfig.map;
const preConfigMap = mainConfig.preConfigMap;

const mapConfig = {

  // attribue les valeur de la configuration principale à la configuration courante this._config 
  makeConfigDefault: function() {

    // default values from mainMapConfig
    for (const key of Object.keys(mainMapConfig)) {
      this._config[key] = this._config[key] || mainMapConfig[key];
    }

    // Layers depuis mapConfig.layerList
    this._config.layers = {};
    if (this._config.layerList) {
      for (const key of Object.keys(this._config.layerList)) {
        this._config.layers[key] = {
          ...mainMapConfig.layers[key],
          ...this._config.layerList[key]
        };
      }
    }
  },

  processConfig: function() {
    this.makeConfigDefault();
    return true;
  }
};

const staticMapConfig = {
  getPreConfigMap(preConfigMapName) {
    return preConfigMap[preConfigMapName];
  }
}

export { mapConfig, staticMapConfig };
