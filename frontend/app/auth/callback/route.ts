import { NextResponse, type NextRequest } from "next/server";

export async function GET(request: NextRequest) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  const next = searchParams.get("next") ?? "/reset-password";

  if (code) {
    const redirectUrl = new URL(next, origin);
    redirectUrl.searchParams.set("code", code);
    return NextResponse.redirect(redirectUrl);
  }

  return NextResponse.redirect(new URL("/login", origin));
}
