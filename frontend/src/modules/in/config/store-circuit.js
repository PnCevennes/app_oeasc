export default {
  group: "in",
  name: "circuit",
  label: "Circuit",
  serverSide: true,
  defs: {
    id_circuit: {
      label: "ID",
      hidden: true
    },
    secteur: {
      label: "Secteur",
      type: "list_form",
      list_type: "select",
      storeName: "commonsSecteur",
      returnObject: true,
      required: true
    },
    nom_circuit: {
      label: "Nom",
      type: "text",
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
    }
  }
};
