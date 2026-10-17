import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Navbar } from "./components/Navbar";
import Login from "./pages/Login";
import { DashboardPage } from "./pages/Dashboard";
import { ComplaintNewPage } from "./pages/ComplaintNew";
import Register from "./pages/Register";
import { VerificationQueuePage } from "./pages/VerificationQueue";

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
    </div>
  );
}

function AppRoutes() {
  const { auth } = useAuth();
  return (
    <Routes>
      <Route path="/login" element={auth ? <Navigate to="/" replace /> : <Login />} />
      <Route
  path="/register"
  element={auth ? <Navigate to="/" replace /> : <Register />}
/>
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout>
              <DashboardPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/complaints/new"
        element={
          <ProtectedRoute allowedRoles={["citizen", "police_officer"]}>
            <Layout>
              <ComplaintNewPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
  path="/verification"
  element={
    <ProtectedRoute
      allowedRoles={["police_officer", "supervisory_officer"]}
    >
      <Layout>
        <VerificationQueuePage />
      </Layout>
    </ProtectedRoute>
  }
/>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}