import { config as mainConfig } from '@/config/config.js';

// configuration principale pour les cartes
const mainMapConfig = mainConfig.map;
const preConfigMap = mainConfig.preConfigMap;

/**
 * Objet de configuration de la carte.
 *
 * @property {Function} makeConfigDefault - Initialise la configuration courante (`this._config`) avec les valeurs par défaut de `mainMapConfig`.
 *   - Si `this._config` n'existe pas, retourne `false`.
 *   - Pour chaque clé de `mainMapConfig`, attribue la valeur par défaut si elle n'est pas déjà définie dans `this._config`.
 *   - Initialise les couches (`layers`) à partir de `layerList` en fusionnant les propriétés de `mainMapConfig.layers` et `layerList`.
 *   - Retourne `true` si la configuration a été appliquée.
 *
 * @property {Function} processConfig - Traite la configuration en appelant `makeConfigDefault`.
 *   - Retourne le résultat de `makeConfigDefault`.
 */
const mapConfig = {
  // attribue les valeur de la configuration principale à la configuration courante this._config
  makeConfigDefault: function () {
    if (!this._config) {
      return false;
    }
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
          ...this._config.layerList[key],
        };
      }
    }
    return true;
  },

  processConfig: function () {
    return this.makeConfigDefault();
  },
};

const staticMapConfig = {
  getPreConfigMap(preConfigMapName) {
    return preConfigMap[preConfigMapName];
  },
};

export { mapConfig, staticMapConfig };
