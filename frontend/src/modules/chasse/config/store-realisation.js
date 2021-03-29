export default {
  group: "chasse",
  name: "realisation",
  label: "Réalisation",
  serverSide: true,

  genre: "F",
  columns: [
    "saison",
    "attribution",
    "auteur_tir",
    "auteur_constat",
    "zone_cynegetique_realisee",
    "zone_interet_realisee",
    "lieu_tir",
    "date_exacte",
    "nomenclature_sexe",
    "nomenclature_classe_age"
  ],
  form: {
    groups: [
      {
        title: "Bracelet",
        forms: ["saison", "attribution"],
        direction: "row"
      },
      {
        title: "Localisation",
        groups: [
          {
            forms: ["zone_cynegetique_affectee", "zone_cynegetique_realisee"],
            direction: "row"
          },
          {
            forms: ["zone_interet_affectee", "zone_interet_realisee"],
            direction: "row"
          },
          {
            forms: ["lieu_tir", "mortalite_hors_pc", "parcelle_onf"],
            direction: "row"
          }
        ]
      },
      {
        title: "Informations (auteur, date)",
        groups: [
          {
            forms: ["auteur_tir", "auteur_constat"],
            direction: "row"
          },
          {
            forms: ["date_exacte", "date_enreg"],
            direction: "row"
          }
        ]
      },
      {
        title: "Information animal",
        groups: [
          {
            forms: ["nomenclature_sexe", "nomenclature_classe_age"],
            direction: "row"
          },
          {
            forms: ["poid_entier", "poid_vide", "poid_c_f_p"],
            direction: "row"
          }
        ]
      }
    ]
    // forms: ["saison", "attribution", "auteur_tir", "auteur_constat", "zone_cynegetique_realisee", "zone_cynegetique_affectee"]
  },
  options: {
    page: 1,
    sortBy: ["saison"],
    sortDesc: [true]
  },
  defs: {
    // // table
    // id_realisation: {
    //   label: "ID"
    // },

    // form
    saison: {
      label: "Saison",
      storeName: "chasseSaison",
      type: 'list_form',
      list_type: 'select',
      returnObject: true,
      required: true
    },
    attribution: {
      label: "Attribution",
      storeName: "chasseAttribution",
      type: "list_form",
      list_type: "autocomplete",
      dataReloadOnSearch: true,
      returnObject: true,
      displayFieldName: 'numero_bracelet',
      params: ({ baseModel }) => ({
        id_saison: baseModel.saison && baseModel.saison.id_saison
      }),
      disabled: ({ baseModel }) =>
        !(baseModel.saison && baseModel.saison.id_saison),
      required: true
    },
    auteur_tir: {
      label: "Auteur tir",
      type: 'list_form',
      list_type: "combobox",
      returnObject: true,
      dataReloadOnSearch: true,
      storeName: "chassePersonne"
    },
    auteur_constat: {
      label: "Auteur constat",
      type: 'list_form',
      list_type: "combobox",
      returnObject: true,
      dataReloadOnSearch: true,
      storeName: "chassePersonne"
    },
    zone_cynegetique_affectee: {
      label: "Zone cynégétique affectee",
      storeName: "chasseZoneCynegetique",
      type: 'list_form',
      list_type: 'select',
      returnObject: true,
      disabled: true,
    },
    zone_cynegetique_realisee: {
      label: "Zone cynégétique réalisée",
      storeName: "chasseZoneCynegetique",
      type: 'list_form',
      list_type: 'select',
      returnObject: true,
    },
    zone_interet_affectee: {
      label: "Zone d'intérêt affectée",
      storeName: "chasseZoneInteret",
      type: 'list_form',
      list_type: "autocomplete",
      returnObject: true,
      dataReloadOnSearch: true,
      disabled: true
    },
    zone_interet_realisee: {
      label: "Zone d'intérêt réalisée",
      storeName: "chasseZoneInteret",
      type: 'list_form',
      list_type: "autocomplete",
      returnObject: true,
      dataReloadOnSearch: true,
      // params: ({ baseModel }) => ({
      //   id_zone_cynegetique: baseModel.zone_cynegetique_realisee &&
      //   baseModel.zone_cynegetique_realisee.id_zone_cynegetique
      // }),
      // disabled: ({ baseModel }) =>
      //   !(
      //     baseModel.zone_cynegetique_realisee &&
      //     baseModel.zone_cynegetique_realisee.id_zone_cynegetique
      //   )
    },
    lieu_tir: {
      label: "Lieu de tir",
      storeName: "chasseLieuTir",
      list_type: "autocomplete",
      type: 'list_form',
      returnObject: true,
      dataReloadOnSearch: true,
      // params: ({ baseModel }) => ({
      //   id_zone_interet: baseModel.zone_interet_realisee &&
      //   baseModel.zone_interet_realisee.id_zone_interet
      // }),
      // disabled: ({ baseModel }) =>
      //   !(
      //     baseModel.zone_interet_realisee &&
      //     baseModel.zone_interet_realisee.id_zone_interet
      //   )
    },
    date_exacte: {
      label: "Date exacte",
      type: "date"
    },
    date_enreg: {
      label: "Date enregistrement",
      type: "date"
    },
    mortalite_hors_pc: {
      label: "Mortalité hors Parc",
      type: "bool_switch"
    },
    parcelle_onf: {
      label: "Parcelle ONF",
      type: "bool_switch"
    },
    nomenclature_sexe: {
      label: "Sexe",
      type: "nomenclature",
      returnObject: true,
      list_type: "select",
      storeName: "commonsNomenclature",
      nomenclatureType: "SEXE"
    },
    nomenclature_classe_age: {
      label: "Classe d'age",
      type: "nomenclature",
      returnObject: true,
      list_type: "select",
      storeName: "commonsNomenclature",
      nomenclatureType: "STADE_VIE"
    },

    // id_nomenclature_mode_chasse: {
    //   label: "Mode de chasse",
    //   type: "nomenclature",
    //   storeName: "commonsNomenclature",
    //   nomenclatureType: "OEASC_MOD_CHASSE"
    // },
    poid_entier: {
      label: "Poid entier",
      type: "number",
      min: 0
    },
    poid_vide: {
      label: "Poid vide",
      type: "number",
      min: 0
    },
    poid_c_f_p: {
      label: "Poid CFP",
      type: "number",
      min: 0
    }
    // long_mandibules_droite: {
    //   label: "Longueur mandibules droite",
    //   type: "number",
    //   min: 0
    // },
    // long_mandibules_gauche: {
    //   label: "Longueur mandibules gauche",
    //   type: "number",
    //   min: 0
    // },
    // long_dagues_droite: {
    //   label: "Longueur dagues droite",
    //   type: "number",
    //   min: 0
    // },
    // long_dagues_gauche: {
    //   label: "Longueur dagues gauche",
    //   type: "number",
    //   min: 0
    // },
    // cors_nb: {
    //   label: "Nombre de cors",
    //   type: "number",
    //   min: 0
    // },
    // cors_commentaires: {
    //   label: "Commentaires (cors)",
    //   type: "text_area"
    // },
    // gestation: {
    //   label: "gestation",
    //   type: "boolean"
    // },
    // commentaires: {
    //   label: "Commentaires (général)",
    //   type: "text_area"
    // }
  }
  // form: {
  //   forms: ['auteur_tir'],
  //   groups_: [
  //     {
  //       title: "Attribution",
  //       forms: ["id_attribution"]
  //     },
  //     {
  //       title: "Tir",
  //       forms: ["date_exacte", "auteur_tir"],
  //       direction: "row"
  //     },
  //     {
  //       title: "Constat",
  //       forms: ["date_enreg", "auteur_constat"],
  //       direction: "row"
  //     },
  //     {
  //       title: "Localisation",
  //       groups: [
  //         {
  //           forms: [
  //             "id_zone_cynegetique_affectee",
  //             "id_zone_cynegetique_realisee"
  //           ],
  //           direction: "row"
  //         },
  //         {
  //           forms: ["id_zone_interet_affectee", "id_zone_interet_realisee"],
  //           direction: "row"
  //         },
  //         {
  //           forms: ["id_lieu_tir", "mortalite_hors_pc", "parcelle_onf"],
  //           direction: "row"
  //         }
  //       ]
  //     },
  //     {
  //       title: "Description",
  //       groups: [
  //         {
  //           forms: ["id_nomenclature_sexe", "id_nomenclature_classe_age"],
  //           direction: "row"
  //         },
  //         {
  //           forms: ["poid_entier", "poid_vide", "poid_c_f_p"],
  //           direction: "row"
  //         }
  //       ]
  //     },
  //     {
  //       title: "Description avancée (cerf)",
  //       condition: ({baseModel, $store}) => {
  //         // cerf + sexe + age
  //         const nomenclature_sexe = $store.getters.nomenclature(
  //           baseModel.id_nomenclature_sexe
  //         );
  //         const nomenclature_classe_age = $store.getters.nomenclature(
  //           baseModel.id_nomenclature_classe_age
  //         );

  //         const attribution = $store.getters.chasseAttribution(
  //           baseModel.id_attribution
  //         );

  //         return nomenclature_classe_age && nomenclature_classe_age.label_fr == 'Adulte'
  //         && nomenclature_sexe && nomenclature_sexe.label_fr == 'Mâle'
  //         && attribution && attribution.label.includes('Cerf');
  //       },
  //       groups_: [
  //         {
  //           direction: "row",
  //           groups: [
  //             {
  //               title: "Mandibules",
  //               forms: ["long_mandibules_gauche", "long_mandibules_droite"]
  //             },
  //             {
  //               title: "Dagues",
  //               forms: ["long_dagues_gauche", "long_dagues_droite"]
  //             }
  //           ]
  //         },
  //         {
  //           title: "Cors",
  //           forms: ["cors_nb", "cors_commentaires"]
  //         }
  //       ]
  //     }
  //   ]
  // },
};

// id_saison: {
//   label: "Saison",
//   storeName: "chasseSaison",
//   list_type: "autocomplete",
//   params: {
//     sortBy: ["nom_saison"],
//     sortDesc: [true],
//     itemsPerPage: 10
//   },
//   default: ({ $store }) => {
//     return $store
//       .dispatch($store.getters.configStore("chasseSaison").get, {
//         value: true,
//         fieldName: "current"
//       })
//       .then(saison => {
//         return saison.id_saison;
//       });
//   }
