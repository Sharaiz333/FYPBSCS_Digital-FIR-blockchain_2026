import { createContext, ReactNode, useContext, useState } from "react";

export type RoleName =
  | "citizen"
  | "police_officer"
  | "investigating_officer"
  | "supervisory_officer"
  | "audit_review_officer"
  | "admin";

interface MockAuthState {
  fullName: string;
  role: RoleName;
}

interface AuthContextValue {
  auth: MockAuthState | null;
  login: (fullName: string, role: RoleName) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<MockAuthState | null>(null);

  function login(fullName: string, role: RoleName) {
    setAuth({ fullName, role });
  }

  function logout() {
    setAuth(null);
  }

  return <AuthContext.Provider value={{ auth, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}