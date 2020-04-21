import './map-tooltip.css'

const mapTooltip = {
  addTooltip(layer, tooltipConfig, tooltipText) {
    console.log(this.addTooltip, tooltipText)
    let tooltipOptions = {
      pane: 'PANE_TOOLTIP',
      direction: 'center',
      opacity: 0.8,
      fillOpacity: 1
    };

    tooltipOptions = { ...tooltipOptions, ...tooltipConfig };

    layer.bindTooltip(tooltipText, tooltipOptions);
  }
};

export { mapTooltip };
