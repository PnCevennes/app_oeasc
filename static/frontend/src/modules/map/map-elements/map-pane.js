// definitions des différents panes (valeur + 600 pour le z-index)

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
  // initialise les différent panes
  initPanes: function() {
    for (const [key, value] of Object.entries(paneDefinions)) {
      const paneName = key;
      this._map.createPane(paneName);
      this._map.getPane(paneName).style.zIndex = value;
    }
  }
};

export { mapPane };
