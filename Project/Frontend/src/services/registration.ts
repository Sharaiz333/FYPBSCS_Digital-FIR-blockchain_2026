import { api } from "./api";
import { PendingCitizen, RegisterValues } from "../types/registration";

// Public endpoint: no token needed. Returns the server's message.
export async function registerCitizen(values: RegisterValues): Promise<string> {
  const { data } = await api.post("/auth/register", {
    full_name: values.fullName.trim(),
    username: values.username.trim(),
    email: values.email.trim() || undefined,
    password: values.password,
    cnic: values.cnic.trim(),
    phone: values.phone.trim(),
    address: values.address.trim() || undefined,
  });
  return data.message as string;
}

export async function fetchCitizensForVerification(): Promise<PendingCitizen[]> {
  const { data } = await api.get<PendingCitizen[]>("/verification/citizens");
  return data;
}

export async function decideCitizen(userId: string, approve: boolean, reason?: string): Promise<void> {
  await api.post(`/verification/citizens/${userId}`, { approve, reason });
}

// The backend sends a readable string in "detail" for the errors we expect.
export function errorDetail(err: unknown, fallback: string): string {
  const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
  return typeof detail === "string" ? detail : fallback;
}