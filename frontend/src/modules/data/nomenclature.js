import { apiRequest } from "@/core/js/data/api.js";
import { dataString } from "./functions";

const STORE = {
  state: {
    _nomenclatures: []
  },

  getters: {
    nomenclatures: state => state._nomenclatures,
    nomenclature: state => id_nomenclature =>
      state._nomenclatures.find(n => n.id_nomenclature === id_nomenclature),
    nomenclatureFromCdNomenclature: state => (type, cd_nomenclature) =>
      state._nomenclatures.find(
        n => n.type == type && n.cd_nomenclature === cd_nomenclature
      ),
    nomenclaturesOfType: state => type =>
      state._nomenclatures.filter(n => n.type === type),
    nomenclatureString: state => (ids, key = "label_fr") =>
      dataString(STORE, state, "nomenclature", ids, key)
  },

  mutations: {
    nomenclatures: (state, nomenclatures) => {
      state._nomenclatures = nomenclatures;
    }
  },

  actions: {
    nomenclatures: ({ commit, getters }) => {
      return new Promise((resolve, reject) => {

        const nomenclatures = getters.nomenclatures.length;
        if (nomenclatures) {
          resolve(nomenclatures);
          return;
        }
        apiRequest("GET", "api/oeasc/nomenclatures").then(
          apiData => {
            const data = [];
            for (const nomenclatureType of Object.values(apiData).filter(
              n => !!n
            )) {
              for (const nomenclature of nomenclatureType.values) {
                nomenclature.type = nomenclatureType.mnemonique;
                data.push(nomenclature);
              }
            }
            commit("nomenclatures", data);
            resolve(data);
          },
          error => {
            reject(error);
          }
        );
      });
    }
  }
};

export { STORE };
