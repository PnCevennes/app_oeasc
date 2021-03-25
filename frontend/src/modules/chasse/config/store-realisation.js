export default {
  group: "chasse",
  name: "realisation",
  label: "Réalisation",
  serverSide: true,
  
  genre: "F",
  columns: ["saison", "attribution", "auteur_tir", "auteur_constat"],
  form: {
    forms: ["saison", "attribution", "auteur_tir", "auteur_constat"]
  },
  options: {
    page: 1,
    itemsPerPage: 5,
    sortBy: ["saison"],
    sortDesc: [true]
  },
  defs: {
    // // table
    // id_realisation: {
    //   label: "ID"
    // },
    // numero_bracelet: {
    //   label: "No Bracelet"
    // },
    // nom_saison: {
    //   label: "Saison"
    // },
    // nom_auteur_tir: {
    //   label: "Auteur tir"
    // },
    // nom_auteur_constat: {
    //   label: "Auteur constat"
    // },
    // nom_zone_cynegetique_realisee: {
    //   label: "Zone cynégétique réalisée"
    // },
    // id_attribution: {
    //   label: "Attribution",
    //   storeName: "chasseAttribution",
    //   displayFieldName: "label",
    //   list_type: 'autocomplete',
    //   params: ({baseModel}) => ({
    //     sortBy: ['label'],
    //     sortDesc: [true],
    //     itemsPerPage: 10,
    //     id_saison: baseModel['id_saison']
    //   }),

    // form
    saison: {
      label: "Saison",
      storeName: "chasseSaison",
      returnObject: true,
      params: {
        sortBy: ["nom_saison"],
        sortDesc: [true],
        itemsPerPage: 10
      },
      required: true
    },
    attribution: {
      label: "Attribution",
      storeName: "chasseAttribution",
      returnObject: true,
      params: ({ baseModel }) => ({
        sortBy: ["numero_bracelet"],
        sortDesc: [false],
        itemsPerPage: 10,
        id_saison: baseModel.saison && baseModel.saison.id_saison
      }),
      disabled: ({ baseModel }) =>
        !(baseModel.saison && baseModel.saison.id_saison),
      required: true
    },
    auteur_tir: {
      label: "Auteur tir",
      list_type: "combobox",
      returnObject: true,
      storeName: "chassePersonne",
      params: {
        sortBy: ["nom_personne"],
        sortDesc: [false],
        itemsPerPage: 10
      }
    },
    auteur_constat: {
      label: "Auteur constat",
      list_type: "combobox",
      returnObject: true,
      storeName: "chassePersonne",
      params: {
        sortBy: ["nom_personne"],
        sortDesc: [false],
        itemsPerPage: 10
      }
    },

    id_zone_cynegetique_realisee: {
      label: "Zone cynégétique réalisée",
      storeName: "chasseZoneCynegetique",
      returnObject: true,
      params: {
        sortBy: ["nom_zone_cinegetique"],
        sortDesc: [false],
        itemsPerPage: 10
      }
    },

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


    // attribution: {
    //   label: "Attribution",
    //   list_type: 'autocomplete',
    //   type: 'list_form',
    //   params: ({baseModel}) => ({
    //     sortBy: ['label'],
    //     sortDesc: [true],
    //     itemsPerPage: 10,
    //     id_saison: baseModel['id_saison']
    //   })
    // },
    // id_auteur_tir: {
    //   label: "Auteur tir",
    //   storeName: "chassePersonne"
    // },
    // id_auteur_constat: {
    //   label: "Auteur constat",
    //   storeName: "chassePersonne"
    // },
    // id_realisation: {
    //   label: "ID prout",
    //   hidden: true,
    //   displayFieldName: "numero_bracelet"
    // },
    // id_zone_cynegetique_affectee: {
    //   label: "Zone cynégétique affectée",
    //   storeName: "chasseZoneCynegetique",
    //   disabled: true
    // },
    // id_zone_interet_affectee: {
    //   label: "Zone intérêt affectee",
    //   storeName: "chasseZoneInteret",
    //   disabled: true
    // },
    // id_zone_cynegetique_realisee: {
    //   label: "Zone cynégétique réalisée",
    //   storeName: "chasseZoneCynegetique"
    // },
    // id_zone_interet_realisee: {
    //   label: "Zone intérêt réalisée",
    //   storeName: "chasseZoneInteret"
    // },
    // id_lieu_tir: {
    //   label: "Lieu de tir",
    //   storeName: "chasseLieuTir"
    // },
    // date_exacte: {
    //   label: "Date exacte",
    //   type: "date"
    // },
    // date_enreg: {
    //   label: "Date enregistrement",
    //   type: "date"
    // },
    // mortalite_hors_pc: {
    //   label: "Mortalité hors Parc",
    //   type: "bool_switch"
    // },
    // parcelle_onf: {
    //   label: "Parcelle ONF",
    //   type: "bool_switch"
    // },
    // id_nomenclature_sexe: {
    //   label: "Sexe",
    //   type: "nomenclature",
    //   storeName: "commonsNomenclature",
    //   nomenclatureType: "SEXE"
    // },
    // id_nomenclature_classe_age: {
    //   label: "Classe d'age",
    //   type: "nomenclature",
    //   storeName: "commonsNomenclature",
    //   nomenclatureType: "STADE_VIE"
    // },
    // id_nomenclature_mode_chasse: {
    //   label: "Mode de chasse",
    //   type: "nomenclature",
    //   storeName: "commonsNomenclature",
    //   nomenclatureType: "OEASC_MOD_CHASSE"
    // },
    // poid_entier: {
    //   label: "Poid entier",
    //   type: "number",
    //   min: 0
    // },
    // poid_vide: {
    //   label: "Poid vide",
    //   type: "number",
    //   min: 0
    // },
    // poid_c_f_p: {
    //   label: "Poid CFP",
    //   type: "number",
    //   min: 0
    // },
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
