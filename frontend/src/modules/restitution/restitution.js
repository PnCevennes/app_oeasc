import * as chroma from "chroma-js";
import restitutionUtils from "./utils.js";

class Restitution {
  $store;
  _valid = false;
  _options = {};
  _rawData;
  _defaultTypes = {
    icons: [
      "circle",
      "square",
      "star",
      "cards-diamond",
      "cloud",
      "pentagon",
      "triangle",
      "wifi-strength-4"
    ],
    colors: chroma.brewer.Dark2,
    icon: "circle",
    color: "rgb(150,150,150)"
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
    const keys = Object.keys(this.items);
    keys.push(this._options.coordsFieldName);
    if (this._options.groupByKey) {
      keys.push(this._options.groupByKey);
    }
    return data.map(d => {
      const d_ = {};
      for (const key of keys) {
        // for (const key of Object.keys(d)) {
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
    const name = item.source || key;
    const value = item.process ? item.process(d, item) : d[name];

    // toujours renvoyer un Array
    return !value ||
      value == [] ||
      (Array.isArray(value) && value.some(v => !v))
      ? ["Indéfini"]
      : Array.isArray(value)
      ? value
      : [value];
  }

  /** list de {key, value, count, ect..} pour les resultats */
  /** comment faire le groupBy ??  */
  dataList(key, filters = null) {
    let dataList = [];
    const item = this.item(key);

    const dataToProcess = this.groupBy(
      this.filteredData(filters),
      this._options.groupByKey,
      [key],
      "concat"
    );

    for (const d of dataToProcess) {
      const value = d[key];

      const elemTextSaves = [];

      for (const v of value) {
        // test si déjà dans la liste
        let elem = dataList.find(d => d.text == v);
        /// si non on le rajoute
        if (!elem) {
          elem = { text: v, count: 0, key };

          dataList.push(elem);
        }
        const elemTextSave = elemTextSaves.find(text => text == elem.text);
        if (!elemTextSave) {
          elemTextSaves.push(elem.text);
          elem.count += 1;
        }
      }
    }
    if (item.type == "date") {
      // on rempli les mois pour ne pas avoir de trous
      dataList = restitutionUtils.fillDates(dataList);
      for (const data of dataList) {
        data.icon = this.icon(data.text, dataList);
        data.color = 'grey';
      }
    } else {
      dataList = dataList.sort((a, b) => b.count - a.count);
      dataList = this.cutDataList(dataList);

      for (const data of dataList) {
        data.icon = this.icon(data.text, dataList);
        data.color = this.color(data.text, dataList);
      }
    }

    return dataList;
  }

  /**
   * pour garder seulement les pires degat
   * apply patch
   * un peu flottant à rendre robuste
   * si patch : pour chaque degat de meme type on garde le max
   */
  patchMaxDegat(d) {
    const key_item_patch = [this._options.choix1, this.options.choix2].find(
      key => this.item(key) && this.item(key).patch
    );
    if (key_item_patch) {
      const keep = {};
      for (const r of d.res) {
        if (
          keep[r.degat_type_label] &&
          keep[r.degat_type_label].degat_gravite_label
        ) {
          const prev = keep[r.degat_type_label].degat_gravite_label[0];
          const cur = r.degat_gravite_label[0];
          const order = this.item(key_item_patch).order;
          const ind_prev = order.indexOf(prev);
          const ind_cur = order.indexOf(cur);
          if (ind_cur < ind_prev) {
            keep[r.degat_gravite_label] = r;
          }
        } else {
          keep[r.degat_type_label] = r;
        }
      }
      d.res = Object.keys(keep).map(key => keep[key]);
    }
  }

  /**
   * out: [...{ groupByKey: grouByValue, res: process(dataGroup, processArgs) }...]
   */
  groupBy(data, groupByKey = null, keys = [], action = null) {
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
    const out = Object.entries(dataDict).map(([groupByValue, dataGroup]) => {
      const d = {};

      d[groupByKey] = groupByValue;

      if (!keys.length) {
        return d;
      }

      const listGroup = this._options.markersGroupByReduceKeys || [];

      for (const key of keys.filter(key => !listGroup.includes(key) && !!key)) {
        d[key] = dataGroup[0][key];
      }

      const condReduce = keys.some(choix => listGroup.includes(choix));
      const dataProcessed = condReduce ? dataGroup : [dataGroup[0]];

      d.res = dataProcessed.map(data => {
        const res = {};
        for (const key of keys.filter(key => !!key)) {
          res[key] = data[key];
        }
        return res;
      });
      if (action == "concat") {
        for (const r of d.res) {
          for (const key of Object.keys(r).filter(key =>
            listGroup.includes(key)
          )) {
            d[key] = (d[key] || []).concat(r[key]);
          }
        }
      }

      if (action == "max") {
        this.patchMaxDegat(d);
      }

      return d;
    });

    return out;
  }

  /** quand on a deux choix (pour les graphes et les tableaux) */
  dataListStacked(dataList1, dataList2) {
    const filteredData = this.filteredData();
    for (const data1 of dataList1) {
      data1.subDataList = [];
      for (const data2 of dataList2) {
        const filters = {};
        filters[data1.key] =
          data1.text != "Autres" ? [data1.text] : data1.autres;
        filters[data2.key] =
          data2.text != "Autres" ? [data2.text] : data2.autres;
        const dataCur = this.filterData(filteredData, filters);

        const countData2 = this.groupBy(dataCur, this.options.groupByKey)
          .length;
        data1.subDataList.push({ ...data2, count: countData2 });
      }
      data1.subDataList.sort((a, b) => b.count - a.count);
    }
    return dataList1;
  }

  filtersDisplay() {
    let out = [];
    for (const [key, filter] of Object.entries(this._options.filters || {})) {
      const filterText = filter && filter.length ? filter.join(", ") : "";
      if (filterText) {
        out.push(`${this.item(key).text} : ${filterText}`);
      }
    }
    return out.join("; ");
  }

  markers(dataList1, dataList2) {
    const condSame = this.condSame();

    let dataMarkers = this.filteredData();

    const markersGroupByKey = this._options.markersGroupByKey;
    if (markersGroupByKey) {
      dataMarkers = this.groupBy(
        dataMarkers,
        this._options.markersGroupByKey,
        [
          this._options.choix1,
          this._options.choix2,
          this._options.coordsFieldName
        ],
        "max"
      );
    }

    const markers = dataMarkers.map(d => {
      const defs = [];

      for (const res of d.res) {
        const d1 = res[this._options.choix1];
        const d2 = res[this._options.choix2];
        d1, d2;
        for (const v1 of d1) {
          if (!d2) {
            defs.push({
              color: this.color(v1, dataList1),
              icon: this.icon(null, dataList1)
            });
          } else if (d2 && condSame) {
            defs.push({
              icon: this.icon(v1, dataList1),
              color: this.color(v1, dataList1)
            });
          } else {
            for (const v2 of d2) {
              defs.push({
                icon: this.icon(v2, dataList2),
                color: this.color(v1, dataList1)
              });
            }
          }
        }
      }
      return {
        coords: d[this._options.coordsFieldName],
        type: "label",
        condSame,
        defs
      };
    });
    markers;
    return markers;
  }

  condSame() {
    return this._options.choix1 == this._options.choix2;
  }

  markerLegendGroups(dataList1, dataList2) {
    const markerLegendGroups = [{ title: this.yTitle() }];
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
          icon:
            ((condSame || index == 1) && data.icon) || this._defaultTypes.icon,
          color:
            ((condSame || index == 0) && data.color) || this._defaultTypes.color
        }))
      };
      index += 1;

