import storeUtils from "@/store/utils";
import admin from "@/components/admin";
import configStorePersonne from "./config/store-personne";
import configStoreZoneCynegetique from "./config/store-zone-cynegetique";
import configStoreZoneIndicative from "./config/store-zone-indicative";
import configStoreLieuTir from "./config/store-lieu-tir";
import configStoreSaison from "./config/store-saison";
import configStoreSaisonDate from "./config/store-saison-date";
import configStoreAttributionMassif from "./config/store-attribution-massif";
import configStoreTypeBracelet from "./config/store-type-bracelet";
import configStoreAttribution from "./config/store-attribution";
import configStoreRealisation from "./config/store-realisation";
import genericForm from "@/components/form/generic-form";

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
            storeName: 'chasseRealisation'
          },
          attribution: {
            storeName: 'chasseAttribution'
          },
          typeBracelet: {
            storeName: 'chasseTypeBracelet'
          },
          affectationMassif: {
            storeName: 'chasseAttributionMassif'
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
          zoneIndicative: {
            storeName: "chasseZoneIndicative"
          },
          zoneCynegetique: {
            storeName: "chasseZoneCynegetique"
          },
          personne: {
            storeName: "chassePersonne"
          },
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
        storeName: 'chasseRealisation',
        value: {
            // id_realisation: 89
        }
      },
    }
  }
];

const STORE = {};

storeUtils.addStore(STORE, configStorePersonne);
storeUtils.addStore(STORE, configStoreZoneCynegetique);
storeUtils.addStore(STORE, configStoreZoneIndicative);
storeUtils.addStore(STORE, configStoreLieuTir);
storeUtils.addStore(STORE, configStoreSaison);
storeUtils.addStore(STORE, configStoreSaisonDate);
storeUtils.addStore(STORE, configStoreAttributionMassif);
storeUtils.addStore(STORE, configStoreTypeBracelet);
storeUtils.addStore(STORE, configStoreAttribution);
storeUtils.addStore(STORE, configStoreRealisation);


export { ROUTE, STORE };
