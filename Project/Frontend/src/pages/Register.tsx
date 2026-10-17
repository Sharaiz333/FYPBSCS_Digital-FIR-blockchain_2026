import { ChangeEvent, FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { FormField, inputClasses } from "../components/FormField";
import { errorDetail, registerCitizen } from "../services/registration";
import { RegisterErrors, RegisterValues } from "../types/registration";
import { validateRegistration } from "../utils/validation";

const EMPTY_VALUES: RegisterValues = {
	fullName: "",
	username: "",
	email: "",
	password: "",
	confirmPassword: "",
	cnic: "",
	phone: "",
	address: "",
};

type FieldName = keyof RegisterValues;

export default function Register() {
	const [values, setValues] = useState(EMPTY_VALUES);
	const [touched, setTouched] = useState<Partial<Record<FieldName, boolean>>>({});
	const [submitAttempted, setSubmitAttempted] = useState(false);
	const [isSubmitting, setIsSubmitting] = useState(false);
	const [submitError, setSubmitError] = useState("");
	const [successMessage, setSuccessMessage] = useState("");
	const allErrors = validateRegistration(values);
	const visibleErrors: RegisterErrors = {};

	(Object.keys(allErrors) as FieldName[]).forEach((name) => {
		if (submitAttempted || touched[name]) visibleErrors[name] = allErrors[name];
	});

	function handleChange(event: ChangeEvent<HTMLInputElement>) {
		const { name, value } = event.target;
		setValues((current) => ({ ...current, [name]: value }));
		setSubmitError("");
	}

	function handleBlur(event: ChangeEvent<HTMLInputElement>) {
		setTouched((current) => ({ ...current, [event.target.name]: true }));
	}

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
		if (firstInvalid) {
			document.getElementById(firstInvalid)?.focus();
			return;
		}

		setIsSubmitting(true);
		try {
			setSuccessMessage(await registerCitizen(values));
		} catch (error) {
			setSubmitError(errorDetail(error, "Registration could not be completed. Please try again."));
		} finally {
			setIsSubmitting(false);
		}
	}

	return (
		<div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10">
			<div className="w-full max-w-2xl rounded-xl bg-white p-6 shadow-sm sm:p-8">
				<h1 className="text-2xl font-bold text-navy-900">Create a citizen account</h1>
				<p className="mt-2 text-sm text-slate-600">Your account will be reviewed by police before you can file a complaint.</p>
				{successMessage ? (
					<div className="mt-6" role="status">
						<p className="rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-800">{successMessage}</p>
						<Link to="/login" className="mt-5 inline-block font-medium text-accent-700 hover:underline">Go to login</Link>
					</div>
				) : (
					<form onSubmit={handleSubmit} noValidate className="mt-6 space-y-5">
						<div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
							<FormField id="fullName" label="Full name" required error={visibleErrors.fullName}>
								<input autoComplete="name" maxLength={100} {...fieldProps("fullName")} />
							</FormField>
							<FormField id="username" label="Username" required error={visibleErrors.username}>
								<input autoComplete="username" maxLength={50} {...fieldProps("username")} />
							</FormField>
							<FormField id="email" label="Email address" error={visibleErrors.email}>
								<input type="email" autoComplete="email" {...fieldProps("email")} />
							</FormField>
							<FormField id="phone" label="Mobile number" required hint="Example: 0300-1234567" error={visibleErrors.phone}>
								<input type="tel" autoComplete="tel" placeholder="0300-1234567" maxLength={12} {...fieldProps("phone")} />
							</FormField>
							<FormField id="cnic" label="CNIC" required hint="Format: 12345-1234567-1" error={visibleErrors.cnic}>
								<input inputMode="numeric" placeholder="12345-1234567-1" maxLength={15} {...fieldProps("cnic")} />
							</FormField>
							<FormField id="address" label="Address" error={visibleErrors.address}>
								<input autoComplete="street-address" maxLength={200} {...fieldProps("address")} />
							</FormField>
							<FormField id="password" label="Password" required error={visibleErrors.password}>
								<input type="password" autoComplete="new-password" {...fieldProps("password")} />
							</FormField>
							<FormField id="confirmPassword" label="Confirm password" required error={visibleErrors.confirmPassword}>
								<input type="password" autoComplete="new-password" {...fieldProps("confirmPassword")} />
							</FormField>
						</div>
						{submitError && <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">{submitError}</p>}
						<button type="submit" disabled={isSubmitting} className="w-full rounded-lg bg-navy-900 py-2.5 font-medium text-white transition-colors hover:bg-navy-800 disabled:opacity-50">
							{isSubmitting ? "Creating account..." : "Create account"}
						</button>
						<p className="text-center text-sm text-slate-600">Already registered? <Link to="/login" className="font-medium text-accent-700 hover:underline">Log in</Link></p>
					</form>
				)}
			</div>
		</div>
	);
}
