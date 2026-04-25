export type AppRole = "user" | "admin";

export interface UserRead {
  id: string;
  email: string;
  role: AppRole;
}
