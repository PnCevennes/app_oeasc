import storeUtils from "@/store/utils";
// import { apiRequest } from "@/core/js/data/api.js";

// import inTest from "./in-test";
// import inTable from "./in-table";
import admin from "@/components/admin";
import configRealisationTable from "./config/table-realisation";
import configCircuitTable from "./config/table-circuit";
import configObserverTable from "./config/table-observer";
import configSecteurTable from "./config/table-secteur";
import configEspeceTable from "./config/table-espece";
import configTagTable from "./config/table-tag";

// route definitions

const configAdmin = {
  title: "Indice Nocturnes",
  tabs: {
    graphiques: {
      label: "Statistiques",
      type: "in-table"
    },
    realisation: {
      config: configRealisationTable,
      label: "Réalisation",
      type: "generic-table"
    },
    circuit: {
      config: configCircuitTable,
      label: "Circuits",
      type: "generic-table"
    },
    observer: {
      config: configObserverTable,
      label: "Observateurs",
      type: "generic-table"
    },
    secteur: {
      config: configSecteurTable,
      label: "Secteurs",
      type: "generic-table"
    },
    tag: {
      config: configTagTable,
      label: "Tags",
      type: "generic-table"
    },
    espece: {
      config: configEspeceTable,
      label: "Especes",
      type: "generic-table"
    }
  }
};

const ROUTE = [
  {
    // index
    name: "in.index",
    path: "/in/index",
    label: "Indices nocturnes",
    type: "page",
    content: "in.index",
    parent: "page.accueil",
    access: 5
  },
  {
    // admin
    name: "in.admin",
    path: "/in/admin",
    label: "Indices nocturnes ",
    parent: "in.index",
    hideTitle: true,
    component: admin,
    props: {
      config: configAdmin
    },
    access: 5
  },
  {
    // page resultats grand public
    path: "/resultats/in",
    name: "resultats.in",
    label: "Indices nocturnes",
    content: "resultats.in",
    parent: "resultats.index",
    type: "page"
  },
  {
    // page resultats grand public (tous graphes)
    path: "/resultats/in_all",
    name: "resultats.in",
    label: "Indices nocturnes",
    content: "resultats.in_all",
    parent: "resultats.index",
    type: "page"
  }
];

const STORE = {}

storeUtils.addSimpleStore(STORE, "inResults", "api/in/results/");

storeUtils.addStore(STORE, "inRealisation", "api/generic/in/realisation", {
  idFieldName: "id_realisation"
});

storeUtils.addStore(STORE, "inCircuit", "api/generic/in/circuit", {
  idFieldName: "id_circuit",
  displayFieldName: "nom_circuit"
});

storeUtils.addStore(STORE, "inSecteur", "api/generic/in/secteur", {
  idFieldName: "id_secteur",
  displayFieldName: "nom_secteur"
});

storeUtils.addStore(STORE, "inObserver", "api/generic/in/observer", {
  idFieldName: "id_observer",
  displayFieldName: "nom_observer"
});

storeUtils.addStore(STORE, "inTag", "api/generic/in/tag", {
  idFieldName: "id_tag",
  displayFieldName: "nom_tag"
});

storeUtils.addStore(STORE, "inEspece", "api/generic/in/espece", {
  idFieldName: "id_espece",
  displayFieldName: "nom_espece"
});

export { ROUTE, STORE };
