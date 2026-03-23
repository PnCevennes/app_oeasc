/**
 * Configuration d'exportation de carte pour le composant Vue.js.
 *
 * @property {Object} formDefs - Définitions des champs du formulaire d'exportation.
 * @property {Object} formDefs.filename - Champ pour le nom du fichier exporté.
 * @property {string} formDefs.filename.label - Libellé affiché pour le champ du nom de fichier.
 * @property {string} formDefs.filename.type - Type de champ, ici texte.
 * @property {Array<Function>} formDefs.filename.rules - Règles de validation pour le nom de fichier.
 *   - Vérifie que le nom se termine par ".png" ou ".jpg".
 * @property {boolean} formDefs.filename.required - Indique si le champ est obligatoire.
 * @property {Object} formDefs.height - Champ pour la hauteur de l'image exportée.
 * @property {string} formDefs.height.label - Libellé affiché pour la hauteur.
 * @property {string} formDefs.height.type - Type de champ, ici nombre.
 * @property {Object} formDefs.width - Champ pour la largeur de l'image exportée.
 * @property {string} formDefs.width.label - Libellé affiché pour la largeur.
 * @property {string} formDefs.width.type - Type de champ, ici nombre.
 * @property {string} title - Titre du formulaire d'exportation affiché à l'utilisateur.
 */
export default {
  formDefs: {
    filename: {
      label: 'nom du fichier',
      type: 'text',
      rules: [
        (u) =>
          ['.jpg', '.png'].some((v) => u.toLowerCase().endsWith(v)) ||
          'Le nom du fichier doit se terminer par ".png" ou ".jpg"',
      ],
      required: true,
    },
    height: {
      label: 'Hauteur',
      type: 'number',
    },
    width: {
      label: 'Largeur',
      type: 'number',
    },
  },

  title: 'Exporter la carte au format png',
};
