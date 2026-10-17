export interface RegisterValues {
  fullName: string;
  username: string;
  email: string; // optional
  password: string;
  confirmPassword: string;
  cnic: string;
  phone: string;
  address: string; // optional
}

export type RegisterErrors = Partial<Record<keyof RegisterValues, string>>;

// What an officer sees in the verification queue (matches the backend's
// PendingCitizenRead schema).
export interface PendingCitizen {
  user_id: string;
  full_name: string;
  username: string;
  email: string | null;
  cnic: string | null;
  phone: string | null;
  address: string | null;
  verification_status: "pending" | "verified" | "rejected";
  created_at: string;
  verified_at: string | null;
  rejection_reason: string | null;
}