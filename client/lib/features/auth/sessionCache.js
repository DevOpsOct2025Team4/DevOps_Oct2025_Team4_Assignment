const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";
const USER_KEY = "user";

let cachedSession = null;
let cachedUser = null;

export function getCachedSession() {
  return cachedSession;
}

export function hydrateSessionFromStorage() {
  if (cachedSession) {
    return cachedSession;
  }

  const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);

  if (!accessToken && !refreshToken) {
    cachedSession = null;
    return null;
  }

  cachedSession = {
    access_token: accessToken || null,
    refresh_token: refreshToken || null
  };

  return cachedSession;
}

export function setCachedSession(session) {
  cachedSession = session
    ? {
        access_token: session.access_token || null,
        refresh_token: session.refresh_token || null
      }
    : null;

  if (session?.access_token) {
    localStorage.setItem(ACCESS_TOKEN_KEY, session.access_token);
  } else {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
  }

  if (session?.refresh_token) {
    localStorage.setItem(REFRESH_TOKEN_KEY, session.refresh_token);
  } else {
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }
}

export function clearCachedSession() {
  cachedSession = null;
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function getCachedUser() {
  return cachedUser;
}

export function hydrateUserFromStorage() {
  if (cachedUser) {
    return cachedUser;
  }

  const rawUser = localStorage.getItem(USER_KEY);
  if (!rawUser) {
    cachedUser = null;
    return null;
  }

  try {
    cachedUser = JSON.parse(rawUser);
  } catch {
    localStorage.removeItem(USER_KEY);
    cachedUser = null;
  }

  return cachedUser;
}

export function setCachedUser(user) {
  cachedUser = user || null;
  if (user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  } else {
    localStorage.removeItem(USER_KEY);
  }
}

export function clearCachedUser() {
  cachedUser = null;
  localStorage.removeItem(USER_KEY);
}

export function clearSessionStorage() {
  clearCachedSession();
  clearCachedUser();
}
