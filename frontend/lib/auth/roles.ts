import type { Session } from "@supabase/supabase-js";

export type AppRole = "user" | "admin";

interface JwtPayload {
  app_role?: unknown;
  app_metadata?: {
    app_role?: unknown;
  };
}

function isAppRole(value: unknown): value is AppRole {
  return value === "user" || value === "admin";
}

function decodeJwtPayload(token: string): JwtPayload | null {
  const [, payload] = token.split(".");

  if (!payload) {
    return null;
  }

  try {
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "=");
    const binary = atob(padded);
    const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0));

    return JSON.parse(new TextDecoder().decode(bytes)) as JwtPayload;
  } catch {
    return null;
  }
}

export function getRoleFromJwt(token: string | null | undefined): AppRole {
  if (!token) {
    return "user";
  }

  const payload = decodeJwtPayload(token);
  const role = payload?.app_role ?? payload?.app_metadata?.app_role;

  return isAppRole(role) ? role : "user";
}

export function getRoleFromSession(session: Session | null | undefined): AppRole {
  return getRoleFromJwt(session?.access_token);
}

export function getDefaultPage(role: AppRole): string {
  return role === "admin" ? "/admin/properties" : "/properties";
}

export function sanitizeRedirectTo(raw: string | null | undefined): string | null {
  if (!raw || raw === "/" || !raw.startsWith("/") || raw.startsWith("//")) {
    return null;
  }

  return raw;
}
