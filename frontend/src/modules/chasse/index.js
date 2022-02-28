import storeUtils from "@/store/utils";
import admin from "@/components/admin";
import configStorePersonne from "./config/store-personne";
import configStoreZoneCynegetique from "./config/store-zone-cynegetique";
import configStoreZoneIndicative from "./config/store-zone-indicative";
import configStoreLieuTir from "./config/store-lieu-tir";
import configStoreLieuTirSynonyme from "./config/store-lieu-tir-synonyme";
import configStoreSaison from "./config/store-saison";
import configStoreSaisonDate from "./config/store-saison-date";
import configStoreAttributionMassif from "./config/store-attribution-massif";
import configStoreTypeBracelet from "./config/store-type-bracelet";
import configStoreAttribution from "./config/store-attribution";
import configStoreRealisation from "./config/store-realisation";
import configFormContentChasse from './config/form-content-chasse'
import genericForm from "@/components/form/generic-form";
import graphChasse from "./graph-chasse";
import graphCustom from "./graph-custom";
import formRealisationChasse from "./form-realisation-chasse";
import exportsChasse from "./exports-chasse";
import { apiRequest } from "@/core/js/data/api.js";
import { round } from "@/core/js/util/util"
const ROUTE = [
  {
    // admin
    name: "chasse.admin",
    path: "/chasse/admin",
    label: "Données chasse",
    hideTitle: true,
    component: admin,
    props: {
      config: {
        title: "Données chasse",
        tabs: {
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
  {
    name: "chasse.testForm",
    path: "/chasse/testForm",
    label: "Données chasse",
    hideTitle: true,
    component: genericForm,
    props: {
      config: {
        storeName: "chasseRealisation",
        value: {
          id_realisation: 89
        },
        debug: [
          "id_attribution",
          "id_lieu_tir_synonyme",
          "attribution.id_attribution",
          "id_zone_indicative_realisee"
        ]
      }
    },
    access: 4
  },
  {
    name: "chasse.saisie",
    path: "/chasse/saisie",
    label: "Saisie données chasse",
    hideTitle: true,
    component: formRealisationChasse,
    access: 4
  },
  {
    name: "chasse.bilan",
    path: "/chasse/bilan",
    label: "Bilan données chasse",
    hideTitle: true,
    type: "page",
    content: "bilanChasse",
    access: 4
  },
  {
    name: "chasse.exports",
    path: "/chasse/export",
    label: "Exports données chasse",
    hideTitle: true,
    component: exportsChasse,
    access: 4
  },
  {
    name: "chasse.resultats_exemples",
    path: "/chasse/resultats_exemples",
    label: "Resultats (exemples)",
    hideTitle: true,
    type: 'page',
    content: 'chasseResultatsExemples',
    access: 4
  }

];

const chasseAction = (actionType) => ({ getter }, { id_espece, ids_zone_cynegetique, ids_zone_indicative, ids_secteur }) => {
  getter;
  return apiRequest(
    "GET",
    `api/chasse/results/${actionType}`,
    {
      params: {
        id_espece,
        ids_secteur,
        ids_zone_cynegetique,
        ids_zone_indicative
    }}
  );

}

const STORE = {
  getters: {
    configFormContentChasse: () => configFormContentChasse
  },
  actions: {
    chasseLastTauxRealisation: ({getter}, params) => {
      return new Promise((resolve) => chasseAction('bilan')({getter}, params).then((bilan) => {
        const last = bilan['taux_realisation'][bilan['taux_realisation'].length-1];
        resolve({
          saison: last[0],
          taux_realisation: round(last[1] * 100, 1)
        });
      }))
    },
    chasseBilan: chasseAction('bilan'),
    chasseIce: chasseAction('ice'),
    chasseCustom: ({ getter }, params) => {
      getter;
      return apiRequest("GET", `api/chasse/results/custom/`, { params });
    }
  }
};

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
