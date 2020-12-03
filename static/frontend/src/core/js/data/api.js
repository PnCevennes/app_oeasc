import { config } from "@/config/config.js";

var url = (urlRelative, params = {}) => {
  const url = new URL(`${config.URL_APPLICATION}/${urlRelative}`);
  Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
  return url;
};

var fail = msg => {
  console.error(`apiRequest fail : ${msg}`);
};

var apiRequest = (method, urlRelative, options = {}) => {
  return new Promise((resolve, reject = fail) => {
    var fetchOptions = {
      method,
      credentials: "include"
    };

    
    if (["POST", "PATCH"].includes(method)) {
      const postOptions = {};
      if (Object.values(options.postData).some(d => d instanceof File)) {
        var data = new FormData();
        for (const [key, value] of Object.entries(options.postData || {})) {
          data.append(key, value);
        }
        postOptions.body = data;
      } else {
        postOptions.body = JSON.stringify(options.postData || {});
        postOptions.headers = {
          Accept: "application/json, text/plain, */*",
          "Content-Type": "application/json"
        };

      }

      fetchOptions = { ...fetchOptions, ...postOptions };
    }

    fetch(url(urlRelative, options.params), fetchOptions).then(
      response => {
        const acceptedStatus = options.accpetedStatus || [200];
        if (acceptedStatus.includes(response.status)) {
          // && contentType.indexOf('application/json') !== -1) {
          response.json().then(
            json => {
              resolve(json);
            },
            error => {
              reject(error);
            }
          );
        } else {
          if (response.json) {
            response.json().then(response => {
              reject(response);
            });
          } else {
            reject(response);
          }
        }
      },
      msg_fail => {
        console.error(`Erreur dans apiRequest ${urlRelative} ${msg_fail}`);
        reject(msg_fail);
      }
    );
  });
};

export { apiRequest };
