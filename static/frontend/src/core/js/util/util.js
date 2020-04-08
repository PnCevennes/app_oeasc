/* eslint-disable no-magic-numbers */
import moment from 'moment';

/** Functions utiles */

const copy = obj => {
  return obj ? JSON.parse(JSON.stringify(obj)): null
};

const arrayEqual = (array1, array2) => {
  return JSON.stringify(array1.sort()) === JSON.stringify(array2.sort());
}

const htmlToElement = html => {
  const template = document.createElement('template');
  template.innerHTML = html.trim();

  return template.content.firstChild;
};

const removeElementByClass = (className, element) => {
  const baseElement = element || document;
  let elements = baseElement.getElementsByClassName(className);
  while(elements.length > 0){
    elements[0].parentNode.removeChild(elements[0]);
  }
}

const removeDoublons = array => [...new Set(array)];

const addDays = (sDate, days) => {
  const m = moment(sDate);
  m.add(days, 'days');
  const sDatenew = m.format('YYYY-MM-DD');

  return sDatenew;
};

const sortDate = (a, b) => {
            
  const date_a = a.split("/");
  const date_b = b.split("/");
  return date_a[2] == date_b[2]
    ? date_a[1] == date_b[1]
    ? date_a[0] == date_b[0]
    ? 0
    : Number(date_a[0]) - Number(date_b[0])
    : Number(date_a[1]) - Number(date_b[1])
    : Number(date_a[2]) - Number(date_b[2]);
}

export { addDays, copy, htmlToElement, removeDoublons, removeElementByClass, arrayEqual, sortDate };
