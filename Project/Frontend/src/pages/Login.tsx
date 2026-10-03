import { FormEvent, useState } from "react";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setMessage("");
    setIsSubmitting(true);

    // Temporary mock login.
    // This will be replaced with the real API call in the authentication stage.
    setTimeout(() => {
      setIsSubmitting(false);
      setMessage(
        "Login form is working. Backend authentication will be connected next."
      );
    }, 800);
  };

  return (
    <main className="min-h-screen bg-navy-950">
      <div className="flex min-h-screen flex-col lg:flex-row">
        {/* Left branding panel */}
        <section className="hidden flex-1 items-center justify-center px-10 lg:flex">
          <div className="max-w-xl text-center">
            <div className="mx-auto mb-8 flex h-24 w-24 items-center justify-center rounded-full border-2 border-accent-600 bg-navy-900">
              <span className="text-3xl font-bold text-white">FIR</span>
            </div>

            <h1 className="text-4xl font-bold tracking-tight text-white">
              Digital FIR
            </h1>

            <p className="mt-3 text-xl text-slate-300">
              Management System
            </p>

            <div className="mx-auto mt-8 h-px w-24 bg-accent-600" />

            <p className="mx-auto mt-8 max-w-md text-sm leading-7 text-slate-400">
              A secure digital platform for managing First Information Reports,
              records, investigations, and authorized users.
            </p>
          </div>
        </section>

        {/* Login panel */}
        <section className="flex min-h-screen w-full items-center justify-center bg-slate-50 px-6 py-12 lg:min-h-screen lg:w-[520px] lg:px-12">
          <div className="w-full max-w-md">
            {/* Mobile branding */}
            <div className="mb-10 text-center lg:hidden">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-navy-900">
                <span className="text-xl font-bold text-white">FIR</span>
              </div>

              <h1 className="text-2xl font-bold text-navy-900">
                Digital FIR
              </h1>

              <p className="mt-1 text-sm text-slate-500">
                Management System
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-lg sm:p-10">
              <div className="mb-8">
                <p className="text-sm font-medium uppercase tracking-wider text-accent-600">
                  Secure Access
                </p>

                <h2 className="mt-2 text-2xl font-bold text-navy-900">
                  Official Login
                </h2>

                <p className="mt-2 text-sm leading-6 text-slate-500">
                  Sign in using your authorized account credentials.
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                {/* Username */}
                <div>
                  <label
                    htmlFor="username"
                    className="mb-2 block text-sm font-medium text-slate-700"
                  >
                    Username
                  </label>

                  <input
                    id="username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    value={username}
                    onChange={(event) => setUsername(event.target.value)}
                    placeholder="Enter your username"
                    required
                    className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-accent-600 focus:ring-2 focus:ring-accent-600/20"
                  />
                </div>

                {/* Password */}
                <div>
                  <label
                    htmlFor="password"
                    className="mb-2 block text-sm font-medium text-slate-700"
                  >
                    Password
                  </label>

                  <div className="relative">
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      autoComplete="current-password"
                      value={password}
                      onChange={(event) => setPassword(event.target.value)}
                      placeholder="Enter your password"
                      required
                      className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 pr-20 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-accent-600 focus:ring-2 focus:ring-accent-600/20"
                    />

                    <button
                      type="button"
                      onClick={() =>
                        setShowPassword((current) => !current)
                      }
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-medium text-slate-500 hover:text-navy-900"
                    >
                      {showPassword ? "Hide" : "Show"}
                    </button>
                  </div>
                </div>

                {/* Submit */}
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full rounded-lg bg-accent-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-accent-700 focus:outline-none focus:ring-2 focus:ring-accent-600 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isSubmitting ? "Signing In..." : "Sign In"}
                </button>

                {/* Temporary message */}
                {message && (
                  <div
                    className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700"
                    role="status"
                  >
                    {message}
                  </div>
                )}
              </form>

              <div className="mt-8 border-t border-slate-100 pt-6">
                <p className="text-center text-xs leading-5 text-slate-400">
                  Authorized personnel only. Access to this system is
                  restricted and monitored.
                </p>
              </div>
            </div>

            <p className="mt-6 text-center text-xs text-slate-400">
              Digital FIR Management System © 2026
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}
