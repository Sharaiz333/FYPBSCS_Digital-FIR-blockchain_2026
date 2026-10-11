import axios from "axios";

export const AUTH_STORAGE_KEY = "digitalfir_auth";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

// Attach the token to every request.
api.interceptors.request.use((config) => {
  const raw = localStorage.getItem(AUTH_STORAGE_KEY);
  if (raw) {
    const { accessToken } = JSON.parse(raw);
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// An expired or invalid token sends the user back to login. The login
// request itself is excluded, otherwise a wrong password would reload the page.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLoginCall = error.config?.url?.includes("/auth/login");
    if (error.response?.status === 401 && !isLoginCall) {
      localStorage.removeItem(AUTH_STORAGE_KEY);
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);