import storeUtils from "@/store/utils";
import admin from "@/components/admin";
import configStoreSecteur from './config/store-secteur';
import configStoreEspece from "./config/store-espece";
import configStoreNomenclature from "./config/store-nomenclature";
import configStoreNomenclatureType from "./config/store-nomenclature-type";

const ROUTE = [
  {
    // admin
    name: "commons.admin",
    path: "/commons/admin",
    label: "Données commons",
    hideTitle: true,
    component: admin,
    props: {
      config: {
        title: "Commons",
        tabs: {
          nomenclature: {
            storeName: "commonsNomenclature"
          },
          nomenclatureType: {
            storeName: "commonsNomenclatureType"
          },
          secteur: {
            storeName: "commonsSecteur"
          },
          espece: {
            storeName: "commonsEspece"
          },
        }
      }
    },
    access: 5
  }
];

const STORE = {};

storeUtils.addStore(STORE, configStoreEspece);
storeUtils.addStore(STORE, configStoreSecteur);
storeUtils.addStore(STORE, configStoreNomenclature);
storeUtils.addStore(STORE, configStoreNomenclatureType);

export { ROUTE, STORE };
