const dataString = function(STORE, state, getterKey, n, dataKey) {
  if (!n || (Array.isArray(n) && !n.length)) {
    return "";
  }

  let nArray = Array.isArray(n) ? n : [n];
  return nArray
    .map(id => {
      const data = STORE.getters[getterKey](state)(id);
      return ((data && data[dataKey]) || "").toLowerCase();
    })
    .join(", ");
};

export { dataString };
