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
  condFilter(v, options) {
    if (Array.isArray(v)) {
      return v.some(e => this.condFilter(e, options));
    }
    const name = options.name;
    return !(
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
      if (!this.condFilter(v, options)) {
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
        out = types[v];
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
    let value = d[options.name];

    if (options.replace) {
      for (const rep of options.replace) {
        if (value == rep[0]) {
          value = rep[1];
        }
      }
    }

    if (options.process) {
      value = options.process(d, options);
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
    for (const d of data) {
      const value = this.getValue(d, options);

      for (const v of value) {
        if (!this.condFilter(v, options)) {
          continue;
        }
        let elem = dataList.find(d => d.text == v);
        if (!elem) {
          elem = { text: v, count: 0, value: v, name: options.name };
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
      dataList = this.cutDataList(dataList, options);
    }

    //color icon
    for (const data of dataList) {
      data.icon = this.icon(data, dataList, {
        ...options,
        name: "text",
        process: null
      })[0];
      data.color = this.color(data, dataList, {
        ...options,
        name: "text",
        process: null
      })[0];
    }

    if (options.order) {
      dataList = dataList.sort((a, b) => {
        const indexA = options.order.findIndex(e => e == a.text);
        const indexB = options.order.findIndex(e => e == b.text);
        return indexB - indexA;
      });
    }
    return dataList;
  },

  dataList2(data, options1, options2) {
    // console.log(options1.filters);
    const dataList1 = this.dataList(data, options1);
    const dataList2 = this.dataList(data, options2);
    console.log(dataList1, dataList2)
    for (const data1 of dataList1) {
      data1.data2 = [];
      for (const data2 of dataList2) {
        let countData2 = 0;
        for (const d of data) {
          const value1 = this.getValue(d, options1);
          const value2 = this.getValue(d, options2);

          let cond1, cond2;
          cond1 = data1.text != "Autres" && value1.includes(data1.text);
          cond2 = data2.text != "Autres" && value2.includes(data2.text);

          const cond1_autre =
            data1.text == "Autres" &&
            data1.autres.some(textAutre => value1.includes(textAutre));
          const cond2_autre =
            data2.text == "Autres" &&
            data2.autres.some(textAutre => value2.includes(textAutre));
          let cond = (cond1 || cond1_autre) && (cond2 || cond2_autre);
          let add = 0;

          const testDataList2 = options1.testDataList2 || options2.testDataList2;
          if (cond && testDataList2) {
              add += testDataList2(
              d,
              data1,
              data2,
              options1,
              options2,
            );
          } else {
            add = cond ? 1 : 0;
          }
          countData2 += add;
        }
        data1.data2.push({ ...data2, count: countData2 });
      }
    }
    console.log(dataList1)
    return dataList1;
  },

  cutDataList(dataList, options) {
    const elemAutres = { text: "Autres", count: 0, autres: [], name: options.name  };
    const out = [];
    for (let i = 0; i < dataList.length; i++) {
      if (i < options.nMax) {
        out.push(dataList[i]);
      } else {
        if (i == options.nMax) {
          out.push(elemAutres);
        }
        elemAutres.autres.push(dataList[i].text);
        elemAutres.count += 1;
      }
    }
    return out;
  },

  results(data, options) {
    const dataFiltered = restitution.filterData(data, options);
    const itemChoix1 = restitution.getItem(options.choix1, options);
    const itemChoix2 = restitution.getItem(options.choix2, options);
    const resultChoix1 = {
      dataList:
        itemChoix1 && itemChoix2
          ? restitution.dataList2(
              dataFiltered,
              {
                ...itemChoix1,
                filters: options.filters,
                nMax: options.nbMax1
              },
              {
                ...options,
                ...itemChoix2,
                filters: options.filters,
                nMax: options.nbMax2
              }
            )
          : options.choix1 &&
            restitution.dataList(dataFiltered, {
              ...itemChoix1,
              filters: options.filters,
              nMax: options.nbMax1
            }),
      ...itemChoix1
    };

    const resultChoix2 = itemChoix2 && {
      dataList: restitution.dataList(dataFiltered, {
        ...itemChoix2,
        filters: options.filters,
        nMax: options.nbMax2
      }),
      ...itemChoix2
    };
    const markers = restitution.markers(
      dataFiltered,
      options,
      resultChoix1,
      resultChoix2
    );
    const markerLegendGroups = restitution.markerLegendGroups(
      options,
      resultChoix1,
      resultChoix2
    );
    return {
      choix: {
        choix1: resultChoix1,
        choix2: resultChoix2
      },
      markers,
      markerLegendGroups,
      ...options,
      condSame:
        resultChoix1 && resultChoix2 && resultChoix2.name == resultChoix1.name,
      nbData: data.length,
      nbDataFiltered: dataFiltered.length,
      filtersDisplay: restitution.filtersDisplay(options)
    };
  },

  filtersDisplay(options) {
    let out = [];
    for (const [key, filter] of Object.entries(options.filters || {})) {
      const filterText = filter && filter.length ? filter.join(", ") : "";
      if (filterText) {
        out.push(`${options.items[key].text} : ${filterText}`);
      }
    }
    return out.join("; ");
  },

  getItem(name, options) {
    return (
      name in options.items && {
        ...options.items[name],
        name
      }
    );
  },

  filterData(data, options) {
    if (!Object.keys(options.filters || {}).length) {
      return data;
    }
    const dataFiltered = data.filter(d => {
      let cond = true;
      for (const [filterName, filterValue] of Object.entries(options.filters)) {
        const item = restitution.getItem(filterName, options) || {
          name: filterName
        };

        const value = restitution.getValue(d, item);
        const test = filterValue;
        if (!filterValue) continue;
        const condFilter =
          !(test && test.length) || test.some(v => value.includes(v));
        cond = cond && condFilter;
      }
      return cond;
    });
    return dataFiltered;
  },

  markers(dataFiltered, options, resultChoix1, resultChoix2) {
    const condSame =
      resultChoix1 && resultChoix2 && resultChoix2.name == resultChoix1.name;

    return dataFiltered.map(d => {
      const icon =
        resultChoix2 &&
        restitution.valueOfType("icon", d, resultChoix2.dataList, {
          ...resultChoix2,
          filters: options.filters
        });
      const color =
        resultChoix1 &&
        restitution.valueOfType("color", d, resultChoix1.dataList, {
          ...resultChoix1,
          ...options
        });
      const defs =
        resultChoix1.processMarkerDefs &&
        resultChoix1.processMarkerDefs(d, { ...resultChoix1, ...options });
      return {
        coords: d[options.coordsFieldName],
        type: "label",
        condSame,
        defs,
        style: {
          icon,
          color
        }
      };
    });
  },

  markerLegendGroups(options, resultChoix1, resultChoix2) {
    const icon_default = "circle";
    const color_default = "rgb(150,150,150)";
    const markerLegendGroups = [];
    const condSame =
      resultChoix1 && resultChoix2 && resultChoix2.name == resultChoix1.name;
    let index = 0;
    for (const res of [resultChoix1, resultChoix2].filter(r => !!r)) {
      const markerLegends = {
        title: res.text,
        legends: res.dataList
          .filter(
            data =>
              !(
                options.filters &&
                options.filters[res.name] &&
                options.filters[res.name].length &&
                !options.filters[res.name].includes(data.text)
              )
          )
          .map(data => ({
            text: data.text,
            count: data.count,
            icon: ((condSame || index == 1) && data.icon) || icon_default,
            color: ((condSame || index == 0) && data.color) || color_default
          }))
      };
      index += 1;

      markerLegendGroups.push(markerLegends);

      if (condSame) break;
    }
    return markerLegendGroups;
  },

  getData: (config, $store) => {
    return new Promise((resolve, reject) => {
      $store.dispatch(config.getData).then(
        data => {
          resolve(
            restitution.filterData(data, {
              ...config,
              filters: config.preFilters
            })
          );
          return;
        },
        error => {
          reject(error);
          return;
        }
      );
    });
  }
};

export { restitution };
