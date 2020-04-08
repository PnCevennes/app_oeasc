import { apiRequest } from "@/core/js/data/api.js";

const STORE = {
  state: {
    _nomenclatures: []
  },

  getters: {
    nomenclature: state => id_nomenclature =>
      state._nomenclatures.find(n => n.id_nomenclature === id_nomenclature),
    nomenclatureFromCdNomenclature: state => (type, cd_nomenclature) =>
      state._nomenclatures.find(n => n.type == type && n.cd_nomenclature === cd_nomenclature),
    nomenclaturesOfType: state => type =>
      state._nomenclatures.filter(n => n.type === type)
  },

  mutations: {
    nomenclatures: (state, nomenclatures) => {
      state._nomenclatures = nomenclatures;
    }
  },

  actions: {
    nomenclatures: ({ commit }) => {
      return new Promise((resolve, reject) => {
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
