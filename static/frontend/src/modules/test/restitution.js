import * as chroma from "chroma-js";

const colors = chroma.brewer.Dark2;

const restitution = {
  color(d, dataList, options = {}) {
    const indexElemAutres = dataList.findIndex(e => e.text == "Autres");
    const value = this.getValue(d, options);
    let index;
    for (const v of value) {
      index = dataList.findIndex(e => e.text == v);
      console.log(index, indexElemAutres);
      return index != -1
        ? colors[index]
        : indexElemAutres != -1
        ? colors[indexElemAutres]
        : null;
    }
    return colors[index];
  },

  getValue(d, options) {
    let value = d;
    if (options.replace) {
      for (const rep of options.replace) {
        if (value == rep[0]) {
          value = rep[1];
        }
      }
    }

    value = !value
      ? []
      : Array.isArray(value)
      ? value
      : options.split
      ? value.split(options.split)
      : [value];

    return value;
  },

  dataList(data, name, options = {}) {
    let dataList = [];
    for (const d of data.filter(d1 => d1.selected != false)) {
      const value = this.getValue(d[name], options);
      for (const v of value) {
        let elem = dataList.find(d => d.text == v);
        if (!elem) {
          elem = { text: v, count: 0 };
          dataList.push(elem);
        }
        elem.count += 1;
      }
    }

    dataList = dataList.sort((a, b) => b.count - a.count);

    if (options.nMax) {
      dataList = this.cutDataList(dataList, options.nMax);
    }

    return dataList;
  },

  cutDataList(dataList, nMax) {
    const elemAutres = { text: "Autres", count: 0 };
    const out = [];
    for (let i = 0; i < dataList.length; i++) {
      if (i < nMax) {
        out.push(dataList[i]);
      } else {
        if (i == nMax) {
          out.push(elemAutres);
        }
        elemAutres.count += 1;
      }
    }
    return out;
  }
};

export { restitution };
