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
import genericForm from "@/components/form/generic-form";
import graphChasse from "./graph-chasse";
import graphCustom from "./graph-custom";
import formRealisationChasse from "./form-realisation-chasse";
import exportsChasse from "./exports-chasse";
import { apiRequest } from "@/core/js/data/api.js";

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

];

const STORE = {
  actions: {
    // exportChasse: ( {getter}, { dataType, exportType, filters }) => {
    //   getter;
    //   return apiRequest(
    //     'GET',
    //     `api/chasse/export/${exportType}`,
    //     {
    //       params: {
    //         data_type: dataType,
    //         filters
    //       }
    //     }
    //   )
    // },
    chasseBilan: ({ getter }, { id_espece, ids_zone_cynegetique, ids_zone_indicative }) => {
      getter;
      console.log('chasseBilan', id_espece, ids_zone_cynegetique, ids_zone_indicative)
      return apiRequest(
        "GET",
        `api/chasse/results/bilan`,
        { params: {
          id_espece,
          ids_zone_cynegetique,
          ids_zone_indicative
        }}
      );
    },
    chasseIce: ({ getter }, { id_espece, id_zone_cynegetique }) => {
      getter;
      return apiRequest(
        "GET",
        `api/chasse/results/ice/${id_espece}/${id_zone_cynegetique}`
      );
    },
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
