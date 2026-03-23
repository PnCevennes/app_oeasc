export default {
  formDefs: {
    nom_circuit: {
      label: 'Nom',
      type: 'text',
      required: true,
    },
    id_secteur: {
      label: 'Secteur',
      type: 'list_form',
      list_type: 'select',
      storeName: 'commonsSecteur',
      required: true,
    },
    numero_circuit: {
      label: 'Numéro',
      type: 'number',
      required: true,
      min: 0,
    },
    km: {
      label: 'Distance (km)',
      type: 'number',
      required: true,
      min: 0,
    },
    actif: {
      label: 'Actif',
      type: 'bool_switch',
      required: true,
      min: 0,
    },
  },

  title: ({ id }) => (id ? `Modificiation du circuit ${id}` : "Création d'un circuit"),
  switchDisplay: ({ id }) => !!id,
  displayValue: ({ id }) => !!id,
  displayLabel: true,
  storeName: 'inCircuit',
};
