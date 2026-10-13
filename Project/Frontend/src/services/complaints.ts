import { ComplaintFormValues, ComplaintSubmitResult } from "../types/complaint";

// TEMPORARY MOCK. Nothing is sent anywhere and nothing is saved.
// When the backend Complaint endpoint exists, only the body of
// submitComplaint changes (to an api.post call). The page that calls it
// stays the same, and COMPLAINT_SERVICE_IS_MOCK is deleted together with
// the "demo mode" banner that uses it.
export const COMPLAINT_SERVICE_IS_MOCK = true;

export async function submitComplaint(_values: ComplaintFormValues): Promise<ComplaintSubmitResult> {
  await new Promise((resolve) => setTimeout(resolve, 800));
  const suffix = Math.floor(10000 + Math.random() * 90000);
  return { referenceNumber: `CMP-${new Date().getFullYear()}-${suffix}` };
}