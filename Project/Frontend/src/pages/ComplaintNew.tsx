import { ChangeEvent, FormEvent, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { FormField, inputClasses } from "../components/FormField";
import { CRIME_CATEGORIES } from "../constants/complaintOptions";
import { MOCK_STATIONS } from "../mock/stations";
import { COMPLAINT_SERVICE_IS_MOCK, submitComplaint } from "../services/complaints";
import { ComplaintFormErrors, ComplaintFormValues } from "../types/complaint";
import { currentDateTimeLocal, validateComplaint } from "../utils/validation";

type FieldName = keyof ComplaintFormValues;

const EMPTY_VALUES: ComplaintFormValues = {
  stationId: "",
  crimeCategory: "",
  incidentDateTime: "",
  incidentLocation: "",
  description: "",
  suspectDetails: "",
  witnessDetails: "",
  complainantName: "",
  complainantCnic: "",
  complainantPhone: "",
  complainantAddress: "",
};

export function ComplaintNewPage() {
  const { auth } = useAuth();
  const isOfficer = auth?.role === "police_officer";
  const defaultName = isOfficer ? "" : auth?.fullName ?? "";
    const [values, setValues] = useState<ComplaintFormValues>({
    ...EMPTY_VALUES,
    complainantName: defaultName,
  });
  const [touched, setTouched] = useState<Partial<Record<FieldName, boolean>>>({});
  const [declared, setDeclared] = useState(false);
  const [submitAttempted, setSubmitAttempted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [referenceNumber, setReferenceNumber] = useState("");

  // Errors are always calculated from the current values. They are only
  // SHOWN for fields the user has left, or for every field after a submit
  // attempt, so people aren't shouted at while still typing.
  const allErrors = useMemo(() => validateComplaint(values), [values]);
  const visibleErrors: ComplaintFormErrors = {};
  (Object.keys(allErrors) as FieldName[]).forEach((name) => {
    if (submitAttempted || touched[name]) visibleErrors[name] = allErrors[name];
  });
  const declarationError = submitAttempted && !declared ? "You must confirm the declaration to submit." : "";

  function handleChange(event: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) {
    const { name, value } = event.target;
    setValues((current) => ({ ...current, [name]: value }));
  }

  function handleBlur(event: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) {
    setTouched((current) => ({ ...current, [event.target.name]: true }));
  }

  // Props shared by every input: wiring, accessibility and error styling.
  function fieldProps(name: FieldName) {
    const hasError = Boolean(visibleErrors[name]);
    return {
      id: name,
      name,
      value: values[name],
      onChange: handleChange,
      onBlur: handleBlur,
      "aria-invalid": hasError,
      "aria-describedby": hasError ? `${name}-error` : undefined,
      className: inputClasses(hasError),
    };
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitAttempted(true);
    setSubmitError("");

    const firstInvalid = (Object.keys(allErrors) as FieldName[])[0];
    if (firstInvalid || !declared) {
      // Move the keyboard focus to the first problem.
      if (firstInvalid) document.getElementById(firstInvalid)?.focus();
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await submitComplaint(values);
      setReferenceNumber(result.referenceNumber);
    } catch {
      setSubmitError("Your complaint could not be submitted. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function fileAnother() {
    setValues({ ...EMPTY_VALUES, complainantName: defaultName });
    setTouched({});
    setDeclared(false);
    setSubmitAttempted(false);
    setReferenceNumber("");
  }

  // ---- Success screen ----
  if (referenceNumber) {
    return (
      <div className="mx-auto max-w-xl rounded-xl bg-white p-8 text-center shadow-sm">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 text-xl text-green-700">
          ✓
        </div>
 <h1 className="text-xl font-semibold text-navy-900">
  {isOfficer ? "Register Walk-in Complaint" : "File a Complaint"}
</h1>
<p className="mt-1 text-sm text-slate-500">
  {isOfficer
    ? "Record a complaint on behalf of a citizen visiting the police station."
    : "Provide accurate details. Police will review your complaint before an FIR is created."}
</p>
        {COMPLAINT_SERVICE_IS_MOCK && (
          <p className="mt-4 rounded bg-amber-50 p-3 text-xs text-amber-700">
            Demo mode: this complaint was NOT saved anywhere. Saving is added when the backend is connected.
          </p>
        )}
        <div className="mt-6 flex justify-center gap-3">
          <Link to="/" className="rounded-lg bg-navy-800 px-4 py-2 text-sm font-medium text-white hover:bg-navy-900">
            Back to dashboard
          </Link>
          <button
            type="button"
            onClick={fileAnother}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            File another complaint
          </button>
        </div>
      </div>
    );
  }

  // ---- Form ----
  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-navy-900">File a Complaint</h1>
        <p className="mt-1 text-sm text-slate-500">
          Provide accurate details. Police will review your complaint before an FIR is created.
        </p>
      </div>

      {COMPLAINT_SERVICE_IS_MOCK && (
        <p className="mb-4 rounded bg-amber-50 p-3 text-xs text-amber-700">
          Demo mode: submissions are not saved yet. Use synthetic data only, never real CNICs or personal details.
        </p>
      )}

      <form onSubmit={handleSubmit} noValidate className="space-y-6">
        {/* Incident details */}
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-1 text-base font-semibold text-navy-900">
  {isOfficer ? "Citizen / Complainant Details" : "Your details"}
</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <FormField id="stationId" label="Police station" required error={visibleErrors.stationId}>
              <select {...fieldProps("stationId")}>
                <option value="">Select a station…</option>
                {MOCK_STATIONS.map((station) => (
                  <option key={station.id} value={station.id}>
                    {station.name} ({station.location})
                  </option>
                ))}
              </select>
            </FormField>

            <FormField id="crimeCategory" label="Crime category" required error={visibleErrors.crimeCategory}>
              <select {...fieldProps("crimeCategory")}>
                <option value="">Select a category…</option>
                {CRIME_CATEGORIES.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
            </FormField>

            <FormField id="incidentDateTime" label="Date and time of incident" required error={visibleErrors.incidentDateTime}>
              <input type="datetime-local" max={currentDateTimeLocal()} {...fieldProps("incidentDateTime")} />
            </FormField>

            <FormField id="incidentLocation" label="Location of incident" required error={visibleErrors.incidentLocation}>
              <input type="text" placeholder="Street, area, city" maxLength={200} {...fieldProps("incidentLocation")} />
            </FormField>
          </div>

          <div className="mt-4">
            <FormField
              id="description"
              label="What happened?"
              required
              hint={`${values.description.length}/2000 characters`}
              error={visibleErrors.description}
            >
              <textarea
                rows={5}
                maxLength={2000}
                placeholder="Describe the incident in your own words."
                {...fieldProps("description")}
              />
            </FormField>
          </div>
        </section>

        {/* Complainant details */}
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-1 text-base font-semibold text-navy-900">Your details</h2>
          <p className="mb-4 text-xs text-slate-400">
            Stored securely off-chain. Personal details are never written to the blockchain.
          </p>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <FormField id="complainantName" label="Full name" required error={visibleErrors.complainantName}>
              <input type="text" autoComplete="name" maxLength={100} {...fieldProps("complainantName")} />
            </FormField>

            <FormField id="complainantCnic" label="CNIC" required hint="Format: 12345-1234567-1" error={visibleErrors.complainantCnic}>
              <input type="text" inputMode="numeric" placeholder="12345-1234567-1" maxLength={15} {...fieldProps("complainantCnic")} />
            </FormField>

            <FormField id="complainantPhone" label="Mobile number" required hint="Example: 0300-1234567" error={visibleErrors.complainantPhone}>
              <input type="tel" autoComplete="tel" placeholder="0300-1234567" maxLength={12} {...fieldProps("complainantPhone")} />
            </FormField>

            <FormField id="complainantAddress" label="Address">
              <input type="text" autoComplete="street-address" maxLength={200} {...fieldProps("complainantAddress")} />
            </FormField>
          </div>
        </section>

        {/* Optional information */}
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-base font-semibold text-navy-900">Additional information</h2>
          <div className="space-y-4">
            <FormField id="suspectDetails" label="Suspect details" hint="Name, description or anything that helps identify them.">
              <textarea rows={3} maxLength={1000} {...fieldProps("suspectDetails")} />
            </FormField>
            <FormField id="witnessDetails" label="Witness details" hint="Anyone who saw what happened and can be contacted.">
              <textarea rows={3} maxLength={1000} {...fieldProps("witnessDetails")} />
            </FormField>
          </div>
        </section>

        {/* Declaration */}
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <label className="flex items-start gap-3 text-sm text-slate-700">
            <input
              type="checkbox"
              checked={declared}
              onChange={(event) => setDeclared(event.target.checked)}
              aria-invalid={Boolean(declarationError)}
              aria-describedby={declarationError ? "declaration-error" : undefined}
              className="mt-0.5 h-4 w-4 rounded border-slate-300 text-accent-600 focus:ring-accent-600"
            />
            <span>
              {isOfficer
  ? "I confirm that I have recorded the citizen's statement accurately and that the information provided is true to the best of my knowledge."
  : "I confirm that the information above is true to the best of my knowledge. I understand that giving false information to the police is an offence."}
            </span>
          </label>
          {declarationError && (
            <p id="declaration-error" className="mt-2 text-xs text-red-600" role="alert">
              {declarationError}
            </p>
          )}
        </section>

        {submitError && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">
            {submitError}
          </div>
        )}

        <div className="flex items-center justify-end gap-3">
          <Link to="/" className="rounded-lg border border-slate-300 px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50">
            Cancel
          </Link>
          <button
            type="submit"
            disabled={isSubmitting}
            className="rounded-lg bg-accent-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-accent-700 focus:outline-none focus:ring-2 focus:ring-accent-600 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? "Submitting…" : "Submit complaint"}
          </button>
        </div>
      </form>
    </div>
  );
}