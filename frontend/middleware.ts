import { type NextRequest, NextResponse } from "next/server";

import { createSupabaseMiddlewareClient } from "@/lib/auth/middleware-client";
import { getDefaultPage, getRoleFromSession } from "@/lib/auth/roles";

export async function middleware(request: NextRequest) {
  const response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  });

  const supabase = createSupabaseMiddlewareClient(request, response);

  const {
    data: { session },
  } = await supabase.auth.getSession();

  const { pathname } = request.nextUrl;
  if (pathname === "/reset-password") {
    return response;
  }

  const isAuthRoute =
    pathname === "/login" ||
    pathname === "/register" ||
    pathname === "/forgot-password";
  const isAdminRoute = pathname.startsWith("/admin");
  const isUserFacingRoute =
    pathname.startsWith("/properties") ||
    pathname.startsWith("/search") ||
    pathname.startsWith("/favorites");

  if (!session && !isAuthRoute) {
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = "/login";
    redirectUrl.search = "";
    redirectUrl.searchParams.set("redirectTo", `${pathname}${request.nextUrl.search}`);

    return NextResponse.redirect(redirectUrl);
  }

  if (session && isAuthRoute) {
    const role = getRoleFromSession(session);
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = getDefaultPage(role);
    redirectUrl.search = "";

    return NextResponse.redirect(redirectUrl);
  }

  if (session) {
    const role = getRoleFromSession(session);

    if (role === "admin" && isUserFacingRoute) {
      const redirectUrl = request.nextUrl.clone();
      redirectUrl.pathname = "/admin/properties";
      redirectUrl.search = "";

      return NextResponse.redirect(redirectUrl);
    }

    if (role !== "admin" && isAdminRoute) {
      const redirectUrl = request.nextUrl.clone();
      redirectUrl.pathname = "/properties";
      redirectUrl.search = "";

      return NextResponse.redirect(redirectUrl);
    }
  }

  return response;
}

export const config = {
  matcher: "/((?!_next/static|_next/image|favicon.ico).*)",
};
