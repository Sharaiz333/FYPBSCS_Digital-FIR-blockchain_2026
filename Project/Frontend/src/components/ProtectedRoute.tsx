import { Navigate } from "react-router-dom";
import { ReactNode } from "react";
import { useAuth } from "../context/AuthContext";
import { RoleName } from "../types/auth";

interface ProtectedRouteProps {
  children: ReactNode;
  allowedRoles?: RoleName[]; // omit to allow any logged-in user
}

// Client-side gate for navigation and UX only. The backend enforces the
// same rules on every API call; a hidden page is never a security measure.
export function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { auth } = useAuth();

  if (!auth) {
    return <Navigate to="/login" replace />;
  }
  if (allowedRoles && !allowedRoles.includes(auth.role)) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
}