// definitions des différents panes (valeur + 600 pour le z-index)

/**
 * Définit les identifiants numériques pour différents "panes" (couches) de la carte.
 * Chaque clé représente un type de couche spécifique utilisé dans la gestion de l'affichage cartographique.
 *
 * @constant
 * @type {Object}
 * @property {number} PANE_TILE - Couche de tuiles de base de la carte.
 * @property {number} PANE_FOND_1 - Première couche de fond personnalisée.
 * ...
 * @property {number} PANE_LAYER_5 - Cinquième couche de données superposées.
 * @property {number} PANE_MARKER_1 - Couche dédiée aux marqueurs principaux.
 * @property {number} PANE_TOOLTIP - Couche réservée à l'affichage des infobulles.
 */
const paneDefinions = {
  PANE_TILE: 200,
  PANE_FOND_1: 401,
  PANE_FOND_2: 402,
  PANE_FOND_3: 403,
  PANE_FOND_4: 404,
  PANE_FOND_5: 405,
  PANE_LAYER_1: 451,
  PANE_LAYER_2: 452,
  PANE_LAYER_3: 453,
  PANE_LAYER_4: 454,
  PANE_LAYER_5: 455,
  PANE_MARKER_1: 601,
  PANE_TOOLTIP: 652
};


const mapPane = {
  /**
   * Initialise les différents "panes" (couches) de la carte.
   * Pour chaque définition dans 'paneDefinions', une nouvelle couche est créée sur la carte
   * avec un nom correspondant à la clé et un z-index correspondant à la valeur.
   * Cela permet de gérer l'ordre d'affichage des éléments cartographiques (tuiles, fonds, couches, marqueurs, tooltips).
   */
  initPanes: function() {
    // Parcourt chaque entrée de l'objet 'paneDefinions'
    for (const [key, value] of Object.entries(paneDefinions)) {
      const paneName = key; // Nom du pane (ex: 'PANE_TILE', 'PANE_LAYER_1', etc.)
      this._map.createPane(paneName); // Crée le pane sur la carte
      // Définit le z-index du pane pour gérer la superposition des couches
      this._map.getPane(paneName).style.zIndex = value;
    }
  }
};

export { mapPane };
