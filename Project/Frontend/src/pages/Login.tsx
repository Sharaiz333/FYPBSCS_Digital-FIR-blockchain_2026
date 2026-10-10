import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth, RoleName } from "../context/MockAuthContext";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Temporary test role selector
  const [mockRole, setMockRole] = useState<RoleName>("citizen");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      login(email || "Test User", mockRole);
      navigate("/");
    }, 500);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md rounded-xl bg-white p-8 shadow-sm">
        <h2 className="text-2xl font-bold text-navy-900">Login to Digital FIR</h2>
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">Email or Username</label>
            <input
              type="text"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm"
              placeholder="Enter username"
              required
            />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">Password</label>
            <input
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm"
              placeholder="Enter password"
              required
            />
          </div>

          {/* Temporary Role Selector */}
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              (Temporary) Test as role
            </label>
            <select
              value={mockRole}
              onChange={(e) => setMockRole(e.target.value as RoleName)}
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm"
            >
              <option value="citizen">Citizen</option>
              <option value="police_officer">Police Officer</option>
              <option value="investigating_officer">Investigating Officer</option>
              <option value="supervisory_officer">Supervisory Officer</option>
              <option value="audit_review_officer">Audit/Review Officer</option>
              <option value="admin">Administrator</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-lg bg-navy-900 py-2.5 text-white font-medium hover:bg-navy-800 transition-colors"
          >
            {isSubmitting ? "Logging in..." : "Log In"}
          </button>
        </form>
      </div>
    </div>
  );
}