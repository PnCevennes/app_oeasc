export default {
  coordsFieldName: "centroid",
  items: {
    declaration_date: {
      text: 'Date',
      process: (d, options) => {
        return d[options.name].split('/').splice(1).join('/');
      },
      type: 'date',
    },
    degat_gravite: {
      text: 'Gravite',
      process: (d, options) => {
        options;
        let out = d.degats || [];
        out = out.map(d => (d.degat_essences)||[]).map(d => (d||{})).flat().map(d => d.degat_gravite_label).filter(d => !!d);
        return out;
        // return (d.degats|| []).map(d => (d.degat_essences || [])).map(d => d.degat_gravite_label);
      },
      color: {
        "Importants": "red",
        "Modérés": "orange",
        "Faibles": "yellow",
      },
    },
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
      },
      zoomOnFilter: "label",
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
