/* eslint-disable no-magic-numbers */
import moment from 'moment';

/** Functions utiles */

var copy = obj => JSON.parse(JSON.stringify(obj));

var htmlToElement = html => {
  var template = document.createElement('template');
  template.innerHTML = html.trim();

  return template.content.firstChild;
};

var removeDoublons = array => [...new Set(array)];

var addDays = (sDate, days) => {
  const m = moment(sDate);
  m.add(days, 'days');
  const sDatenew = m.format('YYYY-MM-DD');

  return sDatenew;
};

export { addDays, copy, htmlToElement, removeDoublons };
