
/**
 * Methodes pour calculer la configuration du graphe highchart pour le rendu générique
 */


/**
 * configuration des series pour les cas 'simple'
 */
const seriesSimple = (data, typeGraph, text) => {
  console.log(typeGraph, text)
  return [
    {
      type: typeGraph,
      name: text,
      colorByPoint: true,
      data: data.map(d => ({
        name: `${d.text} (${d.count})`,
        y: d.count,
        color: null
      }))
    }
  ];

};

/**
 * configuration des series pour les cas 'double'
 *
 * Attention code pas simple du tout!!!!
 * besoin de retourner les données
 *
 * on passe de
 *
 * [
 *    {"text": "Chevreuil", "count": 459, "data": [
 *        {"text": "Mâle", "count": 241},
 *        {"text": "Femelle", "count": 209},
 *        {"text": "Indéterminé", "count": 9}]},
 *    {"text": "Cerf", "count": 113, "data": [
 *        {"text": "Femelle", "count": 58},
 *        {"text": "Mâle", "count": 55}]}
 * ]
 *
 * à
 *
 * [ ...
 *    {
 *        name :`Mâle (296)`,
 *         data: [241, 55],
 *         color: null,
 *         type: typeGraph
 *    }
 *   ... ]
 *
 * TODO changer api
 * pour faire le traitement en backend et
 * pour que ce soit plus simple en frontend??
 */
const seriesRamifiees = (data, typeGraph) => {

  /**
   * counts dictionnaire: {
   *  <fieldName2>: <count_fieldName2>
   * }
   * pour chaque valeur de fieldName2 on compte le nombre total
   */
  const counts = {};
  for (const d of data) {
    for (const d2 of d.data) {
      if (counts[d2.text] == undefined) {
        counts[d2.text] = 0;
      }
      counts[d2.text] += d2.count
    }
  }

  /**
   * series tableau avec une ligne par entrée de counts
   */
  const series = Object.entries(counts)
    .map(([key, value]) => ({
      name :`${key} (${value})`,
      data: [],
      color: null,
      type: typeGraph
    })
  );

  /**
   * data pour les series:
   */
  for (const d of data) {
    for (const d2 of d.data) {
      const name = `${d2.text} (${counts[d2.text]})`;
      series.find(s => s.name == name).data.push(d2.count)
    }
  }


  return series;

}

/**
 * function qui calcule les options d'un graphe highchart en fonction de
 *
 *  * - data: données de type
 *    [ ...
 *      { text: <text> , count : <count>, (?data: [...{ text:<text>, count:<count> }}...] }
 *      ... ]
 * - options: dictionnaire
 *    - title : titre du graph
 *    - typeGraph : type du graph ('pie', 'bar')
 *    - restitution : TODO
 *      - seulement besoin de text pour graphe simple
 */
export default (data, options, text) => {

  // pour savoir si on a affaire à un graph 'simple' ou un graphe 'ramifié
  // sert pour le calcul des series
  const condDoubleGraph = options.fieldName2 && options.fieldName2 != options.fieldName;

  // pour les graph de type pie on ne traite pas les series ramifiées
  const series = condDoubleGraph && (options.typeGraph != 'pie')
  ? seriesRamifiees(data, options.typeGraph)
  : seriesSimple(data, options.typeGraph, text);

  console.log(series)

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
    series,
    height: "600px",
    width: "600px"
  };
  return chartOptions;
};
