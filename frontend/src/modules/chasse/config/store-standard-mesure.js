// Fourchettes standard (poids, longueur de dagues) par espèce, classe d'âge et sexe.
// Utilisées par la page « Données aberrantes » (sexe vide = tous les sexes).
export default {
  group: 'chasse',
  name: 'standardMesure',
  label: 'Standard de mesure',
  labels: 'Standards de mesures',
  genre: 'M',
  serverSide: true,

  columns: [
    'espece',
    'nomenclature_classe_age',
    'nomenclature_sexe',
    'mesure',
    'valeur_min',
    'valeur_max',
  ],

  options: {
    page: 1,
    sortBy: ['espece', 'mesure'],
    sortDesc: [false, false],
  },

  defs: {
    id_standard: {
      label: 'ID',
      type: 'text',
      hidden: true,
    },

    espece: {
      label: 'Espèce',
      storeName: 'commonsEspece',
      type: 'list_form',
      list_type: 'select',
      returnObject: true,
      required: true,
    },

    nomenclature_classe_age: {
      label: "Classe d'âge",
      type: 'nomenclature',
      returnObject: true,
      list_type: 'select',
      storeName: 'commonsNomenclature',
      codes: ['1', '2', '3', '5'],
      nomenclatureType: 'STADE_VIE',
      required: true,
    },

    nomenclature_sexe: {
      label: 'Sexe (vide = tous)',
      type: 'nomenclature',
      returnObject: true,
      list_type: 'select',
      storeName: 'commonsNomenclature',
      codes: ['3', '2', '1'],
      nomenclatureType: 'SEXE',
      clearable: true,
    },

    mesure: {
      label: 'Mesure (poid_entier, poid_vide, poid_c_f_p, long_dagues)',
      type: 'list_form',
      list_type: 'select',
      items: ['poid_entier', 'poid_vide', 'poid_c_f_p', 'long_dagues'],
      required: true,
    },

    valeur_min: {
      label: 'Valeur minimum (kg ou mm)',
      type: 'number',
      min: 0,
    },

    valeur_max: {
      label: 'Valeur maximum (kg ou mm)',
      type: 'number',
      min: 0,
    },
  },
};
