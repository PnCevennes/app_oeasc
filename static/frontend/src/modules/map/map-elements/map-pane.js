// definitions des différents panes (valeur + 600 pour le z-index)


const paneDefinions = {
    PANE_TILE: 0,
    PANE_FOND_1: 11,
    PANE_FOND_2: 12,
    PANE_FOND_3: 13,
    PANE_FOND_4: 14,
    PANE_FOND_5: 15,
    PANE_LAYER_1: 21,
    PANE_LAYER_2: 22,
    PANE_LAYER_3: 23,
    PANE_LAYER_4: 24,
    PANE_LAYER_5: 25,
    PANE_TOOLTIP: 40

}

const mapPane = {
    // initialise les différent panes
    initPanes: function() {
            for (const [key, value] of Object.entries(paneDefinions)) {
              const paneName = key;
              this._map.createPane(paneName);
              this._map.getPane(paneName).style.zIndex = 600 + value;
            }
          }
}

export { mapPane };