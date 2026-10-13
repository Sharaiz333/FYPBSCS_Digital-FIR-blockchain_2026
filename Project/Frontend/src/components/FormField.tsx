import { ReactNode } from "react";

interface FormFieldProps {
  id: string;
  label: string;
  required?: boolean;
  hint?: string;
  error?: string;
  children: ReactNode;
}

// Label + input slot + hint + error message, laid out the same way
// everywhere. The error gets id "<id>-error" so the input can point at it
// with aria-describedby (screen readers then read the error).
export function FormField({ id, label, required, hint, error, children }: FormFieldProps) {
  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-sm font-medium text-slate-700">
        {label}
        {required && <span className="ml-0.5 text-red-600" aria-hidden="true">*</span>}
        {!required && <span className="ml-1 text-xs font-normal text-slate-400">(optional)</span>}
      </label>
      {children}
      {hint && !error && <p className="mt-1 text-xs text-slate-400">{hint}</p>}
      {error && (
        <p id={`${id}-error`} className="mt-1 text-xs text-red-600" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

export function inputClasses(hasError: boolean): string {
  const base =
    "w-full rounded-lg border bg-white px-3.5 py-2.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:ring-2";
  return hasError
    ? `${base} border-red-400 focus:border-red-500 focus:ring-red-500/20`
    : `${base} border-slate-300 focus:border-accent-600 focus:ring-accent-600/20`;
}