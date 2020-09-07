import { restitution } from "@/modules/restitution/restitution-utils.js";
let i = 1;
export default {
  coordsFieldName: "centroid",
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
    degat_gravite: {
      text: "Gravite",
      process: (d, options) => {
        options;
        let out = d.degats || [];
        out = out
          .map(d => d.degat_essences || [])
          .map(d => d || {})
          .flat()
          .map(d => d.degat_gravite_label)
          .filter(d => !!d);
        return out;
        // return (d.degats|| []).map(d => (d.degat_essences || [])).map(d => d.degat_gravite_label);
      },
      processMarkerDefs: (d, options) => {
        restitution;
        options;
        d;

        if (i == 1) {
          i = 0;
          console.log(options);
        }

        const defs = [];
        if (!d.degats) {
          return defs;
        }

        for (const degat of d.degats) {
          let color = "black";
          let icon = "pencil";
          // filtre sur les dégâts
          const condFilter = !(
            options.filters &&
            options.filters.degat_types_label &&
            options.filters.degat_types_label.length &&
            !options.filters.degat_types_label.includes(degat.degat_type_label)
          );
          if (!condFilter) {
            continue;
          }

          // icon
          icon = restitution.icon(
            { degat_type_label: degat.degat_type_label },
            options.dataList[0].data2,
            { name: "degat_type_label" }
          );
          // si degat essences le pire des dégats => couleur et type_degat => icone
          let gravite = null;
          let gravites = ["Faibles", "Modérés", "Importants"];
          let lastIndex = -1;
          for (const degat_essence of degat.degat_essences || []) {
            if (!degat_essence.degat_gravite_label) {
              continue;
            }
            const index = gravites.indexOf(degat_essence.degat_gravite_label);

            if (index > lastIndex) {
              lastIndex = index;
              gravite = degat_essence.degat_gravite_label;
            }
          }

          if (gravite) {
            // color = restitution.color({degat_gravite: gravite}, options.dataList, options)
            color = options.color[gravite];
          }
          defs.push({ color, icon });
        }
        return defs;
      },
      color: {
        Importants: "red",
        Modérés: "orange",
        Faibles: "yellow"
      }
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
  filters: {
    valide: ["Validé"]
  }
};
