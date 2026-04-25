import { getAccessToken } from "@/lib/auth/session";
import type { UserRead } from "@/types/auth";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getMe(): Promise<UserRead> {
  const accessToken = await getAccessToken();

  if (!accessToken) {
    throw new Error("No active session");
  }

  const res = await fetch(`${apiUrl}/api/v1/auth/me`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!res.ok) {
    throw new Error(`HTTP ${res.status} ${res.statusText}`);
  }

  return res.json() as Promise<UserRead>;
}

export const authApi = {
  getMe,
};
