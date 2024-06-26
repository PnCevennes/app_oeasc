/** definitions pour la restitution des déclaration à partir des données de la vue */
import restitutionUtils from "@/modules/restitution/utils.js";

export default {
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
      text: "Dégâts - gravité",
      order: ["Indéfini", "Faibles", "Modérés", "Importants"],
      colors: {
        Importants: "red",
        Modérés: "orange",
        Faibles: "yellow",
      }
    },
    degat_etendue_label: {
      text: "Dégâts - étendue",
      order: ['Indéfini', "Localisés", "Généralisés"],
      colors: {
        "Généralisés": "red",
        "Localisés": "yellow"
      }
    },
    degat_anteriorite_label: {
      text: "Dégâts - anteriorité",
      order: [
        'Indéfini',
        "Ne sais pas",
        "Anciens (années antérieures)",
        "Récurrents",
        "Récents (année en cours)",
      ],
      colors: {
        "Récents (année en cours)": "red",
        "Récurrents": "orange",
        "Anciens (années antérieures)": "yellow"
      }
    },
    degat_gravite_label_max: {
      source: 'degat_gravite_label',
      text: "Dégâts - gravite (max)",
      patch: 'degat_type_label',
    },
    degat_etendue_label_max: {
      source: 'degat_etendue_label',
      text: "Dégâts - étendue (max)",
      patch: 'degat_type_label',
    },
    degat_anteriorite_label_max: {
      source: 'degat_anteriorite_label',
      text: "Dégâts - antériorité (max)",
      patch: 'degat_type_label',
    },

    degat_essence_label: {
      text: "Dégâts - essence"
    },
    peuplement_type_label: {
      text: "Peuplement - type"
    },
    degat_type_label: {
      text: "Dégâts - type"
    },
    secteur: {
      text: "Secteur",
      process: restitutionUtils.split(", "),
      colors: {
        "Causses et Gorges": "#e8e805",
        "Aigoual": "red",
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
    // communes: {
    //   text: "Commune",
    //   name: "communes",
    //   process: restitutionUtils.split(", ")
    // },
    // declarant: {
    //   text: "Déclarant",
    //   name: "declarant",
    //   process: restitutionUtils.split(", ")
    // },
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
    // peuplement_acces_label: {
    //   text: "Accès au peuplement",
    //   process: restitutionUtils.split(", ")
    // },
    peuplement_ess_1_label: {
      text: "Essence principale",
      process: restitutionUtils.split(", ")
    },
    valide: {
      // text: "Validé"
    },
    id_declaration: {}
  },
  default: {
    groupByKeyItems: [
      {
        value: null,
        text: "Nombre de dégâts"
      },
      {
        value: "id_declaration",
        text: "Nombre de déclarations"
      }
    ],
    display:'graph',
    typeGraph:'bar',
    stacking:false,
    coordsFieldName: "centroid",
    groupByKey: "id_declaration",
    markersGroupByKey: "id_declaration",
    markersGroupByReduceKeys: [
      "degat_type_label",
      "degat_gravite_label",
      "degat_etendue_label",
      "degat_anteriorite_label",
      "degat_essence_label"
    ],
    dataType: "declaration",
    nbMax1: 7,
    nbMax2: 7,
    choix1: "degat_type_label",
    // choix2: "degat_essence_label",
    // choix2: "degat_gravite_label",
    n: 0,
    height: "600px",
    filters: {
        // secteur: ['Causses et Gorges']
    },
    preFilters: {
      valide: ["Validé"]
    },
  }
};
