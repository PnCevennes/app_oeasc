export default (data, options, restitution) => {

  /**
   * Options de configuration pour un graphique personnalisé.
   *
   * @constant
   * @type {Object}
   * @property {Object} title - Configuration du titre du graphique.
   * @property {string} title.text - Texte affiché comme titre du graphique, défini par `options.title`.
   * @property {Object} xAxis - Configuration de l'axe des abscisses.
   * @property {Array<string>} xAxis.categories - Catégories affichées sur l'axe X, générées à partir de `data` sous la forme "texte (compte)".
   * @property {Object} yAxis - Configuration de l'axe des ordonnées.
   * @property {Object} yAxis.title - Titre de l'axe Y.
   * @property {string} yAxis.title.text - Texte affiché pour l'axe Y ("nb").
   * @property {Array<Object>} series - Liste des séries de données à afficher.
   * @property {string} series[].type - Type de graphique (ex: "bar", "column"), défini par `options.typeGraph`.
   * @property {string} series[].name - Nom de la série, récupéré depuis `restitution.items[options.field_name].text`.
   * @property {boolean} series[].colorByPoint - Si vrai, chaque point de la série aura une couleur différente.
   * @property {Array<Object>} series[].data - Données de la série, chaque objet représentant une catégorie.
   * @property {string} series[].data[].name - Nom de la catégorie, sous la forme "texte (compte)".
   * @property {number} series[].data[].y - Valeur numérique associée à la catégorie.
   * @property {string|null} series[].data[].color - Couleur du point (null pour couleur par défaut).
   * @property {string} height - Hauteur du graphique (ex: "600px").
   * @property {string} width - Largeur du graphique (ex: "600px").
   *
   * @description
   * Cette configuration est utilisée pour générer un graphique personnalisé dans un composant Vue.js,
   * typiquement avec une bibliothèque de graphiques telle que Highcharts ou Chart.js.
   * Elle permet d'afficher des données dynamiques, où les catégories et les valeurs sont extraites
   * d'un tableau `data` et les options de rendu sont personnalisables via l'objet `options`.
   * 
   * Utilisation typique : 
   * - Affichage de statistiques ou de rapports dans un tableau de bord.
   * - Visualisation de données issues d'une API ou d'une base de données.
   */
  const chartOptions = {
    title: {
      text: options.title
    },
    xAxis: {
      categories: data.map(d => `${d.text} (${d.count})`)
    },
    yAxis: {
      // min: -0.01,
      // endOnTick: false,
      // startOnTick: false,
      title: {
        text: "nb"
      }
    },
    series: [
      {
        type: options.typeGraph,
        name: restitution.items[options.field_name].text,
        colorByPoint: true,
        data: data.map(d => ({
          name: `${d.text} (${d.count})`,
          y: d.count,
          color: null
        }))
      }
    ],
    height: "600px",
    width: "600px"
  };
  return chartOptions;
};
