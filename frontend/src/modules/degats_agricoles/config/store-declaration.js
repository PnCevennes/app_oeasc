export default {
  group: 'agricole',
  name: 'declaration',
  label: 'Déclaration dégâts',
  labels: 'Déclarations dégâts',
  genre: 'F',
  displayFieldName: 'numero_dossier',
  serverSide: true, // si pagination et tri sont gérés côté serveur

  options: {
    page: 1, // on affiche la première page par défaut
    itemsPerPage: 20,
    itemsPerPageOptions: [20, 50, 100],
    sortBy: ['saison', 'numero_dossier'],
    sortDesc: [true, true], // tri en ordre décroissant
  },

  defs: {
    id_declaration: {
      label: 'ID',
      type: 'text',
      hidden: true,
    },
    saison: {
      label: 'Saison',
      storeName: 'agricoleSaison',
      type: 'list_form',
      list_type: 'select',
      returnObject: true, // true si ca ne retourne pas qu'une valeur mais plusieurs dans un objet
      required: true,
    },
    numero_dossier: {
      label: 'N° dossier',
      type: 'text',
      required: true,
    },
    date_creation: {
      label: 'Date de création',
      type: 'date',
    },
    date_document: {
      label: 'Date document',
      type: 'date',
    },
    commune: {
      label: 'Commune',
      storeName: 'agricoleCommune',
      type: 'list_form',
      list_type: 'autocomplete',
      returnObject: true,
    },
    ug_agricole: {
      label: 'Unité de gestion',
      storeName: 'agricoleUgAgricole',
      type: 'list_form',
      list_type: 'select',
      returnObject: true,
    },
    culture: {
      label: 'Culture',
      storeName: 'agricoleCulture',
      type: 'list_form',
      list_type: 'autocomplete',
      returnObject: true,
    },
    espece: {
      label: 'Espèce',
      storeName: 'commonsEspece',
      type: 'list_form',
      list_type: 'select',
      returnObject: true,
    },
    surface_detruite: {
      label: 'Surface détruite (ha)',
      type: 'number',
      min: 0,
    },
    volume_detruit: {
      label: 'Volume détruit (qtx)',
      type: 'number',
      min: 0,
    },
    unit_quantite_detruite: {
      label: 'Unité quantité détruite',
      type: 'text',
    },
    pourcentage: {
      label: 'Pourcentage',
      type: 'number',
      min: 0,
      max: 100,
    },
    montant_paye: {
      label: 'Montant payé (€)',
      type: 'number',
    },
    surface_ressemis: {
      label: 'Surface ressemis (ha)',
      type: 'number',
      min: 0,
    },
    montant_paye_ressemis: {
      label: 'Montant payé ressemis (€)',
      type: 'number',
    },
    montant_total_paye: {
      label: 'Montant total payé (€)',
      type: 'number',
    },
  },
};
