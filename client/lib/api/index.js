import axios from "axios";
import {
  clearSessionStorage,
  getCachedSession,
  getCachedUser,
  hydrateSessionFromStorage,
  hydrateUserFromStorage,
  setCachedSession,
  setCachedUser
} from "../features/auth/sessionCache";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json"
  }
});

const resolveSession = () => getCachedSession() ?? hydrateSessionFromStorage();

api.interceptors.request.use(
  (config) => {
    const headers = config.headers ? { ...config.headers } : {};

    if (config.data instanceof FormData) {
      delete headers["Content-Type"];
      delete headers["content-type"];
    }

    if (!config.skipAuth) {
      const session = resolveSession();
      if (session?.access_token) {
        headers.Authorization = `Bearer ${session.access_token}`;
      }
    }

    return { ...config, headers };
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearSessionStorage();
      console.error("Unauthorized - please log in");
    }
    return Promise.reject(error);
  }
);

function normalizePath(path) {
  if (!path) {
    return "";
  }

  if (/^https?:\/\//i.test(path)) {
    return path;
  }

  let trimmed = path;
  if (trimmed.startsWith("/api/")) {
    trimmed = trimmed.slice(5);
  } else if (trimmed === "/api") {
    trimmed = "";
  } else if (trimmed.startsWith("/api")) {
    trimmed = trimmed.slice(4);
  }

  return trimmed.replace(/^\/+/, "");
}

export function getAccessToken() {
  return resolveSession()?.access_token ?? null;
}

export function getRefreshToken() {
  return resolveSession()?.refresh_token ?? null;
}

export function getStoredUser() {
  return getCachedUser() ?? hydrateUserFromStorage();
}

export function setSession(session, user) {
  if (session) {
    setCachedSession(session);
  }
  if (user) {
    setCachedUser(user);
  }
}

export function clearSession() {
  clearSessionStorage();
}

export async function apiRequest(path, options = {}) {
  const {
    method = "GET",
    headers = {},
    body,
    auth = true
  } = options;

  const url = normalizePath(path);

  try {
    const response = await api.request({
      url,
      method,
      headers,
      data: body,
      skipAuth: !auth
    });
    return { response, data: response.data };
  } catch (error) {
    if (error.response) {
      return { response: error.response, data: error.response.data, error };
    }
    throw error;
  }
}

export async function login(email, password) {
  const { data } = await apiRequest("login", {
    method: "POST",
    auth: false,
    body: { email, password }
  });

  if (data?.success) {
    setSession(data.session, data.user);
  }

  return data;
}

export async function logout() {
  const refreshToken = getRefreshToken();

  try {
    if (refreshToken) {
      await apiRequest("logout", {
        method: "POST",
        body: { refresh_token: refreshToken }
      });
    }
  } finally {
    clearSession();
  }
}

export default api;
