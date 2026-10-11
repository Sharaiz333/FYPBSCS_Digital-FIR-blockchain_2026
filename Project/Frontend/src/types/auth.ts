export type RoleName =
  | "citizen"
  | "police_officer"
  | "investigating_officer"
  | "supervisory_officer"
  | "audit_review_officer"
  | "admin";

export interface AuthState {
  accessToken: string;
  userId: string;
  fullName: string;
  role: RoleName;
}