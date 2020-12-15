import { config as mainConfig} from '@/config/config.js';

// configuration principale pour les cartes
const mainMapConfig = mainConfig.map;
const preConfigMap = mainConfig.preConfigMap;

const mapConfig = {

  // attribue les valeur de la configuration principale à la configuration courante this._config 
  makeConfigDefault: function() {

    if(!this._config) {
      return false
    }
    // this._config = this._config || {}
    
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

    return true;
  },

  processConfig: function() {
    return this.makeConfigDefault();
  }
};

const staticMapConfig = {
  getPreConfigMap(preConfigMapName) {
    return preConfigMap[preConfigMapName];
  }
}

export { mapConfig, staticMapConfig };
