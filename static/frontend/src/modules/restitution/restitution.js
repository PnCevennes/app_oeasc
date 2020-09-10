import * as chroma from "chroma-js";
import restitutionUtils from "./utils.js";

class Restitution {
  $store;
  _valid = false;
  _options = {};
  _rawData;
  _defaultTypes = {
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

  constructor(dataType, $store) {
    this.$store = $store;
    this._options.dataType = dataType;
    this._valid = !!this.getConfig();
    if (this.valid()) {
      this.setDefaultOptions();
    }
  }

  valid() {
    return this._valid;
  }

  options() {
    return this._options;
  }

  setOptions(options) {
    for (const key of Object.keys(options)) {
      this._options[key] = options[key];
    }
  }

  setDefaultOptions() {
    if (this.default) {
      for (const key of Object.keys(this.default)) {
        this._options[key] = this._options[key] || this.default[key];
      }
      this._options = this.default;
    }
  }

  processData(data) {
    return data.map(d => {
      const d_ = {};
      for (const key of Object.keys(d)) {
        d_[key] = this.getValue(d, key);
      }
      return d_;
    });
  }

  filterData(data, filters) {
    let filteredData = data;
    for (const [key, filter] of Object.entries(
      filters || this._options.filters || {}
    )) {
      filteredData = filteredData.filter(d =>
        d[key].some(v => !(filter && filter.length && !filter.includes(v)))
      );
    }
    return filteredData;
  }

  getValue(d, key) {
    const item = this.item(key);
    const value = item.process ? item.process(d, item) : d[key];

    // toujours renvoyer un Array
    return !value ? [] : Array.isArray(value) ? value : [value];
  }

  /** list de {key, value, count, ect..} pour les resultats */
  /** comment faire le groupBy ??  */
  dataList(key, filters = null) {
    let dataList = [];
    const item = this.item(key);
    for (const d of this.filteredData(filters)) {
      const value = d[key];
      // console.log(value)
      for (const v of value) {
        // test si déjà dans la liste
        let elem = dataList.find(d => d.text == v);
        /// si non on le rajoute
        if (!elem) {
          elem = { text: v, count: 0, key };
          dataList.push(elem);
        }
        elem.count += 1;
      }
    }
    if (item.type == "date") {
      // on rempli les mois pour ne pas avoir de trous
      dataList = restitutionUtils.fillDates(dataList);
    } else {
      dataList = dataList.sort((a, b) => b.count - a.count);
      dataList = this.cutDataList(dataList);
    }

    for (const data of dataList) {
      data.icon = this.icon(data.text, dataList);
      data.color = this.color(data.text, dataList);
    }

    return dataList;
  }

  /**
   * out: [...{ groupByKey: grouByValue, res: process(dataGroup, processArgs) }...]
   */
  groupBy(data, groupByKey = null, process = null, processArgs = null) {
    // si pas de groupByKey on renvoie data
    if (!groupByKey) {
      return data;
    }

    const dataDict = {};
    // on regroupe par groupByKey dans un dict
    for (const d of data) {
      for (const groupByValue of d[groupByKey]) {
        dataDict[groupByValue] = dataDict[groupByValue] || [];
        dataDict[groupByValue].push(d);
      }
    }

    // out: [...{ groupByKey: grouByValue, res: process(dataGroup, processArgs) }...]
    const out = Object.entries(dataDict).map((groupByValue, dataGroup) => {
      const d = {};
      d[groupByKey] = groupByValue;
      if (process) {
        d.res = process(dataGroup, processArgs);
      }
      return d;
    });

    return out;
  }

  /** quand on a deux choix (pour les graphes et les tableaux) */
  dataList_stacked(dataList1, dataList2) {
    const filteredData = this.filteredData();
    for (const data1 of dataList1) {
      data1.subDataList = [];
      for (const data2 of dataList2) {
        const filters = {};
        filters[data1.key] =
          data1.text == "Autres" ? [data1.text] : data1.autres;
        filters[data2.key] =
          data2.text == "Autres" ? [data2.text] : data2.autres;
        const dataCur = this.filterData(filteredData, filters);
        
        const countData2 = this.groupBy(dataCur, this.options.groupByKey)
          .length;
        data1.subDataList.push({ ...data2, count: countData2 });
      }
    }
  }
  //   dataList_stacked(dataList1, dataList2) {
  //       const filteredData=this.filteredData();
  //     const dataLists = [dataList1, dataList2];
  //     for (const data1 of dataList1) {
  //       data1.subDataList = [];
  //       let countData1 = 0;
  //       for (const data2 of dataList2) {
  //         let countData2 = 0;
  //         for (const d of filteredData) {
  //           let cond = true;
  //             for (const key of dataLists.map(data => data[0].key)) {
  //             const value = d[key];
  //             const data = data1.key == key ? data1 : data2;
  //             const condValue =
  //               data.text != "Autres"
  //                 ? value.includes(data.text)
  //                 : data.autres.some(textAutre => value.includes(textAutre));
  //             cond = cond && condValue;
  //           }
  //           if (cond) {
  //             countData2 += 1;
  //           }
  //         }
  //         countData1 += countData2;
  //         data1.subDataList.push({ ...subDataList, count: countData2 });
  //       }
  //       data1.count = countData1;
  //     }
  //     return dataList1;
  //   }

  markers(dataList1, dataList2) {
    const condSame = this.condSame();

    const markers = this.filteredData().map(d => {
      //   const defs = []
      //   for (const color of colors) {
      //     for (const icons of icons) {
      //       const icon = dataList2 && this.icon(d[this._options.choix2], dataList2);
      //       const color = this.color(d[this._options.choix1], dataList1);
      //       defs.push(color, icon);
      //     }
      //   }
      dataList1, dataList2;
      const def = { color: "red", icon: "pencil" };
      return {
        coords: d[this._options.coordsFieldName],
        type: "label",
        condSame,
        defs: [def]
      };
    });
    return markers;
  }

  condSame() {
    return this._options.choix1 == this._options.choix2;
  }

  markerLegendGroups(dataList1, dataList2) {
    const icon_default = "circle";
    const color_default = "rgb(150,150,150)";
    const markerLegendGroups = [];
    const condSame = this.condSame();
    let index = 0;
    for (const dataList of [dataList1, dataList2].filter(r => !!r)) {
      const key = dataList[0].key;
      const item = this.item(key);
      const markerLegends = {
        title: item.text,
        legends: dataList.map(data => ({
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
  }

  data() {
    return this._rawData && this._rawData.length
      ? this.filterData(
          this.processData(this._rawData),
          this._options.preFilters || {}
        )
      : [];
  }

  resetFilteredData() {
    this._filteredData = null;
  }

  filteredData(filters = null) {
    if (!this._filteredData) {
      console.log("filteredData", this.data());
      this._filteredData = this.filterData(this.data(), filters);
    }
    return this._filteredData;
  }

  /** results */
  results() {
    this.resetFilteredData();
    let dataList1 = this.dataList(this._options.choix1);
    const item1 = this.item(this._options.choix1);
    const dataList2 =
      this._options.choix2 && this.dataList(this._options.choix2);
    const item2 = this.item(this._options.choix2);

    if (dataList1 && dataList2) {
      dataList1 = this.dataList_stacked(dataList1, dataList2);
    }

    const out = {
      condSame: this.condSame(),
      options: this.options(),
      choix: {
        choix1: {
          text: item1.text,
          dataList: dataList1
        }
      },
      makers: this.markers(dataList1, dataList2),
      markerLegendGroups: this.markerLegendGroups(dataList1, dataList2),
      yTitle: this.options.yTitle,
      items: this.items
    };
    if (dataList2) {
      out.choix.choix2 = {
        dataList: dataList2,
        text: item2.text
      };
    }

    return out;
  }

  item(key) {
    return { ...(this.items[key] || {}), key };
  }

  /** type : icon ou color */
  valueOfType(type, value, dataList) {
    const key = dataList[0].key;
    const item = this.item(key);
    const types = item[`${type}s`] || this._defaultTypes[type];
    if (!Array.isArray(types)) {
      return types[value];
    }

    // sinon types est un array
    let index = dataList.findIndex(e => e.text == value);
    if (index == -1) {
      index = dataList.findIndex(e => e.text == "Autres");
    }

    return types[index];
  }

  icon(value, dataList) {
    return this.valueOfType("icon", value, dataList);
  }

  color(value, dataList) {
    return this.valueOfType("color", value, dataList);
  }

  cutDataList(dataList) {
    const nbMax =
      this._options.choix1 == dataList[0].key
        ? this._options.nbMax1
        : this._options.choix2 == dataList[0].key
        ? this._options.nbMax2
        : null;

    if (!nbMax) {
      return dataList;
    }
    const elemAutres = { text: "Autres", count: 0, autres: [] };
    const out = [];
    for (let i = 0; i < dataList.length; i++) {
      if (i < nbMax) {
        out.push(dataList[i]);
      } else {
        if (i == nbMax) {
          out.push(elemAutres);
        }
        elemAutres.autres.push(dataList[i].text);
        elemAutres.count += dataList[i].count;
      }
    }
    return out;
  }

  getConfig() {
    if (!this._options.dataType) {
      return;
    }
    const configRestitution = this.$store.getters.configRestitution(
      this._options.dataType
    );
    if (!configRestitution) {
      return;
    }
    for (const [key, value] of Object.entries(configRestitution)) {
      this[key] = value;
    }
    return this.getDataAction;
  }

  getData() {
    return new Promise((resolve, reject) => {
      if (!this.getDataAction) {
        resolve([]);
      }
      this.$store.dispatch(this.getDataAction).then(
        rawData => {
          this._rawData = rawData;
          resolve(this._rawData);
          return;
        },
        error => {
          reject(error);
          return;
        }
      );
    });
  }
}

export { Restitution };
