import './map-tooltip.css'

/**
 * Ajoute un tooltip à une couche de carte.
 *
 * @param {Object} layer - La couche de la carte à laquelle le tooltip sera ajouté.
 * @param {Object} tooltipConfig - Configuration supplémentaire pour le tooltip (ex : position, opacité, etc.).
 * @param {string} tooltipText - Texte à afficher dans le tooltip.
 *
 * @description
 * Cette méthode fusionne les options par défaut du tooltip avec celles fournies en paramètre,
 * puis lie le tooltip à la couche spécifiée. Le tooltip s'affichera au centre de la couche,
 * avec une opacité de 0.8 et une opacité de remplissage de 1, sauf si ces valeurs sont
 * modifiées dans la configuration.
 */
const mapTooltip = {
  addTooltip(layer, tooltipConfig, tooltipText) {
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
