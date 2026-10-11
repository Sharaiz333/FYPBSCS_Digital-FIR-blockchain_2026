import { createContext, ReactNode, useContext, useState } from "react";
import { AuthState } from "../types/auth";
import { getStoredAuth, loginRequest, logoutRequest } from "../services/auth";

interface AuthContextValue {
  auth: AuthState | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<AuthState | null>(getStoredAuth());

  async function login(username: string, password: string) {
    setAuth(await loginRequest(username, password));
  }

  function logout() {
    logoutRequest();
    setAuth(null);
  }

  return <AuthContext.Provider value={{ auth, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}