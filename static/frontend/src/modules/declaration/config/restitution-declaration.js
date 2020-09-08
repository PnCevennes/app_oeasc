/** definitions pour la restitution des déclaration à partir des données de la vue */

import { processDegat, processDegatMarkerDefs } from "./utils";
export default {
  coordsFieldName: "centroid",
  dataType: "declaration",
  items: {
    declaration_date: {
      text: "Date",
      process: (d, options) => {
        return d[options.name]
          .split("/")
          .splice(1)
          .join("/");
      },
      type: "date"
    },
    degat_gravite_label: {
      text: "Dégâts - gravite",
      process: processDegat,
      processMarkerDefs: processDegatMarkerDefs,
      order: ["Faibles", "Modérés", "Importants"],
      color: {
        Importants: "red",
        Modérés: "orange",
        Faibles: "yellow"
      }
    },
    degat_essence_label: {
      text: "Dégâts - essence",
      process: processDegat,
      processMarkerDefs: processDegatMarkerDefs
    },
    degat_type_labels: {
      text: "Dégâts - type",
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
      },
      zoomOnFilter: "label"
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
    },
    valide: {
      text: "Validé"
    }
  },
  default: {
    display: "table",
    typeGraph: "column",
    nbMax1: 7,
    nbMax2: 7,
    // choix2: "degat_essence_label",
    choix1: "degat_gravite_label",
    // choix2: "degat_type_labels",
    n: 0,
    height: "600px",
    filters: {
      degat_type_labels: ["Frottis"]
    }
  },
  preFilters: {
    valide: ["Validé"]
  }
};
