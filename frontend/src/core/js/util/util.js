/* Quelques fonctions simples */




// import moment from "moment";
import fastDeepEqual from 'fast-deep-equal';
/** Functions utiles */

// fonction de comparaison d'objets
// elle permet de comparer deux objets
// en profondeur
// exemple :
// const obj1 = {a: 1, b: {c: 2}}
// const obj2 = {a: 1, b: {c: 2}}
// console.log(fde(obj1, obj2)) // true
// obj2.b.c = 3
// console.log(fde(obj1, obj2)) // false  
const fde = (obj1, obj2) => {
  return fastDeepEqual(obj1, obj2)
}


const jsoncopy = obj => {
  return obj
    ? JSON.parse(JSON.stringify(obj))
    : null;
}



const copy = obj => {
  /*
    // fonction de copie d'objet
    // elle permet de copier un objet
    // en profondeur
    // exemple :
    // const obj = {a: 1, b: {c: 2}}
    // const objCopy = copy(obj)
    // objCopy.b.c = 3
    // console.log(obj.b.c) // 2
    // console.log(objCopy.b.c) // 3
  */


  if (Array.isArray(obj)) {
    return obj.map(item => copy(item));
  } else if (typeof obj === "object" && obj) {
    const out = {};
    for (const key in obj) {
      out[key] = copy(obj[key]);
    }
    return out;
  } else {
    return obj;
  }
};

// const arrayEqual = (array1, array2) => {
//   return JSON.stringify(array1.sort()) === JSON.stringify(array2.sort());
// };


// const htmlToElement = html => {
//   const template = document.createElement("template");
//   template.innerHTML = html.trim();

//   return template.content.firstChild;
// };

// const removeElementByClass = (className, element) => {
//   const baseElement = element || document;
//   let elements = baseElement.getElementsByClassName(className);
//   while (elements.length > 0) {
//     elements[0].parentNode.removeChild(elements[0]);
//   }
// };

// const removeDoublons = array => [...new Set(array)];

// TODO REMOVE moment use only once
// const addDays = (sDate, days) => {
//   const m = moment(sDate);
//   m.add(days, "days");
//   const sDatenew = m.format("YYYY-MM-DD");

//   return sDatenew;
// };


const sortDate = (a, b) => {
  // retourne 0 si les dates sont égales, -1 si a est plus petit que b, 1 sinon
  if(!(a && b)) return 0
  if(!a) return -1;
  if(!b) return 1
  if (a.includes("/")) {
    const date_a = a.split("/");
    const date_b = b.split("/");
    return date_a[2] == date_b[2]
      ? date_a[1] == date_b[1]
        ? date_a[0] == date_b[0]
          ? 0
          : Number(date_a[0]) - Number(date_b[0])
        : Number(date_a[1]) - Number(date_b[1])
      : Number(date_a[2]) - Number(date_b[2]);
  } else {
    return a == b ? 0 : a < b ? -1 : 1;
  }
};

// Met la première lettre en majuscule pour le nommage des stores
const upFirstLetter = s => {
  return s.charAt(0).toUpperCase() + s.slice(1);
};

// Retourne true si l'objet est un objet et non un tableau
const isObject = obj => {
  return Object(obj) === obj && !Array.isArray(obj);
}

// Renomme en snake pour les url de requete get
const camelToSnakeCase = str =>
  str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);

const round = function(x, dec) {
  if (x == 0) return 0;
  return Math.floor(x * 10 ** dec) / 10 ** dec;
};


export {
  // addDays,
  copy,
  // htmlToElement,
  // removeDoublons,
  // removeElementByClass,
  // arrayEqual,
  sortDate,
  upFirstLetter,
  camelToSnakeCase,
  round,
  isObject,
  jsoncopy,
  fde
};
