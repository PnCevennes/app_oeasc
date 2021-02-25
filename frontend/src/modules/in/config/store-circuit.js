export default {
  group: "in",
  name: "circuit",
  label: "Circuit",
  defs: {
    id_circuit: {
      label: "ID",
      hidden: true
    },
    id_secteur: {
      label: "Secteur",
      type: "list_form",
      list_type: "select",
      storeName: "commonsSecteur",
      required: true
    },
    nom_circuit: {
      label: "Nom",
      required: true
    },
    numero_circuit: {
      label: "Numéro",
      type: "number",
      required: true,
      min: 0
    },
    km: {
      label: "Distance (km)",
      type: "number",
      required: true,
      min: 0
    },
    actif: {
      label: "Actif",
      type: "bool_switch",
      required: true,
      min: 0
    },
  }
};
