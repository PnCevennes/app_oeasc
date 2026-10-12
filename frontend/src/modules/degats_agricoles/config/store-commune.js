// Communes de l'observatoire (ref_geo.communes_aoa), en lecture seule : sert aux
// listes de choix des déclarations de dégâts agricoles.
export default {
  group: 'agricole',
  name: 'commune',
  label: 'Commune',
  idFieldName: 'id',
  displayFieldName: 'nom',

  options: {
    sortBy: ['nom'],
    sortDesc: [false],
  },

  defs: {
    id: {
      label: 'ID',
      type: 'text',
      hidden: true,
    },
    nom: {
      label: 'Nom',
      type: 'text',
    },
    insee_com: {
      label: 'Code INSEE',
      type: 'text',
    },
  },
};
