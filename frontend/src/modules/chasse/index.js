// les formulaires sont importés ici. Puis ajoutés à la fin de ce fichier dans storeUtils.addStore

import storeUtils from "@/store/utils.js"; // pour importer addStore qui construit les states, mutations, actions et getters
import { apiRequest } from "@/core/js/data/api.js"; // pour intégrer apiRequest dang des actions de store
import { round } from "@/core/js/util/util.js";


// Import des fichiers de configuration des stores
// import admin from "./admin.vue"; // la page d'administration avec le tableau de données
import admin from "@/components/admin";
// import genericForm from "./form/generic-form.vue";
import { generateConfigformDef } from './config/form-content-chasse.js';
import configStorePersonne from "./config/store-personne.js";
import configStoreZoneCynegetique from "./config/store-zone-cynegetique.js";
import configStoreZoneIndicative from "./config/store-zone-indicative.js";
import configStoreLieuTir from "./config/store-lieu-tir.js";
import configStoreLieuTirSynonyme from "./config/store-lieu-tir-synonyme.js";
import configStoreSaison from "./config/store-saison.js";
import configStoreSaisonDate from "./config/store-saison-date.js";
import configStoreAttributionMassif from "./config/store-attribution-massif.js";
import configStoreTypeBracelet from "./config/store-type-bracelet.js";
import configStoreAttribution from "./config/store-attribution.js";
import configStoreRealisation from "./config/store-realisation.js";



// Import des routes 
// import donneesChasse from "./donnees-chasse.vue";
import graphChasse from "./graph-chasse.vue";
import graphCustom from "./graph-custom.vue";
import formRealisationChasse from "./form-realisation-chasse.vue";
import exportsChasse from "./exports-chasse.vue";
import pageChasseBilanDetaille from "./page-chasse-bilan-detaille.vue";



const ROUTE = [
  {
    // Route vers les tableaux des données de chasse
    name: "chasse.admin",
    path: "/chasse/admin",
    label: "Données chasse",
    hideTitle: true, // True => cache le bandeau header pour plus de place
    component: admin, // le component admin est le composant générique qui affiche une table avec generic-table.vue (il faut la props.config.tabs)
    props: {
      config: { 
        // titre affiché en haut de page suivi de "- Page d'administration"
        title: "Données chasse",
        // tabs nécéssaire pour le composant admin
        // liste des onglets avec les stores associés corresondants aux fichiers dans le dossier config
        // le nom du tab peut être différent du nom du store, Ça ne change rien
        tabs: {
          realisation_tab: {
            storeName: "chasseRealisation"
          },
          attribution_tab: {
            storeName: "chasseAttribution"
          },
          typeBracelet_tab: {
            storeName: "chasseTypeBracelet"
          },
          affectationMassif_tab: {
            storeName: "chasseAttributionMassif"
          },
          saisonDate_tab: {
            storeName: "chasseSaisonDate"
          },
          saison_tab: {
            storeName: "chasseSaison"
          },
          lieuTir_tab: {
            storeName: "chasseLieuTir"
          },
          lieuTirSynonyme_tab: {
            storeName: "chasseLieuTirSynonyme"
          },
          zoneIndicative_tab: {
            storeName: "chasseZoneIndicative"
          },
          zoneCynegetique_tab: {
            storeName: "chasseZoneCynegetique"
          },
          personne_tab: {
            storeName: "chassePersonne"
          }
        }
      }
    },
    access: 5 // droit d'accès minimum
  },

  {
    name: "chasse.saisie",
    path: "/chasse/saisie",
    label: "Saisie données chasse",
    hideTitle: true,// True => cache le bandeau header pour plus de place
    component: formRealisationChasse,
    access: 4
  },

  {
    name: "chasse.exports",
    path: "/chasse/export",
    label: "Exports données chasse", // titre dans le menu (mais pas dans la page)
    hideTitle: true,// True => cache le bandeau header pour plus de place
    component: exportsChasse,
    access: 4
  },
  { 
    name: "chasse.restitution_bilan_detaille",
    path: "/chasse/restitution_bilan_detaille",
    label: "Chasse : analyse détaillée",
    hideTitle: true,// True => cache le bandeau header pour plus de place
    component: pageChasseBilanDetaille,
  },


  {
    name: "chasse.restitution_gd_public",
    path: "/chasse/restitution_gd_public",
    label: "Plans de chasse", // titre dans le menu (mais pas dans la page)
    type: "page", 
    content: "chasse_restitution_gd_public",
    parent: "resultats.index", // définit la place dans le menu. Ici dans "resultats des suivis"
  },
  {
    name: "chasse.restitution_indices_performances",
    path: "/chasse/restitution_indices_performances",
    label: "Indices de performance", // titre dans le menu (mais pas dans la page)
    type: "page",
    content: "chasse_restitution_indices_performances",
    parent: "resultats.index", // définit la place dans le menu. Ici dans "resultats des suivis"
  },
  {
    name: "chasse.bilan",
    path: "/chasse/bilan",
    label: "Bilan données chasse", // titre dans le menu (mais pas dans la page)
    hideTitle: true,// True => cache le bandeau header pour plus de place
    type: "page",
    content: "bilanChasse",
    access: 4
  },


];

