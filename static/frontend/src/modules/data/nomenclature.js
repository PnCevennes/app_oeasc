const nomenclatureActions = { 
  getNomenclaturesOfType: ({ dispatch }, { nomenclatureType }) => {
    return dispatch('cacheOrRequest', {
      url: `api/oeasc/nomenclatures/${nomenclatureType}`,
      cacheKeys: ['nomenclature', nomenclatureType],
      dataKeys: ['values']
    });
  },
  getAllNomenclatures: ({ dispatch }) => {
    return dispatch('cacheOrRequest', {
      url: `api/oeasc/nomenclatures`,
      cacheKeys: ['nomenclature']
    });
  }
};

export { nomenclatureActions };
