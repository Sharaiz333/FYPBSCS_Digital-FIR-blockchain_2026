import { api, AUTH_STORAGE_KEY } from "./api";
import { AuthState } from "../types/auth";

export async function loginRequest(username: string, password: string): Promise<AuthState> {
  const { data } = await api.post("/auth/login", { username, password });
  const auth: AuthState = {
    accessToken: data.access_token,
    userId: data.user_id,
    fullName: data.full_name,
    role: data.role,
  };
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(auth));
  return auth;
}

export function logoutRequest(): void {
  localStorage.removeItem(AUTH_STORAGE_KEY);
}

export function getStoredAuth(): AuthState | null {
  const raw = localStorage.getItem(AUTH_STORAGE_KEY);
  return raw ? (JSON.parse(raw) as AuthState) : null;
}