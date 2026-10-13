import { ComplaintFormErrors, ComplaintFormValues } from "../types/complaint";

const CNIC_PATTERN = /^\d{5}-\d{7}-\d$/; // 12345-1234567-1
const PHONE_PATTERN = /^03\d{2}-?\d{7}$/; // 0300-1234567 or 03001234567

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