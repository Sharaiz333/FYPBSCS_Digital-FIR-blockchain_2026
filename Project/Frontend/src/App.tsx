import { useEffect, useState } from "react";

export default function App() {
  const [backendStatus, setBackendStatus] = useState<"checking" | "ok" | "unreachable">("checking");

  useEffect(() => {
    const baseUrl = import.meta.env.VITE_API_BASE_URL;
    fetch(`${baseUrl}/health`)
      .then((res) => (res.ok ? setBackendStatus("ok") : setBackendStatus("unreachable")))
      .catch(() => setBackendStatus("unreachable"));
  }, []);

  return (
    <div className="flex min-h-screen items-center justify-center bg-navy-950">
      <div className="rounded-lg bg-white p-8 text-center shadow-xl">
        <h1 className="text-xl font-semibold text-navy-900">Digital FIR Management System</h1>
        <p className="mt-2 text-sm text-slate-500">Frontend skeleton — Stage 1</p>
        <p className="mt-4 text-sm">
          Backend status:{" "}
          <span
            className={
              backendStatus === "ok"
                ? "font-medium text-green-600"
                : backendStatus === "unreachable"
                ? "font-medium text-red-600"
                : "text-slate-400"
            }
          >
            {backendStatus}
          </span>
        </p>
      </div>
    </div>
  );
}