import { formFunctions } from "@/components/form/functions/form.js";

// Configuration du module "realisation" pour la gestion des réalisations de chasse.
// Ce module définit la structure des colonnes, des groupes de formulaires, des options de requête,
// ainsi que les définitions de champs (defs) utilisés dans les formulaires et les tables.


// Objet principal d'export : configuration du module "realisation"
export default {
  // Groupe fonctionnel du module (ici "chasse")
  group: "chasse",
  // Nom technique du module
  name: "realisation",
  // Libellé affiché pour le module
  label: "Réalisation",
  // Indique si la pagination/tri est côté serveur
  serverSide: true,
  // Genre grammatical utilisé pour le module
  genre: "F",

  // Liste des champs affichés dans le tableau principal
  columns: [
    "saison",
    "attribution",
    "date_exacte",
    "auteur_tir_str",
    "auteur_constat_str",
    "zone_cynegetique_realisee",
    "zone_indicative_realisee",
    "lieu_tir_synonyme",
    "nomenclature_sexe",
    "nomenclature_classe_age",
    "nomenclature_mode_chasse"
  ],

  // Définition des groupes et sous-groupes de champs pour le formulaire de saisie
  form: {
    groups: [
      // Groupe "Bracelet" : sélection de la saison et de l'attribution
      {
        title: "Bracelet",
        forms: ["saison", "attribution"],
        direction: "row"
      },
      // Groupe "Localisation" : affiché si une attribution est sélectionnée
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
                forms: ["lieu_tir_synonyme", "lieu_tir_txt"]
              }

            ]
          }
        ]
      },
      // Groupe "Informations" : affiché si une attribution est sélectionnée
      {
        title: "Informations",
        condition: ({ baseModel }) =>
          baseModel.attribution && baseModel.attribution.id_attribution,
        direction: "row",
        groups: [
          {
            title: "Auteurs",
            forms: ["auteur_tir_str", "auteur_constat_str"]
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
      // Groupe "Information animal" : affiché si une attribution est sélectionnée
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
      // Groupe "Description avancée (cerf)" : affiché pour les mâles adultes/sub-adultes
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
              // Groupe "Dagues" : longueurs des dagues
              {
                title: "Dagues",
                forms: ["long_dagues_gauche", "long_dagues_droite"],
                direction: "row"
              },
              // Groupe "Cors" : nombre de cors
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
      // Groupe "Commentaires" : affiché si une attribution est sélectionnée
      {
        condition: ({ baseModel }) =>
          baseModel.attribution && baseModel.attribution.id_attribution,
        title: "Commentaires",
        forms: ["commentaire"]
      }
    ]
  },

  // Paramètres par défaut pour les requêtes (pagination, tri, etc.)
  options: {
    page: 1,
    sortBy: ["saison", "date_exacte"],
    sortDesc: [true, true],
  },

  // Définitions détaillées de chaque champ utilisé dans le module
  defs: {
    // Champ technique caché (ID)
    id_realisation: {
      label: "ID",
      hidden: true
    },

    // Champ "Saison" : sélection de la saison de chasse
    saison: {
      label: "Saison",
      storeName: "chasseSaison",
      type: "list_form",
      list_type: "select",
      returnObject: true,
      required: true,
      // On ne change pas la saison pour un update
      disabled: ({ baseModel }) => !!baseModel.id_realisation,
      // Valeur par défaut : dernière saison connue
      default: ({ $store, config }) => $store._actions.lastSaison[0](config)
    },

    // Champ "Attribution" : sélection du bracelet/attribution
    attribution: {
      label: "Attribution",
      storeName: "chasseAttribution",
      type: "list_form",
      list_type: "autocomplete",
      dataReloadOnSearch: true,
      returnObject: true,
      displayFieldName: "numero_bracelet",
      // Filtre les attributions selon la saison et si une réalisation existe déjà
      params: ({ baseModel }) => {
        const params = {
          id_saison: baseModel.saison && baseModel.saison.id_saison
        };
        // Si on crée une nouvelle réalisation, on choisit parmi les attributions sans réalisation
        if (!baseModel.id_realisation) {
          params.has_realisation = false;
        }
        return params;
      },
      required: true,
      // Lors du changement d'attribution, met à jour les zones associées si non déjà renseignées
      change: ({ baseModel, $store }) => {
        if (!baseModel.attribution) {
          return;
        }
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



    auteur_tir_str: {
      label: "Auteur tir",
      type: "text",
      returnObject: true,
    },

    // Champ "Auteur constat" : personne ayant constaté
    auteur_constat_str: {
      label: "Auteur constat",
      type: "text",
      returnObject: true,
    },

    // Champ "Zone cynégétique affectée" : zone attribuée (lecture seule)
    zone_cynegetique_affectee: {
      label: "Zone cynégétique affectee",
      storeName: "chasseZoneCynegetique",
      type: "list_form",
      list_type: "select",
      returnObject: true,
      disabled: true
    },

    // Champ "Zone cynégétique réalisée" : zone réellement utilisée
    zone_cynegetique_realisee: {
      label: "Zone cynégétique réalisée",
      storeName: "chasseZoneCynegetique",
      type: "list_form",
      list_type: "select",
      returnObject: true,
      required: true
    },

    // Champ "Zone indicative affectée" : zone indicative attribuée (lecture seule)
    zone_indicative_affectee: {
      label: "Zone indicative affectée",
      storeName: "chasseZoneIndicative",
      type: "list_form",
      list_type: "autocomplete",
      returnObject: true,
      dataReloadOnSearch: true,
      disabled: true
    },

    // Champ "Zone indicative réalisée" : zone indicative réellement utilisée
    zone_indicative_realisee: {
      label: "Zone indicative réalisée",
      storeName: "chasseZoneIndicative",
      type: "list_form",
      list_type: "autocomplete",
      returnObject: true,
      dataReloadOnSearch: true,
      required: true
    },

    // Champ "Lieu de tir (Syn)" : lieu du tir (synonyme)
    lieu_tir_synonyme: {
      label: "Lieu de tir (Syn)",
      storeName: "chasseLieuTirSynonyme",
      displayFieldName: "lieu_tir_synonyme_display",
      list_type: "autocomplete",
      type: "list_form",
      returnObject: true,
      dataReloadOnSearch: true,
      required: false
    },

    lieu_tir_txt: {
      label: "Lieu de tir txt",
      type: "text",
      returnObject: true,
    },

    // Champ "Date du tir" (saisie rapide JJMM)
    date_exacte_fast: {
      label: "Date du tir",
      type: "text",
      // Lors du changement, convertit JJMM en date complète et met à jour les champs date
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
      // Règles de validation : format JJMM et cohérence avec la saison
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

    // Champ "Date du constat" (saisie rapide JJMM)
    date_enreg_fast: {
      label: "Date du constat",
      type: "text",
      // Lors du changement, convertit JJMM en date complète
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
      // Règles de validation : format JJMM et cohérence avec la saison
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

    // Champ "Date du tir" (date complète)
    date_exacte: {
      label: "Date du tir",
      type: "date",
      required: true,
      condition: ({ baseModel }) => {return !baseModel || !!baseModel.date_exacte},
      // La date exacte doit être comprise entre la date de début et de fin de saison
      rules: ({ baseModel }) =>
        baseModel.saison
          ? [
              formFunctions.rules.dateMin(baseModel.saison.date_debut),
              formFunctions.rules.dateMax(baseModel.saison.date_fin)
            ]
          : null,
    },

    // Champ "Date du constat" (date complète)
    date_enreg: {
      label: "Date du constat",
      type: "date",
      required: true,
      condition: ({ baseModel }) => !!baseModel.date_enreg
    },

    // Champ booléen "Hors PNC"
    mortalite_hors_pc: {
      label: "Hors PNC",
      type: "bool_switch"
    },

    // Champ booléen "Parcelle ONF"
    parcelle_onf: {
      label: "Parcelle ONF",
      type: "bool_switch"
    },

    // Champ "Sexe" : nomenclature sexe
    nomenclature_sexe: {
      label: "Sexe",
      type: "nomenclature",
      returnObject: true,
      list_type: "select",
      storeName: "commonsNomenclature",
      codes: ["3", "2", "1"],
      nomenclatureType: "SEXE",
    },

    // Champ "Classe d'âge" : nomenclature stade de vie
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

    // Champ "Mode de chasse" : nomenclature mode de chasse
    nomenclature_mode_chasse: {
      label: "Mode de chasse",
      type: "nomenclature",
      returnObject: true,
      list_type: "select",
      storeName: "commonsNomenclature",
      nomenclatureType: "OEASC_MOD_CHASSE",
      required: true,
    },

    // Champ "Poids entier" (kg)
    poid_entier: {
      label: "Poid entier (kg)",
      type: "number",
      min: 0
    },

    // Champ "Poids vide" (kg)
    poid_vide: {
      label: "Poid vide  (kg)",
      type: "number",
      min: 0
    },

    // Champ "Poids CFP" (kg)
    poid_c_f_p: {
      label: "Poid CFP (kg)",
      type: "number",
      min: 0
    },

    // Champ "Longueur mandibules droite" (mm)
    long_mandibules_droite: {
      label: "Longueur mandibules droite (mm)",
      type: "number",
      min: 0
    },

    // Champ "Longueur mandibules gauche" (mm)
    long_mandibules_gauche: {
      label: "Longueur mandibules gauche (mm)",
      type: "number",
      min: 0
    },

    // Champ "Longueur dagues droite" (mm)
    long_dagues_droite: {
      label: "Longueur dagues droite (mm)",
      type: "number",
      min: 0
    },

    // Champ "Longueur dagues gauche" (mm)
    long_dagues_gauche: {
      label: "Longueur dagues gauche (mm)",
      type: "number",
      min: 0
    },

    // Champ "Nombre de cors"
    cors_nb: {
      label: "Nombre de cors",
      type: "number",
      min: 0
    },

    // Champ "Commentaires (cors)"
    cors_commentaires: {
      label: "Commentaires (cors)",
      type: "text_area"
    },

    // Champ booléen "gestation" (désactivé si sexe non femelle)
    gestation: {
      label: "gestation",
      type: "bool_switch",
      disabled: ({ baseModel }) =>
        baseModel.nomenclature_sexe &&
        baseModel.nomenclature_sexe.label_fr != "Femelle"
    },

    // Champ "Commentaires (général)"
    commentaire: {
      label: "Commentaires (général)",
      type: "text_area"
    }
  }
};
