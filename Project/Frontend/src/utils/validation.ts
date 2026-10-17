import { ComplaintFormErrors, ComplaintFormValues } from "../types/complaint";
import { RegisterErrors, RegisterValues } from "../types/registration";

export const CNIC_PATTERN = /^\d{5}-\d{7}-\d$/;
export const PHONE_PATTERN = /^03\d{2}-?\d{7}$/;

// Client-side validation is for fast feedback only. The backend must
// validate everything again, because anyone can bypass the browser.
export function validateComplaint(values: ComplaintFormValues): ComplaintFormErrors {
  const errors: ComplaintFormErrors = {};

  if (!values.stationId) errors.stationId = "Select the police station.";
  if (!values.crimeCategory) errors.crimeCategory = "Select a crime category.";

  if (!values.incidentDateTime) {
    errors.incidentDateTime = "Enter when the incident happened.";
  } else if (new Date(values.incidentDateTime).getTime() > Date.now()) {
    errors.incidentDateTime = "The incident date and time cannot be in the future.";
  }

  if (values.incidentLocation.trim().length < 5) {
    errors.incidentLocation = "Enter where the incident happened (at least 5 characters).";
  }
  if (values.description.trim().length < 20) {
    errors.description = "Describe the incident in at least 20 characters.";
  }

  if (values.complainantName.trim().length < 2) {
    errors.complainantName = "Enter your full name.";
  }
  if (!CNIC_PATTERN.test(values.complainantCnic.trim())) {
    errors.complainantCnic = "Use the format 12345-1234567-1.";
  }
  if (!PHONE_PATTERN.test(values.complainantPhone.trim())) {
    errors.complainantPhone = "Enter a mobile number like 0300-1234567.";
  }

  return errors;
}

// Current local time formatted for <input type="datetime-local" max=...>
export function currentDateTimeLocal(): string {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  return now.toISOString().slice(0, 16);
}

const USERNAME_PATTERN = /^[A-Za-z0-9_.-]{3,50}$/;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function validateRegistration(values: RegisterValues): RegisterErrors {
  const errors: RegisterErrors = {};

  if (values.fullName.trim().length < 2) {
    errors.fullName = "Enter your full name.";
  }

  if (!USERNAME_PATTERN.test(values.username)) {
    errors.username = "3-50 characters: letters, numbers, dot, dash or underscore.";
  }

  if (values.email.trim() && !EMAIL_PATTERN.test(values.email.trim())) {
    errors.email = "Enter a valid email address, or leave it empty.";
  }

  if (values.password.length < 8) {
    errors.password = "Use at least 8 characters.";
  }

  if (values.confirmPassword !== values.password) {
    errors.confirmPassword = "The passwords do not match.";
  }

  if (!CNIC_PATTERN.test(values.cnic.trim())) {
    errors.cnic = "Use the format 12345-1234567-1.";
  }

  if (!PHONE_PATTERN.test(values.phone.trim())) {
    errors.phone = "Enter a mobile number like 0300-1234567.";
  }

  return errors;
}