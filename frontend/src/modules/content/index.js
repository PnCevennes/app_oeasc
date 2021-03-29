import storeUtils from "@/store/utils";
import content from "./content";
import actualite from "./actualite";
// import { apiRequest } from "@/core/js/data/api.js";
import admin from "@/components/admin";

import configStoreTag from './config/store-tag';
import configStoreContent from "./config/store-content";


const ROUTE = [
  {
    // admin
    name: "content.admin",
    path: "/content/admin",
    label: "Contenus",
    hideTitle: true,
    component: admin,
    props: {
      config: {
        title: "Contenus",
        tabs: {
          content: {
            storeName: 'commonsContent',
          },
          tag: {
            storeName: 'commonsContent',
          },
        }      
      }
    },
    access: 5
  },

  {
    path: "/actualites",
    label: "Actualités",
    name: "actualite.index",
    parent: "page.accueil",
    component: actualite,
    props: {
      tagNames: ["actualité"]
    }
  },
  {
    path: "/actualite/:code",
    name: "actualite.content",
    parent: "actualite.index",
    type: "page"
  },
  {
    path: "/content/:code",
    label: "content",
    name: "content",
    component: content,
    props: {
      page: true,
    }
  },
  {
    path: "/actualite/",
    label: "actualite",
    name: "actualite.new",
    parent: "actualite.index",
    component: content,
    props: {
      page: true,
      code: null,
      tagNames:['actualité'] 
    }
  }
];

const STORE = {}

// const STORE = {
//   state: {
//     _contents: {}
//   },
//   getters: {
//     content: state => code => {
//       return state._contents[code];
//     }
//   },
//   mutations: {
//     content: (state, code, data) => {
//       state._contents[code] = data;
//     }
//   },
//   actions: {
//     content: ({ getters, commit }, code) => {
//       return new Promise((resolve, reject) => {
//         const content = getters.content(code);
//         if (content) {
//           resolve(content);
//         }
//         apiRequest("GET", `api/commons/content/${code}`).then(
//           data => {
//             commit("content", code, data);
//             resolve(data);
//           },
//           error => {
//             reject(error);
//           }
//         );
//       });
//     }
//   }
// };

storeUtils.addStore(STORE, configStoreContent)
storeUtils.addStore(STORE, configStoreTag)

// storeUtils.addStore(STORE, "commonsContent", "api/generic/commons/content", {
//   idFieldName: "id_content",
//   displayFieldName: "code"
// });
// storeUtils.addStore(STORE, "commonsTag", "api/generic/commons/tag", {
//   idFieldName: "id_tag",
//   displayFieldName: "nom_tag"
// });
export { ROUTE, STORE, content };
