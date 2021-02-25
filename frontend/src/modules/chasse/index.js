import storeUtils from "@/store/utils";
import admin from "@/components/admin";
import configStorePersonne from "./config/store-personne";
import configStoreZoneCynegetique from "./config/store-zone-cynegetique";
import configStoreZoneInteret from "./config/store-zone-interet";
import configStoreLieuTir from "./config/store-lieu-tir";
import configStoreSaison from "./config/store-saison";
import configStoreSaisonDate from "./config/store-saison-date";
import configStoreAttributionMassif from "./config/store-attribution-massif";
import configStoreTypeBracelet from "./config/store-type-bracelet";
import configStoreAttribution from "./config/store-attribution";
import configStoreRealisation from "./config/store-realisation";


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
        title: "Indice Nocturnes",
        tabs: {          
          // realisation: {
          //   storeName: 'chasseRealisation'
          // },
          // attribution: {
          //   storeName: 'chasseAttribution'
          // },
          // typeBracelet: {
          //   storeName: 'chasseTypeBracelet'
          // },
          // affectationMassif: {
          //   storeName: 'chasseAttributionMassif'
          // },
          // saisonDate: {
          //   storeName: "chasseSaisonDate"
          // },
          // saison: {
          //   storeName: "chasseSaison"
          // },
          // lieuTir: {
          //   storeName: "chasseLieuTir"
          // },
          // zoneInteret: {
          //   storeName: "chasseZoneInteret"
          // },
          // zoneCynegetique: {
          //   storeName: "chasseZoneCynegetique"
          // },
          personne: {
            storeName: "chassePersonne"
          },
        }
      }
    },
    access: 5
  }
];

const STORE = {};

storeUtils.addStore(STORE, configStorePersonne);
storeUtils.addStore(STORE, configStoreZoneCynegetique);
storeUtils.addStore(STORE, configStoreZoneInteret);
storeUtils.addStore(STORE, configStoreLieuTir);
storeUtils.addStore(STORE, configStoreSaison);
storeUtils.addStore(STORE, configStoreSaisonDate);
storeUtils.addStore(STORE, configStoreAttributionMassif);
storeUtils.addStore(STORE, configStoreTypeBracelet);
storeUtils.addStore(STORE, configStoreAttribution);
storeUtils.addStore(STORE, configStoreRealisation);


export { ROUTE, STORE };
