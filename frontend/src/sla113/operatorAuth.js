/**
 * SLA113 operator credentials for the standalone console.
 *
 * The backend now requires an operator for every SLA113 write (see
 * backend/core/operator_guard.py). The console has no login of its own, so:
 *  - every request to /api/sla113 carries the stored operator key, and the HIC
 *    access token if the operator is also signed in to HIC (a system-admin
 *    session is accepted as an operator);
 *  - on a 401 OPERATOR_REQUIRED the operator is asked for the key once, it is
 *    stored in this browser, and the request is retried.
 *
 * Scoped to SLA113 URLs only, and installed/ejected with the console, so the
 * public Arcade and Showcase pages are unaffected.
 */
import axios from "axios";

const OPERATOR_KEY_STORAGE = "sla113_operator_key";
const HIC_ACCESS_TOKEN_STORAGE = "access_token";
const OPERATOR_HEADER = "X-SLA113-Operator-Key";

const isOperatorUrl = (url = "") => url.includes("/api/sla113");

const readStorage = (key) => {
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
};

const writeStorage = (key, value) => {
  try {
    if (value) window.localStorage.setItem(key, value);
    else window.localStorage.removeItem(key);
  } catch {
    /* storage unavailable: key lasts for this request only */
  }
};

export function clearOperatorKey() {
  writeStorage(OPERATOR_KEY_STORAGE, null);
}

export function installOperatorAuth(client = axios) {
  const requestId = client.interceptors.request.use((config) => {
    if (!isOperatorUrl(config.url)) return config;
    config.headers = config.headers || {};
    const key = readStorage(OPERATOR_KEY_STORAGE);
    if (key && !config.headers[OPERATOR_HEADER]) {
      config.headers[OPERATOR_HEADER] = key;
    }
    const token = readStorage(HIC_ACCESS_TOKEN_STORAGE);
    if (token && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  const responseId = client.interceptors.response.use(
    (response) => response,
    async (error) => {
      const { config, response } = error || {};
      const code = response?.data?.detail?.code;
      if (
        response?.status === 401 &&
        code === "OPERATOR_REQUIRED" &&
        config &&
        isOperatorUrl(config.url) &&
        !config.__sla113OperatorRetry
      ) {
        const entered = window.prompt(
          "This SLA113 action needs the operator key (SLA113_OPERATOR_KEY). " +
            "It will be saved in this browser."
        );
        if (entered && entered.trim()) {
          writeStorage(OPERATOR_KEY_STORAGE, entered.trim());
          config.__sla113OperatorRetry = true;
          config.headers = { ...(config.headers || {}), [OPERATOR_HEADER]: entered.trim() };
          return client(config);
        }
      }
      if (response?.status === 401 && code === "OPERATOR_REQUIRED" && config?.__sla113OperatorRetry) {
        // The key that was just entered was rejected; forget it.
        clearOperatorKey();
      }
      return Promise.reject(error);
    }
  );

  return () => {
    client.interceptors.request.eject(requestId);
    client.interceptors.response.eject(responseId);
  };
}
