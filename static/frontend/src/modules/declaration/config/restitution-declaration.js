/** definitions pour la restitution des déclaration à partir des données de la vue */
import restitutionUtils from "@/modules/restitution/utils.js";

export default {
  coordsFieldName: "centroid",
  dataType: "declaration",
  items: {
    declaration_date: {
      text: "Date",
      process: (d, item) => {
        return d[item.key]
          .split("/")
          .splice(1)
          .join("/");
      },
      type: "date"
    },
    degat_gravite_label: {
      text: "Dégâts - gravite",
      // order: ["Faibles", "Modérés", "Importants"],
      colors: {
        Importants: "red",
        Modérés: "orange",
        Faibles: "yellow"
      }
    },
    degat_essence_label: {
      text: "Dégâts - essence"
    },
    degat_type_label: {
      text: "Dégâts - type"
    },
    secteur: {
      text: "Secteur",
      process: restitutionUtils.split(", "),
      colors: {
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
      process: restitutionUtils.split(", ")
    },
    type_foret: {
      text: "Type de forêt",
      name: "type_foret",
      process: restitutionUtils.split(", ")
    },
    communes: {
      text: "Commune",
      name: "communes",
      process: restitutionUtils.split(", ")
    },
    declarant: {
      text: "Déclarant",
      name: "declarant",
      process: restitutionUtils.split(", ")
    },
    b_peuplement_paturage_presence: {
      text: "Pâturage",
      process: restitutionUtils.replace([
        [true, "Oui"],
        [false, "Non"]
      ])
    },
    b_peuplement_protection_existence: {
      text: "Protection",
      process: restitutionUtils.replace([
        [true, "Oui"],
        [false, "Non"]
      ])
    },
    peuplement_acces_label: {
      text: "Accès au peuplement",
      process: restitutionUtils.split(", ")
    },
    peuplement_ess_1_label: {
      text: "Essence principale",
      process: restitutionUtils.split(", ")
    },
    valide: {
      text: "Validé"
    }
  },
  default: {
    dataType: "declaration",
    display: "map",
    typeGraph: "column",
    nbMax1: 7,
    nbMax2: 7,
    choix2: "degat_essence_label",
    choix1: "degat_gravite_label",
    // choix2: "degat_type_labels",
    n: 0,
    height: "600px",
    filters: {
      degat_type_label: ["Frottis"]
    },
    preFilters: {
      valide: ["Validé"]
    },
    yTitle: 'Nombre de dégâts',  
  },
};
