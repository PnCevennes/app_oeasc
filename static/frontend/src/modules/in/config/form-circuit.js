export default {
  formDefs: {
    nom_circuit: {
      label: "Nom",
      type: "text",
      required: true
    },
    id_secteur: {
      label: "Secteur",
      type: "list_form",
      display: "select",
      storeName: "inSecteur",
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
    // ug_tags: {
    //   type: "list_form",
    //   display: "combobox",
    //   label: "Tags",
    //   maxLength: 4,
    //   multiple: true,
    //   url: "api/in/tags/",
    //   valueFieldName: "tag",
    //   displayFieldName: "tag"
    // }
  },
  //   groups: [
  //     {
  //       title: "Informations",
  //       forms: ["date_realisation", "id_circuit", "serie", "observers"]
  //     },
  //     {
  //       title: "Météo",
  //       direction: "row",
  //       forms: ["temperature", "temps", "vent"]
  //     },
  //     {
  //       title: 'Observations',
  //       forms: ["groupes", "observations"]
  //     }
  //   ],

  title: ({ id }) =>
    id ? `Modificiation du circuit ${id}` : "Création d'un circuit",
  switchDisplay: ({ id }) => !!id,
  displayValue: ({ id }) => !!id,
  displayLabel: true,
  storeName: "inCircuit",
  idFieldName: "id_circuit"
};
