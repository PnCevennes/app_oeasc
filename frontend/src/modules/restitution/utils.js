import { copy } from "@/core/js/util/util.js";

const compareDates = (a, b) =>
  a.text.split("/")[1] - b.text.split("/")[1] ||
  a.text.split("/")[0] - b.text.split("/")[0];

const fillDates = dataList => {
  dataList = copy(dataList);
  dataList = dataList.sort(compareDates);
  const dMin = dataList[0].text;
  const dMax = dataList[dataList.length - 1].text;
  let d = dMin;
  //pour avoir tous les mois
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
      dataList.push({ text: d, count: 0, key: dataList[0].key});
    }
  }
  dataList = dataList.sort(compareDates);
  return dataList;
};

const split = separator => (d, item) => {
  return d[item.key].split(separator);
};

const replace = replaceList => (d, item) => {
  let val = d[item.key];
  for (const replace of replaceList) {
    if (replace[0] == val);
    val = replace[1];
  }
  return val;
};

export default {
  fillDates,
  split,
  replace,
};
