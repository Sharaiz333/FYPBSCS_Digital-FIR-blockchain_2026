import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/MockAuthContext";

const ROLE_LABELS: Record<string, string> = {
  citizen: "Citizen",
  police_officer: "Police Officer",
  investigating_officer: "Investigating Officer",
  supervisory_officer: "Supervisory Officer",
  audit_review_officer: "Audit/Review Officer",
  admin: "System Administrator",
};

export function Navbar() {
  const { auth, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  if (!auth) return null;

  return (
    <header className="bg-navy-900 text-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <span className="text-lg font-semibold tracking-wide">
          Digital FIR <span className="text-accent-600">•</span> Pakistan Police
        </span>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-slate-300">
            {auth.fullName} <span className="text-slate-400">({ROLE_LABELS[auth.role]})</span>
          </span>
          <button
            onClick={handleLogout}
            className="rounded bg-navy-700 px-3 py-1.5 hover:bg-navy-800 transition-colors"
          >
            Log out
          </button>
        </div>
      </div>
    </header>
  );
}