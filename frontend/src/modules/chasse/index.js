// les formulaires sont importés ici. Puis ajoutés à la fin de ce fichier dans storeUtils.addStore

import storeUtils from "@/store/utils.js"; // pour importer addStore qui construit les states, mutations, actions et getters
import { apiRequest } from "@/core/js/data/api.js"; // pour intégrer apiRequest dang des actions de store
import { round } from "@/core/js/util/util.js";


// Import des fichiers de configuration des stores
import admin from "./admin.vue"; // la page d'administration avec le tableau de données
import genericForm from "./form/generic-form.vue";
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
import donneesChasse from "./donnees-chasse.vue";
import graphChasse from "./graph-chasse.vue";
import graphCustom from "./graph-custom.vue";
import formRealisationChasse from "./form-realisation-chasse.vue";
import exportsChasse from "./exports-chasse.vue";
import pageChasseBilanDetaille from "./page-chasse-bilan-detaille.vue";



const ROUTE = [
  {
    // admin
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
    // Listing des données de chasse avec possibilité de les modifier, supprimer, ajouter
    // C'est la version standard de la page admin pour ne plus passer par le formulaire dynamique
    name: "chasse.donneesChasse",
    path: "/chasse/donneesChasse",
    label: "Données chasse",
    hideTitle: true,// True => cache le bandeau header pour plus de place
    component: donneesChasse,
    props: {
      config: {
        title: "Données chasse",
        tabs: { // les différents onglets du formulaire


          realisation: {
            storeName: "chasseRealisation"
          },
          attribution: {
            storeName: "chasseAttribution"
          },
          typeBracelet: {
            storeName: "chasseTypeBracelet"
          },
          affectationMassif: {
            storeName: "chasseAttributionMassif"
          },
          saisonDate: {
            storeName: "chasseSaisonDate"
          },
          saison: {
            storeName: "chasseSaison"
          },
          lieuTir: {
            storeName: "chasseLieuTir"
          },
          lieuTirSynonyme: {
            storeName: "chasseLieuTirSynonyme"
          },
          zoneIndicative: {
            storeName: "chasseZoneIndicative"
          },
          zoneCynegetique: {
            storeName: "chasseZoneCynegetique"
          },
          personne: {
            storeName: "chassePersonne"
          }
        }
      }
    },
    access: 5
  },


  // Route de test
  // {
  //   name: "chasse.testForm",
  //   path: "/chasse/testForm",
  //   label: "Données chasse",
  //   hideTitle: true,// True => cache le bandeau header pour plus de place
  //   component: genericForm,
  //   props: {
  //     config: {
  //       storeName: "chasseRealisation",
  //       value: {
  //         id_realisation: 89
  //       },
  //       debug: [
  //         "id_attribution",
  //         "id_lieu_tir_synonyme",
  //         "attribution.id_attribution",
  //         "id_zone_indicative_realisee"
  //       ]
  //     }
  //   },
  //   access: 4
  // },



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
  { //TODO rename component
    name: "chasse.restitution_bilan_detaille",
    path: "/chasse/restitution_bilan_detaille",
    label: "Chasse : analyse détaillée",
    hideTitle: true,// True => cache le bandeau header pour plus de place
    component: pageChasseBilanDetaille,
  },




  // les type: page => il faut défénir content qui correspond à l'id du contenu dans la base de données dans la table content
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
    // Usage configFormContentChasse(['id_saison', 'id_espece', 'id_secteur', 'id_zone_cynegetique', 'id_zone_indicative'])
    // eslint-disable-next-line no-unused-vars
    configFormContentChasse: (state) => (fields) => generateConfigformDef(fields)
  },
  actions: {
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
    getAnalyseBilanInfos: ($store, params) => {
      return apiRequest("GET", 'api/chasse/results/infos',  { params })
    },
    chasseLastTauxRealisation: ({getter}, params) => {
      return new Promise((resolve) => chasseAction('bilan')({getter}, params).then((bilan) => {
        const last = bilan['taux_realisation'][bilan['taux_realisation'].length-1];
        resolve(round(last[1] * 100, 1));
      }))
    },
    chasseAttributionBracelet: chasseAction('attribution_bracelet'),
    chasseBilan: chasseAction('bilan'),
    chasseIce: chasseAction('ice'),
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
