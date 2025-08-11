/**
 * Configuration de l'entité "Attribution Massif" pour le module chasse.
 *
 * Cet objet exporté définit la configuration du store pour la gestion des attributions de massifs,
 * incluant les paramètres de pagination, de tri, et la définition des champs affichés dans l'interface.
 *
 * @property {string} group - Groupe fonctionnel auquel appartient cette configuration (ici, "chasse").
 * @property {string} name - Nom unique de la configuration (ici, "attributionMassif").
 * @property {string} label - Libellé affiché dans l'interface utilisateur.
 * @property {boolean} serverSide - Indique si la pagination et le tri sont gérés côté serveur.
 * @property {Object} options - Paramètres pour la requête GET (pagination, tri, etc.).
 * @property {number} options.page - Numéro de la page courante (par défaut 1).
 * @property {number} options.itemsPerPage - Nombre d'éléments par page (par défaut 20).
 * @property {number[]} options.itemsPerPageOptions - Options disponibles pour le nombre d'éléments par page.
 * @property {string[]} options.sortBy - Champs utilisés pour le tri initial.
 * @property {boolean[]} options.sortDesc - Ordre de tri pour chaque champ (true = décroissant).
 * @property {Object} defs - Définitions des champs affichés et éditables dans l'interface.
 *
 * @property {Object} defs.id_attribution_massif - Identifiant unique de l'attribution massif (caché à l'affichage).
 * @property {Object} defs.saison - Saison de chasse associée (sélection via liste déroulante liée au store "chasseSaison").
 * @property {Object} defs.espece - Espèce concernée (sélection via liste déroulante liée au store "commonsEspece").
 * @property {Object} defs.zone_cynegetique - Zone cynégétique concernée (sélection via liste déroulante liée au store "chasseZoneCynegetique").
 * @property {Object} defs.nb_affecte_min - Nombre minimum d'affectations (champ numérique, valeur minimale 0).
 * @property {Object} defs.nb_affecte_max - Nombre maximum d'affectations (champ numérique, valeur minimale 0).
 *
 * @example
 * // Utilisé dans les vues de gestion des attributions de massifs pour :
 * // - Afficher la liste paginée et triée des attributions
 * // - Permettre la création et l'édition d'une attribution via des formulaires dynamiques
 * // - Gérer les filtres et tris côté serveur pour de grandes volumétries de données
 */
export default {
  group: "chasse",
  name: "attributionMassif",
  label: "Attribution Massif",
  serverSide: true, // si pagination et tri sont gérés côté serveur


  options: { // paramètres ajoutés à la requête get
    page: 1,
    itemsPerPage: 20,
    itemsPerPageOptions: [20, 50, 100],
    sortBy: ["saison", "id_attribution_massif"],
    sortDesc: [true, true],
  },


  defs: {
    id_attribution_massif: {
      label: "ID",
      hidden: true
    },
    saison: {
        label: 'saison',
        storeName: 'chasseSaison',
        type: 'list_form',
        list_type: 'select',
        returnObject: true, // true si ca ne retourne pas qu'une valeur mais plusieurs dans un objet
    },
    espece: {
        label: 'Espèce',
        storeName: 'commonsEspece',
        type: 'list_form',
        list_type: 'select',
        returnObject: true, // true si ca ne retourne pas qu'une valeur mais plusieurs dans un objet
    },
    zone_cynegetique: {
        label: 'Zone Cinégétique',
        storeName: 'chasseZoneCynegetique',
        type: 'list_form',
        list_type: 'select',
        returnObject: true,
    },
    nb_affecte_min: {
        label: 'nb affecté min',
        type: 'number',
        min: 0
    },
    nb_affecte_max: {
        label: 'nb affecté max',
        type: 'number',
        min: 0
    }
  },
};
