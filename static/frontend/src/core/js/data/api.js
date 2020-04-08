import { config } from "@/config/config.js";

var url = urlRelative => {
  return `${config.URL_APPLICATION}/${urlRelative}`;
};

var fail = msg => {
  console.log(`apiRequest fail : ${msg}`);
};

var apiRequest = (method, urlRelative, options = {}) => {
  return new Promise((resolve, reject = fail) => {
    var fetchOptions = {
      method,
      credentials: "include"
    };

    if (["POST", "PATCH"].includes(method)) {
      const postOptions = {
        body: JSON.stringify(options.data || {}),
        headers: {
          Accept: "application/json, text/plain, */*",
          "Content-Type": "application/json"
        }
      };
      fetchOptions = { ...fetchOptions, ...postOptions };
    }
    fetch(url(urlRelative), fetchOptions).then(
      response => {
        const acceptedStatus = options.accpetedStatus || [200];
        if (acceptedStatus.includes(response.status)) {
          // && contentType.indexOf('application/json') !== -1) {
          response.json().then(
            json => {
              resolve(json);
            },
            error => {
              console.log('aaa', error);
              reject(error);
            }
          );
        } else {
          reject(response);
        }
      },
      msg_fail => {
        console.log(`Erreur dans apiRequest ${urlRelative} ${msg_fail}`);
        reject(msg_fail);
      }
    );
  });
};

export { apiRequest };
