import { config } from "../config.js";

var url = urlRelative => {
  return `${config.URL_APPLICATION}/${urlRelative}`;
};

var fail = (msg) => {
  console.log(`apiRequest fail : ${msg}`);
};

var apiRequest = (urlRelative, data=null) => {
  return new Promise((resolve, reject=fail) => {
    fetch(url(urlRelative), data).then(
      response => {
        var contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
          response.json().then(
            (json) => {
              resolve(json);
            });
        } else {
          reject(`Erreur dans apiRequest la reponse n'est pas de type json ${urlRelative}`);
          console.log("Oops, nous n'avons pas du JSON!");
        }
      },
      msg_fail => {
        console.log(`Erreur dans apiRequest ${urlRelative} ${msg_fail}`);
        reject(msg_fail)
      }
    );
  });
};

export { apiRequest };
