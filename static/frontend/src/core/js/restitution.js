import * as chroma from "chroma-js";

const defaults = {
  icon: [
    "circle",
    "square",
    "star",
    "cards-diamond",
    "cloud",
    "pentagon",
    "triangle",
    "wifi-strength-4",

  ],
  color: chroma.brewer.Dark2
};

const defaultValue = {
  color: "lightgrey",
  icon: "circle-outline"
};

const restitution = {
  valueOfType(type, d, dataList, options = {}) {
    const types = options[type] || defaults[type];

    const indexElemAutres = dataList.findIndex(e => e.text == "Autres");
    const value = this.getValue(d, options);
    let index;
    let arrayOut = [];
    for (const v of value) {
      index = dataList.findIndex(e => e.text == v);
      let out =
        index != -1
          ? types[index]
          : indexElemAutres != -1
          ? types[indexElemAutres]
          : null;
      out = out || defaultValue[type];
      arrayOut.push(out)
    }
    return arrayOut;
  },

  color(d, dataList, options = {}) {
    return this.valueOfType("color", d, dataList, options);
  },

  icon(d, dataList, options = {}) {
    return this.valueOfType("icon", d, dataList, options);
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

  dataList(data, options) {
    let dataList = [];
    const name = options.name;
    for (const d of data
      // .filter(d1 => d1.selected)
      ) {
      const value = this.getValue(d[name], options);
      for (const v of value) {
        let elem = dataList.find(d => d.text == v);
        if (!elem) {
          elem = { text: v, count: 0, value: d[name] };
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
