/** fonctions pour
 *
 * gerer les données dégâts dans la restitution
 *   pour les essences et la gravité
 *
 */

import { restitution } from "@/modules/restitution/utils.js";

const listFieldDegetEssence = [
  "degat_gravite_label",
  "degat_etendue_label",
  "degat_essence_label",
  "degat_anteriorite_label"
];

const getDegats = (d, options) => {
  return (d.degats || []).filter(degat =>
    restitution.condFilter(degat.degat_type_label, {
      ...options,
      name: "degat_type_labels"
    })
  );
};

const getDegatEssences = (degat, options) => {
  let degat_essences = degat.degat_essences || [];
  for (const key of ["choix1", "choix2"].filter(key =>
    listFieldDegetEssence.includes(options[key])
  )) {

    const name = options[key];
    console.log(name);
    degat_essences = degat_essences.filter(
      degat_essence =>
        (!!degat_essence[name]) &&
        restitution.condFilter(degat_essence[name], {
          ...options,
          name: name
        })
    );
  }
  return degat_essences;
};

/**
 * pour donner une valeur à une déclaration (pour faire les dataList ensuite)
 * */
const processDegat = (d, options) => {
  options;
  let out = [];
  for (const degat of getDegats(d, options)) {
    for (const degat_essence of getDegatEssences(degat, options)) {
      if(degat_essence[options.name]) {
        out.push(degat_essence[options.name]);
      }
    }
  }

  return out;
};

/**
 * pour afficher les degat_gravite_label ou degat_essence_label (etendue, antériorité possible) sur la carte
 * ne marche que dans le cas ou choix1 champ courrant et choix 2 = degat_type_labels
 * */
const processDegatMarkerDefs = (d, options) => {
  if (
    !(
      options.choix1 == options.name &&
      (listFieldDegetEssence.includes(options.choix2) ||
        options.choix2 == "degat_type_labels") &&
      options.choix1 != options.choix2
    )
  ) {
    return;
  }


  const defs = [];
  for (const degat of getDegats(d, options)) {
    let color = "black";
    let icon = "pencil";
    if (options.choix2 == "degat_type_labels") {
      icon = restitution.icon(
        { degat_type_labels: degat.degat_type_label },
        options.dataList[0].data2,
        { name: "degat_type_labels" }
      )[0];
    }
    let val = null;
    let lastIndex = -1;
    for (const degat_essence of getDegatEssences(degat, options)) {
      const v = degat_essence[options.name];
      if (!v) {
        continue;
      }
      if (options.order && (options.choix2 == "degat_type_labels") && options.getMax) {
        const index = options.order.indexOf(v);
        if (index > lastIndex) {
          lastIndex = index;
          val = v;
        }
      } else {
        const dd = {};
        dd[options.choix1] = v;
        color = restitution.color(dd, options.dataList, {
          ...options,
          name: options.choix1,
          process: null
        })[0];
        if (options.choix2 != "degat_type_labels") {
          dd[options.choix2] = degat_essence[options.choix2];
          icon = restitution.icon(dd, options.dataList[0].data2, {
            ...options,
            name: options.choix2,
            process: null
          })[0];
        }
        // color = (options.dataList.find(d => d.text === v) || {}).color;
        defs.push({ color, icon });
      }
    }

    if (val) {
      const dd = {};
      dd[options.name] = val;
      color = restitution.color(dd, options.dataList, {
        ...options, 
        name: options.name, 
        process: null,
      })[0];
      defs.push({ color, icon });
    }
  }
  return defs;
};

// for (const degat of d.degats.filter(degat =>
//   restitution.condFilter(degat.degat_type_label, {
//     ...options,
//     name: "degat_type_labels"
//   })
// )) {
// let color = "black";
// let icon = "pencil";
// icon = restitution.icon(
//   { degat_type_labels: degat.degat_type_label },
//   options.dataList[0].data2,
//   { name: "degat_type_labels" }
// );

// cas gravite et degat_type => pire cas
// sinon tout
// si degat essences le pire des dégats => couleur et type_degat => icone

// let val = null;
// let lastIndex = -1;

// for (const degat_essence of (degat.degat_essences || []).filter(
//   degat_essence =>
//     restitution.condFilter(
//       degat_essence[options.name] && degat_essence[options.name],
//       {
//         ...options,
//         name: options.name
//       }
//     )
// )) {
//     const v = degat_essence[options.name];
//     if (!v) {
//       continue;
//     }

//     if (options.order && options.choix2 == "degat_type_labels") {
//       const index = options.order.indexOf(v);
//       if (index > lastIndex) {
//         lastIndex = index;
//         val = v;
//       }
//     } else {
//       const dd = {};
//       dd[options.name] = v;
//       color = restitution.color(dd, options.dataList, { name: options.name });
//       // color = (options.dataList.find(d => d.text === v) || {}).color;
//       console.log;
//       defs.push({ color, icon });
//     }
//   }

//   if (val) {
//     const dd = {};
//     dd[options.name] = val;
//     color = restitution.color(dd, options.dataList, { name: options.name });
//     defs.push({ color, icon });
//   }
// }
//   return defs;
// };

export { processDegat, processDegatMarkerDefs };
