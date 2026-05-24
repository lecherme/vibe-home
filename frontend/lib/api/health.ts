import { apiUrl } from "@/lib/api/config";
import type { HealthResponse } from "@/types/health";

export async function getHealthStatus(): Promise<HealthResponse> {
  const res = await fetch(`${apiUrl}/health`);
  if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);
  return res.json() as Promise<HealthResponse>;
}
