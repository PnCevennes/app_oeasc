import { config } from "@/config/config.js";

const STORE = {};

for (const key of ["state", "mutations", "getters"]) {
  STORE[key] = STORE[key] || {};
}
if (STORE.state.pendings == undefined) {
  STORE.state.pendings = {};
  STORE.getters.pendings = state => api => state.pendings[api];
  STORE.mutations.addPending = (state, { request, api }) => {
    state.pendings[api] = request;
  };
  STORE.mutations.removePending = (state, api) => {
    if (state.pendings[api]) {
      delete state.pendings[api];
    }
  };
}

var url = (urlRelative, params = {}) => {
  const url = new URL(`${config.URL_APPLICATION}${urlRelative}`);
  Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
  return url;
};

var fail = msg => {
  console.error(`apiRequest fail : ${msg}`);
};

var apiRequest = (method, urlRelative, options = {}, $store = null) => {
  // pending request
  const url_ = url(urlRelative, options.params);

  let request = null;
  let commit;
  if (method == "GET" && $store) {
    //?? autre methodes ??
    request = $store.getters.pendings(url_.href);
    if (!request) {
      commit = true;
    } else {
      // console.log("use pending", url_.href);
    }
  }

  request =
    request ||
    new Promise((resolve, reject = fail) => {
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

      fetch(url_, fetchOptions).then(
        response => {
          if (method == "GET" && $store) {
            $store.commit("removePending", url_.href);
          } // remove pending

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
              response.json().then(
                json => {
                  reject(json);
                },
                error => {
                  reject(error);
                }
              );
            } else {
              reject(response);
            }
          }
        },
        msg_fail => {
          if (method == "GET" && $store) {
            $store.commit("removePending", url_.href);
          } // remove pending

          console.error(`Erreur dans apiRequest ${urlRelative} ${msg_fail}`);
          reject(msg_fail);
        }
      );
    });

  if (commit) {
    $store.commit("addPending", {
      api: url_.href,
      request
    });
  }

  return request;
};

export { apiRequest, STORE };