/**
 * Génère une fonction d'action pour effectuer une requête API liée à la chasse.
 *
 * @param {string} actionType - Le type d'action à effectuer (ex: 'list', 'details', etc.).
 * @returns {Function} Une fonction prenant deux objets en paramètres :
 *   - {Object} context - Contexte Vuex, contenant notamment le getter (non utilisé ici).
 *   - {Object} params - Paramètres pour la requête API :
 *     @param {number|string} params.id_saison - Identifiant de la saison de chasse.
 *     @param {number|string} params.id_espece - Identifiant de l'espèce chassée.
 *     @param {number|string} params.id_zone_cynegetique - Identifiant de la zone cynégétique.
 *     @param {number|string} params.id_zone_indicative - Identifiant de la zone indicative.
 *     @param {number|string} params.id_secteur - Identifiant du secteur de chasse.
 *     @param {number|string} params.poids_ou_dagues - Poids ou nombre de dagues (selon le contexte).
 * @returns {Promise} Résultat de la requête API, contenant les résultats de chasse selon les paramètres fournis.
 *
 * @example
 * // Utilisation dans un module Vuex pour récupérer les résultats de chasse d'une saison et d'une espèce donnée :
 * dispatch('chasseAction', { id_saison: 2023, id_espece: 5, ... })
 *
 * @remarks
 * Cette fonction est utilisée dans le contexte d'un module Vuex pour centraliser les appels API relatifs aux résultats de chasse.
 * Elle permet de factoriser la logique d'appel en fonction du type d'action souhaité (ex: récupération de liste, détails, etc.).
 */
const chasseAction = (actionType) => ({ getter }, { id_saison, id_espece, id_zone_cynegetique, id_zone_indicative, id_secteur, poids_ou_dagues }) => {
  getter;
  
  return apiRequest(
    "GET",
    `api/chasse/results/${actionType}`,
    {
      params: {
        id_saison,
        id_espece,
        id_secteur,
        id_zone_cynegetique,
        id_zone_indicative,
        poids_ou_dagues
    }}
  );

}

