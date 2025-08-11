

/**
 * Génère un titre de localisation basé sur les propriétés de l'objet `data`.
 *
 * Cette fonction est utilisée pour afficher un titre descriptif dans l'interface utilisateur,
 * en fonction de la zone géographique sélectionnée par l'utilisateur dans le module chasse.
 * Elle vérifie successivement la présence des propriétés suivantes dans l'objet `data` :
 * - `nom_zone_indicative` : Si présente, retourne " - ZI : <nom_zone_indicative>"
 * - `nom_zone_cynegetique` : Si présente, retourne " - ZC : <nom_zone_cynegetique>"
 * - `nom_secteur` : Si présente, retourne " - Secteur : <nom_secteur>"
 * Si aucune de ces propriétés n'est définie, retourne une chaîne vide.
 *
 * @param {Object} data - Objet contenant les informations de localisation.
 * @param {string} [data.nom_zone_indicative] - Nom de la zone indicative (ZI).
 * @param {string} [data.nom_zone_cynegetique] - Nom de la zone cynégétique (ZC).
 * @param {string} [data.nom_secteur] - Nom du secteur.
 * @returns {string} Titre formaté pour la localisation, ou chaîne vide si aucune information n'est disponible.
 */
const localisationTitle = (data) => {
  return data.nom_zone_indicative
? ` - ZI : ${data.nom_zone_indicative}`
: data.nom_zone_cynegetique
  ? ` - ZC : ${data.nom_zone_cynegetique}`
  : data.nom_secteur
    ? ` - Secteur : ${data.nom_secteur}`
    : ''
};

/**
 * Génère des textes descriptifs pour différents types de données de chasse.
 *
 * @param {Object} data - L'objet contenant les informations sur le type de données.
 * @param {string} data.data_type - Le type de données à traiter, attendu 'poids' ou autre (par exemple 'longueur').
 * @returns {Object} Un objet contenant :
 *   - {string} dataTypeTitle : Le titre à afficher selon le type de données ('Masse corporelle' ou 'Longueur des dagues').
 *   - {string} dataTypeAxis : Le label de l'axe pour un graphique ('Poids (kg)' ou 'Longueur des dagues (mm)').
 *   - {string} dataTypeSerie : Le nom de la série de données pour un graphique ou un tableau.
 *
 * @example
 * // Utilisé pour configurer dynamiquement les textes d'affichage dans des graphiques Vue.js
 * const config = dataTxt({ data_type: 'poids' });
 * // config = {
 * //   dataTypeTitle: 'Masse corporelle',
 * //   dataTypeAxis: 'Poids (kg)',
 * //   dataTypeSerie: 'Poids vide moyen (kg)'
 * // }
 *
 * // Cette fonction est typiquement utilisée dans les composants Vue.js affichant des graphiques ou des tableaux
 * // où le type de données (poids ou longueur) peut varier selon le contexte utilisateur.
 */
const dataTxt = (data) => {
  return {
    dataTypeTitle: data.data_type == 'poids' ? 'Masse corporelle' : 'Longueur des dagues',
    dataTypeAxis: data.data_type == 'poids' ? 'Poids (kg)' : 'Longueur des dagues (mm)',
    dataTypeSerie: data.data_type == 'poids' ? 'Poids vide moyen (kg)' : 'Longueur des dagues (mm)',
  }
}

export {
  localisationTitle,
  dataTxt
}