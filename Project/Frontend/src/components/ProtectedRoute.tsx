import { Navigate } from "react-router-dom";
import { ReactNode } from "react";
import { useAuth } from "../context/MockAuthContext";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { auth } = useAuth();

  if (!auth) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}