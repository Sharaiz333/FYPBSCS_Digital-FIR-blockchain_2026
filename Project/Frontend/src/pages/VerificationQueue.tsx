import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { decideCitizen, errorDetail, fetchCitizensForVerification } from "../services/registration";
import { PendingCitizen } from "../types/registration";

type PendingAction = { id: string; type: "approve" | "reject" };

export function VerificationQueuePage() {
  const [citizens, setCitizens] = useState<PendingCitizen[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [action, setAction] = useState<PendingAction | null>(null);
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [rowError, setRowError] = useState("");
  const [notice, setNotice] = useState("");

  async function load() {
    setLoading(true);
    setLoadError("");
    try {
      setCitizens(await fetchCitizensForVerification());
    } catch (err) {
      setLoadError(errorDetail(err, "Could not load the verification queue."));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function startAction(id: string, type: "approve" | "reject") {
    setAction({ id, type });
    setReason("");
    setRowError("");
  }

  async function confirmAction() {
    if (!action) return;
    if (action.type === "reject" && !reason.trim()) {
      setRowError("Enter a reason for rejecting this registration.");
      return;
    }
    setBusy(true);
    setRowError("");
    try {
      await decideCitizen(action.id, action.type === "approve", reason.trim() || undefined);
      const person = citizens.find((c) => c.user_id === action.id);
      setNotice(`${person?.full_name ?? "Citizen"} was ${action.type === "approve" ? "approved" : "rejected"}.`);
      setAction(null);
      await load();
    } catch (err) {
      setRowError(errorDetail(err, "The decision could not be saved. Please try again."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold text-navy-900">Citizen verification</h1>
          <p className="mt-1 text-sm text-slate-500">
            Compare each registration with the person's original CNIC before approving.
          </p>
        </div>
        <Link to="/" className="text-sm text-accent-600 hover:underline">
          ← Dashboard
        </Link>
      </div>

      {notice && (
        <p className="mb-4 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700" role="status">
          {notice}
        </p>
      )}
      {loadError && (
        <p className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">
          {loadError}
        </p>
      )}
      {loading && <p className="text-sm text-slate-500">Loading…</p>}
      {!loading && !loadError && citizens.length === 0 && (
        <p className="rounded-lg bg-white p-6 text-sm text-slate-500 shadow-sm">No registrations are waiting for verification.</p>
      )}

      <ul className="space-y-4">
        {citizens.map((citizen) => {
          const isActive = action?.id === citizen.user_id;
          return (
            <li key={citizen.user_id} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="font-semibold text-navy-900">{citizen.full_name}</p>
                  <p className="text-xs text-slate-400">
                    @{citizen.username} · registered {new Date(citizen.created_at).toLocaleString()}
                  </p>
                </div>
                {!isActive && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => startAction(citizen.user_id, "approve")}
                      className="rounded-lg bg-navy-800 px-3 py-1.5 text-sm font-medium text-white hover:bg-navy-900"
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => startAction(citizen.user_id, "reject")}
                      className="rounded-lg border border-red-300 px-3 py-1.5 text-sm font-medium text-red-700 hover:bg-red-50"
                    >
                      Reject
                    </button>
                  </div>
                )}
              </div>

              <dl className="mt-4 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
                <div>
                  <dt className="text-xs uppercase text-slate-400">CNIC</dt>
                  <dd className="font-mono text-slate-800">{citizen.cnic}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase text-slate-400">Mobile</dt>
                  <dd className="text-slate-800">{citizen.phone}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase text-slate-400">Address</dt>
                  <dd className="text-slate-800">{citizen.address || "—"}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase text-slate-400">Email</dt>
                  <dd className="text-slate-800">{citizen.email || "—"}</dd>
                </div>
              </dl>

              {isActive && action && (
                <div className="mt-4 rounded-lg bg-slate-50 p-4">
                  {action.type === "approve" ? (
                    <p className="text-sm text-slate-700">
                      Confirm that you have checked this person's <strong>original CNIC</strong> and the details above
                      match. They will be able to log in immediately.
                    </p>
                  ) : (
                    <div>
                      <label htmlFor="reject-reason" className="mb-1.5 block text-sm font-medium text-slate-700">
                        Reason for rejection
                      </label>
                      <input
                        id="reject-reason"
                        value={reason}
                        onChange={(event) => setReason(event.target.value)}
                        maxLength={300}
                        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-accent-600 focus:ring-2 focus:ring-accent-600/20"
                      />
                    </div>
                  )}
                  {rowError && (
                    <p className="mt-2 text-sm text-red-600" role="alert">
                      {rowError}
                    </p>
                  )}
                  <div className="mt-3 flex gap-2">
                    <button
                      onClick={confirmAction}
                      disabled={busy}
                      className={`rounded-lg px-4 py-2 text-sm font-medium text-white disabled:opacity-60 ${
                        action.type === "approve" ? "bg-navy-800 hover:bg-navy-900" : "bg-red-600 hover:bg-red-700"
                      }`}
                    >
                      {busy ? "Saving…" : action.type === "approve" ? "Confirm approval" : "Confirm rejection"}
                    </button>
                    <button
                      onClick={() => setAction(null)}
                      disabled={busy}
                      className="rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-700 hover:bg-white"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}