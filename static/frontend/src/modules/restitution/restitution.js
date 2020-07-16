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
    "wifi-strength-4"
  ],
  color: chroma.brewer.Dark2
};

const defaultValue = {
  color: "lightgrey",
  icon: "stop_circle"
};

const restitution = {
  
  condFilter(options, v) {
    const name = options.name;
    return (
      options.filters &&
      options.filters[name] &&
      options.filters[name].length &&
      !options.filters[name].includes(v)
    );
  },

  valueOfType(type, d, dataList, options = {}) {
    const types = options[type] || defaults[type];

    const indexElemAutres = dataList.findIndex(e => e.text == "Autres");
    const value = this.getValue(d, options);
    
    let index;
    let arrayOut = [];
    for (const v of value) {
      if (this.condFilter(options, v)) {
        continue;
      }
      let out;
      if (Array.isArray(types)) {
        index = dataList.findIndex(e => e.text == v);
        out =
          index != -1
            ? types[index]
            : indexElemAutres != -1
            ? types[indexElemAutres]
            : null;
      } else {
        out = types[d];
      }

      out = out || defaultValue[type];

      arrayOut.push(out);
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

    if (options.process) {
      value = options.process(d);
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
    for (const d of data) {
      const value = this.getValue(d[name], options);
      for (const v of value) {
        if (this.condFilter(options, v)) {
          continue;
        }
        let elem = dataList.find(d => d.text == v);
        if (!elem) {
          elem = { text: v, count: 0, value: d[name] };
          dataList.push(elem);
        }
        elem.count += 1;
      }
    }

    if (options.type == "date") {
      dataList = dataList.sort(
        (a, b) =>
          a.text.split("/")[1] - b.text.split("/")[1] ||
          a.text.split("/")[0] - b.text.split("/")[0]
      );
      const dMin = dataList[0].text;
      const dMax = dataList[dataList.length - 1].text;
      let d = dMin;
      while (
        !(
          d.split("/")[1] >= dMax.split("/")[1] &&
          d.split("/")[0] >= dMax.split("/")[0]
        )
      ) {
        let y = parseInt(d.split("/")[1]);
        let m = parseInt(d.split("/")[0]) + 1;
        if (m == 13) {
          m = 1;
          y += 1;
        }
        d = `${m < 10 ? "0" : ""}${m}/${y}`;
        if (!dataList.find(data => data.text == d)) {
          dataList.push({ text: d, count: 0 });
        }
      }
      dataList = dataList.sort(
        (a, b) =>
          a.text.split("/")[1] - b.text.split("/")[1] ||
          a.text.split("/")[0] - b.text.split("/")[0]
      );
    } else {
      dataList = dataList.sort((a, b) => b.count - a.count);
    }

    if (options.nMax && options.type != "date") {
      dataList = this.cutDataList(dataList, options.nMax);
    }

    //color icon
    for (const data of dataList) {
      data.icon = this.icon(data.text, dataList, options)[0];
      data.color = this.color(data.text, dataList, options)[0];
    }

    return dataList;
  },

  dataList2(data, options1, options2) {
    const name1 = options1.name;
    const name2 = options2.name;

    const dataList1 = this.dataList(data, options1);
    const dataList2 = this.dataList(data, options2);

    for (const data1 of dataList1) {
      data1.data2 = [];
      console.log(data1.text);
      for (const data2 of dataList2) {
        let countData2 = 0;
        for (const d of data) {
          const value1 = this.getValue(d[name1], options1);
          const value2 = this.getValue(d[name2], options2);
          const cond1 = data1.text != "Autres" && value1.includes(data1.text);
          const cond2 = data2.text != "Autres" && value2.includes(data2.text);
          const cond1_autre =
            data1.text == "Autres" &&
            data1.autres.some(textAutre => value1.includes(textAutre));
          const cond2_autre =
            data2.text == "Autres" &&
            data2.autres.some(textAutre => value2.includes(textAutre));
          if ((cond1 || cond1_autre) && (cond2 || cond2_autre)) {
            countData2++;
          }
        }
        data1.data2.push({ ...data2, count: countData2 });
      }
    }
    return dataList1;
  },

  cutDataList(dataList, nMax) {
    const elemAutres = { text: "Autres", count: 0, autres: [] };
    const out = [];
    for (let i = 0; i < dataList.length; i++) {
      if (i < nMax) {
        out.push(dataList[i]);
      } else {
        if (i == nMax) {
          out.push(elemAutres);
        }
        elemAutres.autres.push(dataList[i].text);
        elemAutres.count += 1;
      }
    }
    return out;
  },

  
};

export { restitution };
