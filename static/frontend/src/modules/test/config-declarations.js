export default {
  coordsFieldName: "centroid",
  items: {
    degat_types_label: {
      text: "Dégât",
      split: ", "
    },
    secteur: {
      text: "Secteur",
      split: ", ",
      color: {
        "Causses et Gorges": "#e8e805",
        "Mont Aigoual": "red",
        "Mont Lozère": "blue",
        "Vallées cévenoles": "green"
      }
    },
    organisme: {
      text: "Organisme",
      name: "organisme",
      split: ", "
    },
    type_foret: {
      text: "Type de forêt",
      name: "type_foret",
      split: ", "
    },
    communes: {
      text: "Commune",
      name: "communes",
      split: ", "
    },
    declarant: {
      text: "Déclarant",
      name: "declarant",
      split: ", "
    },
    b_peuplement_paturage_presence: {
      text: "Pâturage",
      replace: [
        [true, "Oui"],
        [false, "Non"]
      ]
    },
    b_peuplement_protection_existence: {
      text: "Protection",
      replace: [
        [true, "Oui"],
        [false, "Non"]
      ]
    },
    peuplement_acces_label: {
      text: "Accès au peuplement",
      split: ", "
    },
    peuplement_ess_1_label: {
      text: "Essence principale",
      split: ", "
    }
  }
};
