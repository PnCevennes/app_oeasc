import { formFunctions } from "@/components/form/functions/form";

export default {
  group: "chasse",
  name: "realisation",
  label: "Réalisation",
  serverSide: true,
  genre: "F",
  columns: [
    "saison",
    "attribution",
    "date_exacte",
    "auteur_tir",
    "auteur_constat",
    "zone_cynegetique_realisee",
    "zone_indicative_realisee",
    "lieu_tir_synonyme",
    "nomenclature_sexe",
    "nomenclature_classe_age",
    "nomenclature_mode_chasse"
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
        condition: ({ baseModel }) =>
          baseModel.attribution && baseModel.attribution.id_attribution,
        groups: [
          {
            direction: "row",
            groups: [
              {
                title: "Zone cynégetique",
                forms: [
                  "zone_cynegetique_affectee",
                  "zone_cynegetique_realisee"
                ]
              },
              {
                title: "Zone indicative",
                forms: ["zone_indicative_affectee", "zone_indicative_realisee"]
              },
              {
                title: "Informations",
                groups: [
                  {
                    forms: ["mortalite_hors_pc", "parcelle_onf"]
                  }
                ]
              }
            ]
          },
          {
            title: "Lieu de tir",
            groups: [
              {
                forms: ["lieu_tir_synonyme"]
              }
            ]
          }
        ]
      },
      {
        title: "Informations",
        condition: ({ baseModel }) =>
          baseModel.attribution && baseModel.attribution.id_attribution,
        direction: "row",
        groups: [
          {
            title: "Auteurs",
            forms: ["auteur_tir", "auteur_constat"]
          },
          {
            title: "Dates",
            forms: [
              "date_exacte_fast",
              "date_exacte",
              "date_enreg_fast",
              "date_enreg"
            ]
          },
          {
            title: "Compléments",
            forms: ["nomenclature_mode_chasse"]
          }
        ]
      },
      {
        title: "Information animal",
        condition: ({ baseModel }) =>
          baseModel.attribution && baseModel.attribution.id_attribution,
        direction: "row",
        groups: [
          {
            title: "Général",
            forms: ["nomenclature_sexe", "nomenclature_classe_age", "gestation"]
          },
          {
            title: "Poids",
            forms: ["poid_entier", "poid_vide", "poid_c_f_p"]
          }
        ]
      },
      {
        title: "Description avancée (cerf)",
        condition: ({ baseModel }) =>
          baseModel.nomenclature_classe_age &&
          ["Adulte", "Sub-adulte"].includes(
            baseModel.nomenclature_classe_age.label_fr
          ) &&
          baseModel.nomenclature_sexe &&
          baseModel.nomenclature_sexe.label_fr == "Mâle",
        direction: "row",
        groups: [
          {
            groups: [
              // {
              //   title: "Mandibules",
              //   forms: ["long_mandibules_gauche", "long_mandibules_droite"],
              //   direction: "row"
              // },
              {
                title: "Dagues",
                forms: ["long_dagues_gauche", "long_dagues_droite"],
                direction: "row"
              },
              {
                title: "Cors",
                forms: ["cors_nb"]
              }
            ]
          },
          {
            forms: ["cors_commentaires"]
          }
        ]
      },
      {
        condition: ({ baseModel }) =>
          baseModel.attribution && baseModel.attribution.id_attribution,
        title: "Commentaires",
        forms: ["commentaire"]
      }
    ]
  },
  options: {
    page: 1,
    sortBy: ["saison", "date_exacte"],
    sortDesc: [true, true]
  },
  defs: {
    // // table
    id_realisation: {
      label: "ID",
      hidden: true
    },

    // form
    saison: {
      label: "Saison",
      storeName: "chasseSaison",
      type: "list_form",
      list_type: "select",
      returnObject: true,
      required: true,
      // on ne change pas la saison pour un update
      disabled: ({ baseModel }) => !!baseModel.id_realisation,
      default: ({ $store }) => $store._actions.lastSaison[0]($store)
    },
    attribution: {
      label: "Attribution",
      storeName: "chasseAttribution",
      type: "list_form",
      list_type: "autocomplete",
      dataReloadOnSearch: true,
      returnObject: true,
      displayFieldName: "numero_bracelet",
      params: ({ baseModel }) => {
        const params = {
          id_saison: baseModel.saison && baseModel.saison.id_saison
        };
        // si on crée une nouvelle réalisation :
        //   - on choisit parmi des attributions sans réalisation
        if (!baseModel.id_realisation) {
          params.has_realisation = false;
        }

        return params;
      },
      required: true,
      change: ({ baseModel, $store }) => {
        if (!baseModel.attribution) {
          return;
        }

        // on n'affecte que si ce n'est pas déja fait

        baseModel.zone_cynegetique_affectee =
          baseModel.zone_cynegetique_affectee ||
          baseModel.attribution.zone_cynegetique_affectee;

        baseModel.zone_cynegetique_realisee =
          baseModel.zone_cynegetique_realisee ||
          baseModel.attribution.zone_cynegetique_affectee;

        baseModel.zone_indicative_affectee =
          baseModel.zone_indicative_affectee ||
          baseModel.attribution.zone_indicative_affectee;

        baseModel.zone_indicative_realisee =
          baseModel.zone_indicative_realisee ||
          baseModel.attribution.zone_indicative_affectee;

        $store.dispatch('setClearableTabIndex');
      }
    },
    auteur_tir: {
      label: "Auteur tir",
      type: "list_form",
      list_type: "combobox",
      returnObject: true,
      dataReloadOnSearch: true,
      storeName: "chassePersonne"
    },
    auteur_constat: {
      label: "Auteur constat",
      type: "list_form",
      list_type: "combobox",
      returnObject: true,
      dataReloadOnSearch: true,
      storeName: "chassePersonne"
    },
    zone_cynegetique_affectee: {
      label: "Zone cynégétique affectee",
      storeName: "chasseZoneCynegetique",
      type: "list_form",
      list_type: "select",
      returnObject: true,
      disabled: true
    },
    zone_cynegetique_realisee: {
      label: "Zone cynégétique réalisée",
      storeName: "chasseZoneCynegetique",
      type: "list_form",
      list_type: "select",
      returnObject: true,
      required: true
      // changed: ({baseModel}) => {}
    },
    zone_indicative_affectee: {
      label: "Zone indicative affectée",
      storeName: "chasseZoneIndicative",
      type: "list_form",
      list_type: "autocomplete",
      returnObject: true,
      dataReloadOnSearch: true,
      disabled: true
    },
    zone_indicative_realisee: {
      label: "Zone indicative réalisée",
      storeName: "chasseZoneIndicative",
      type: "list_form",
      list_type: "autocomplete",
      returnObject: true,
      // params: ({baseModel}) => ({
      //   "id_zone_cynegetique": baseModel.id_zone_cynegetique_affectee
      // }),
      dataReloadOnSearch: true,
      required: true
    },
    lieu_tir_synonyme: {
      label: "Lieu de tir (Syn)",
      storeName: "chasseLieuTirSynonyme",
      displayFieldName: "lieu_tir_synonyme_display",
      list_type: "autocomplete",
      type: "list_form",
      // params: ({ baseModel }) => ({
      //   "lieu_tir.id_zone_indicative": baseModel.id_zone_indicative_affectee
      // }),
      returnObject: true,
      dataReloadOnSearch: true,
      required: true
    },


    date_exacte_fast: {
      label: "Date du tir",
      type: "text",
      change: ({ baseModel, $store }) => {
        const d = formFunctions.getDateFromMMJJ(
          baseModel.date_exacte_fast,
          baseModel.saison.date_debut,
          baseModel.saison.date_fin
        );
        if (!d.err) {
          baseModel.date_enreg = baseModel.date_enreg || d;
          baseModel.date_exacte = d;
          $store.dispatch('focus','#form-date_enreg')
        }
      },
      required: ({ baseModel }) => !baseModel.date_exacte,
      condition: ({ baseModel }) => !baseModel.date_exacte,
      rules: ({ baseModel }) =>
        baseModel.saison && [
          v =>
            (v && v.length == 4) ||
            'la date doit être au format "JJMM" (4 caractères)',
          v => {
            const d = formFunctions.getDateFromMMJJ(
              v,
              baseModel.saison.date_debut,
              baseModel.saison.date_fin
            );
            if (d.err) {
              return d.err;
            }
            return true;
          }
        ]
    },

    date_enreg_fast: {
      label: "Date du constat",
      type: "text",
      change: ({ baseModel }) => {
        const d = formFunctions.getDateFromMMJJ(
          baseModel.date_enreg_fast,
          baseModel.saison.date_debut,
          baseModel.saison.date_fin
        );
        if (!d.err) {
          baseModel.date_enreg = d;
        }
      },
      condition: ({ baseModel }) => !baseModel.date_enreg,
      rules: ({ baseModel }) =>
        baseModel.saison && [
          v =>
            (v && v.length == 4) ||
            'la date doit être au format "JJMM" (4 caractères)',
          v => {
            const dateMin = `${baseModel.saison.date_debut.substring(
              0,
              4
            )}-01-01`;
            const dateMax = `${baseModel.saison.date_fin.substring(
              0,
              4
            )}-12-31`;
            const d = formFunctions.getDateFromMMJJ(v, dateMin, dateMax);
            if (d.err) {
              return d.err;
            }
            return true;
          }
        ]
    },

    date_exacte: {
      label: "Date du tir",
      type: "date",
      required: true,
      condition: ({ baseModel }) => {return !baseModel || !!baseModel.date_exacte},

      // la date exacte doit être comprise entre la date de debut de saison et la date de fin de saison
      rules: ({ baseModel }) =>
        baseModel.saison
          ? [
              formFunctions.rules.dateMin(baseModel.saison.date_debut),
              formFunctions.rules.dateMax(baseModel.saison.date_fin)
            ]
          : null,

      // change: ({ baseModel }) => {
      //   // par défaut la date d'enregistrement (ou date de constat), est égale à la date de tir
      //   // cf. max (c'est le cas très souvent)
      //   if (baseModel.date_exacte && !baseModel.date_enreg) {
      //     baseModel.date_enreg = baseModel.date_exacte;
      //   }
      // }
    },
    date_enreg: {
      label: "Date du constat",
      type: "date",
      required: true,
      condition: ({ baseModel }) => !!baseModel.date_enreg
    },
    mortalite_hors_pc: {
      label: "Hors PNC",
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
      codes: ["3", "2", "1"],
      nomenclatureType: "SEXE",
      // required: true,
      // change: ({baseModel, $store}) => {
      //   if(baseModel.nomenclature_sexe && !baseModel.nomenclature_classe_age) {
      //     $store.dispatch('focus', '#form-nomenclature_classe_age');
      //   }
      // }
    },
    nomenclature_classe_age: {
      label: "Classe d'age",
      type: "nomenclature",
      returnObject: true,
      list_type: "select",
      storeName: "commonsNomenclature",
      codes: ["1", "2", "3", "5"],
      nomenclatureType: "STADE_VIE",
      required: true,
    },
    nomenclature_mode_chasse: {
      label: "Mode de chasse",
      type: "nomenclature",
      returnObject: true,
      list_type: "select",
      storeName: "commonsNomenclature",
      nomenclatureType: "OEASC_MOD_CHASSE",
      required: true,
      // change: ({baseModel, $store}) => {
      //   if(baseModel.nomenclature_mode_chasse && !baseModel.nomenclature_sexe) {
      //     $store.dispatch('focus', '#form-nomenclature_sexe');
      //   }
      // }
    },
    poid_entier: {
      label: "Poid entier (kg)",
      type: "number",
      min: 0
    },
    poid_vide: {
      label: "Poid vide  (kg)",
      type: "number",
      min: 0
    },
    poid_c_f_p: {
      label: "Poid CFP (kg)",
      type: "number",
      min: 0
    },
    long_mandibules_droite: {
      label: "Longueur mandibules droite (mm)",
      type: "number",
      min: 0
    },
    long_mandibules_gauche: {
      label: "Longueur mandibules gauche (mm)",
      type: "number",
      min: 0
    },
    long_dagues_droite: {
      label: "Longueur dagues droite (mm)",
      type: "number",
      min: 0
    },
    long_dagues_gauche: {
      label: "Longueur dagues gauche (mm)",
      type: "number",
      min: 0
    },
    cors_nb: {
      label: "Nombre de cors",
      type: "number",
      min: 0
    },
    cors_commentaires: {
      label: "Commentaires (cors)",
      type: "text_area"
    },
    gestation: {
      label: "gestation",
      type: "bool_switch",
      disabled: ({ baseModel }) =>
        baseModel.nomenclature_sexe &&
        baseModel.nomenclature_sexe.label_fr != "Femelle"
    },
    commentaire: {
      label: "Commentaires (général)",
      type: "text_area"
    }
  }
};