      markerLegendGroups.push(markerLegends);

      if (condSame) break;
    }
    return markerLegendGroups;
  }

  data() {
    if (this._data && this._data.length) {
      return this._data;
    }
    this._data =
      this._rawData && this._rawData.length
        ? this.filterData(
            this.processData(this._rawData),
            this._options.preFilters || {}
          )
        : [];
    return this._data;
  }

  resetData() {
    this._data = null;
  }

  filteredData(filters = null) {
    // if(!this._filteredData) {
    //   this._filteredData  = this.filterData(this.data(), filters);
    // }
    // return this._filteredData
    return this.filterData(this.data(), filters);
  }

  /** results */
  results() {
    this.resetData();
    let dataList1 = this.dataList(this._options.choix1);
    const item1 = this.item(this._options.choix1);
    const dataList2 =
      this._options.choix2 && this.dataList(this._options.choix2);
    const item2 = this.item(this._options.choix2);

    if (dataList1 && dataList2) {
      dataList1 = this.dataListStacked(dataList1, dataList2);
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
      markers: this.markers(dataList1, dataList2),
      markerLegendGroups: this.markerLegendGroups(dataList1, dataList2),
      yTitle: this.yTitle(),
      items: this.items,
      nbDataFiltered: this.filteredData().length,
      nbData: this.data().length,
      filtersDisplay: this.filtersDisplay()
    };

    if (dataList2) {
      out.choix.choix2 = {
        dataList: dataList2,
        text: item2.text
      };
    }

    return out;
  }

  yTitle() {
    return this._options.groupByKeyItems.find(
      i => i.value == this._options.groupByKey
    ).text;
  }

  item(key) {
    return { ...(this.items[key] || {}), key };
  }

  /** type : icon ou color */
  valueOfType(type, value, dataList) {
    let out;
    const key = dataList[0].key;

    const item = this.item(key);
    const types = item[`${type}s`] || this._defaultTypes[`${type}s`];
    if (!Array.isArray(types)) {
      out = types[value];
    } else {
      // sinon types est un array
      let index = dataList.findIndex(e => e.text == value);
      if (index == -1) {
        index = dataList.findIndex(e => e.text == "Autres");
      }

      out = types[index];
    }
    return out || this._defaultTypes[type];
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
    const elemAutres = {
      text: "Autres",
      count: 0,
      autres: [],
      key: dataList[0].key
    };
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