const STORE = {
  getters: {
    /**
     * Génère la configuration d'un formulaire de chasse à partir d'une liste de champs.
     * @param {Array<string>} fields - Liste des noms de champs à inclure dans le formulaire.
     * @returns {Object} Configuration du formulaire générée.
     * @example
     * // Utilisé pour générer dynamiquement le contenu d'un formulaire de chasse
     * configFormContentChasse(['id_saison', 'id_espece', 'id_secteur', 'id_zone_cynegetique', 'id_zone_indicative'])
     */
    // eslint-disable-next-line no-unused-vars
    configFormContentChasse: (state) => (fields) => generateConfigformDef(fields)
  },
  actions: {
    /**
     * Récupère la dernière saison de chasse active.
     * @param {Object} $store - Contexte du store Vuex.
     * @param {Object} [options={returnObject: true}] - Options pour le retour (objet complet ou seulement l'id).
     * @returns {Promise<Object|number|null>} La dernière saison (objet ou id), ou null si aucune trouvée.
     * @example
     * // Utilisé pour pré-remplir des formulaires ou afficher la saison courante
     * dispatch('lastSaison')
     */
    lastSaison: ($store, options = {returnObject: true}) => {
      return new Promise(resolve => {
        const configStore = $store.getters.configStore("chasseSaison");
        $store
          .dispatch(configStore.getAll, {
            current: true
          })
          .then(saisons => {
            if (saisons && saisons[0]) {
              resolve(options.returnObject ? saisons[0] : saisons[0].id_saison);
            } else {
              resolve(null);
            }
          });
      })
    },

    /**
     * Détermine l'échelle géographique de la chasse selon les paramètres fournis.
     * @param {Object} $store - Contexte du store Vuex.
     * @param {Object} params - Paramètres contenant potentiellement des identifiants de zones.
     * @returns {Promise<string>} Libellé de l'échelle (ex: "Secteur : ...", "Zone cynegetique : ...", ou "Cœur").
     * @example
     * // Utilisé pour afficher le niveau géographique sélectionné dans un bilan ou une synthèse
     * dispatch('chasseEchelle', { id_secteur: 1 })
     */
    chasseEchelle: ($store, params) => {
      const testVar = (v) => Array.isArray(v) ? v.length : v;
      return new Promise((resolve) => {
        for (const idFieldName of ['id_zone_indicative', 'id_zone_cynegetique', 'id_secteur']) {
          if(!testVar(params[idFieldName])) {
            continue
          }
          const configStore = $store.getters.findConfigStore({idFieldName});
          $store.dispatch(configStore.getAll, params )
            .then( val => {
                resolve(`${configStore.labels} : ${val.map(v => v[configStore.displayFieldName]).join(', ')}`)
            });
          return;
        }
        resolve(`Cœur`);
      });
    },

    /**
     * Récupère des informations d'analyse pour le bilan de chasse.
     * @param {Object} $store - Contexte du store Vuex.
     * @param {Object} params - Paramètres pour la requête API.
     * @returns {Promise<Object>} Résultat de l'appel API.
     * @example
     * // Utilisé pour afficher des informations complémentaires dans les bilans
     * dispatch('getAnalyseBilanInfos', { id_saison: 2023 })
     */
    getAnalyseBilanInfos: ($store, params) => {
      return apiRequest("GET", 'api/chasse/results/infos',  { params })
    },

    /**
     * Récupère le dernier taux de réalisation de chasse (en pourcentage, arrondi à 1 décimale).
     * @param {Object} context - Contexte du store Vuex (doit contenir 'getter').
     * @param {Object} params - Paramètres pour la récupération du bilan.
     * @returns {Promise<number>} Dernier taux de réalisation en pourcentage.
     * @example
     * // Utilisé pour afficher un indicateur de performance dans un tableau de bord
     * dispatch('chasseLastTauxRealisation', { id_saison: 2023 })
     */
    chasseLastTauxRealisation: ({getter}, params) => {
      return new Promise((resolve) => chasseAction('bilan')({getter}, params).then((bilan) => {
        const last = bilan['taux_realisation'][bilan['taux_realisation'].length-1];
        resolve(round(last[1] * 100, 1));
      }))
    },

    /**
     * Action générique pour l'attribution de bracelets de chasse.
     * @param {Object} context - Contexte du store Vuex.
     * @param {Object} params - Paramètres pour l'attribution.
     * @returns {Promise<Object>} Résultat de l'attribution.
     * @example
     * // Utilisé lors de la gestion des bracelets pour les chasseurs
     * dispatch('chasseAttributionBracelet', { id_chasseur: 42 })
     */
    chasseAttributionBracelet: chasseAction('attribution_bracelet'),

    /**
     * Action générique pour récupérer le bilan de chasse.
     * @param {Object} context - Contexte du store Vuex.
     * @param {Object} params - Paramètres pour le bilan.
     * @returns {Promise<Object>} Résultat du bilan.
     * @example
     * // Utilisé pour afficher le bilan global ou détaillé d'une saison
     * dispatch('chasseBilan', { id_saison: 2023 })
     */
    chasseBilan: chasseAction('bilan'),

    /**
     * Action générique pour récupérer les données ICE (Indicateur de Chasse Efficace).
     * @param {Object} context - Contexte du store Vuex.
     * @param {Object} params - Paramètres pour la récupération.
     * @returns {Promise<Object>} Résultat ICE.
     * @example
     * // Utilisé pour des analyses avancées sur l'efficacité de la chasse
     * dispatch('chasseIce', { id_saison: 2023 })
     */
    chasseIce: chasseAction('ice'),

    /**
     * Récupère des résultats personnalisés de chasse via une requête API.
     * @param {Object} context - Contexte du store Vuex (doit contenir 'getter').
     * @param {Object} params - Paramètres pour la requête personnalisée.
     * @returns {Promise<Object>} Résultat de la requête personnalisée.
     * @example
     * // Utilisé pour des rapports ou exports personnalisés
     * dispatch('chasseCustom', { filtre: 'spécifique' })
     */
    chasseCustom: ({ getter }, params) => {
      getter;
      return apiRequest("GET", `api/chasse/results/custom/`, { params });
    }
  }
};



// Ajout des configStore en fonction des fichiers dans config
storeUtils.addStore(STORE, configStorePersonne);
storeUtils.addStore(STORE, configStoreZoneCynegetique);
storeUtils.addStore(STORE, configStoreZoneIndicative);
storeUtils.addStore(STORE, configStoreLieuTir);
storeUtils.addStore(STORE, configStoreLieuTirSynonyme);
storeUtils.addStore(STORE, configStoreSaison);
storeUtils.addStore(STORE, configStoreSaisonDate);
storeUtils.addStore(STORE, configStoreAttributionMassif);
storeUtils.addStore(STORE, configStoreTypeBracelet);
storeUtils.addStore(STORE, configStoreAttribution);
storeUtils.addStore(STORE, configStoreRealisation);

const CONTENT = {
  graphChasse,
  graphCustom
};

export { ROUTE, STORE, CONTENT };
