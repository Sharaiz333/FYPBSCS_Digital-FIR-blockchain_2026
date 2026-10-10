import { useAuth } from "../context/MockAuthContext";

const ROLE_DESCRIPTIONS: Record<string, string> = {
  citizen: "You'll be able to submit complaints and track their status here.",
  police_officer: "Station complaints and FIR intake will appear here.",
  investigating_officer: "Your assigned cases and investigation timeline will appear here.",
  supervisory_officer: "FIRs awaiting review/assignment and oversight tools will appear here.",
  audit_review_officer: "Read-only audit trail and blockchain history views will appear here.",
  admin: "User management and system administration will appear here.",
};

export function DashboardPage() {
  const { auth } = useAuth();

  if (!auth) return null;

  return (
    <div className="rounded-lg bg-white p-6 shadow-sm">
      <h1 className="text-xl font-semibold text-navy-900">Welcome, {auth.fullName}</h1>
      <p className="mt-2 text-sm text-slate-500">{ROLE_DESCRIPTIONS[auth.role]}</p>
      <p className="mt-6 rounded bg-amber-50 p-3 text-xs text-amber-700">
        This is a placeholder dashboard (Stage 3). Real FIR lists, forms, and role-specific
        content are built in later stages, once the frontend is connected to the backend.
      </p>
    </div>
  );
}