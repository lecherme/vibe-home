"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { signOut } from "@/lib/auth/session";

export function NavBar() {
  const router = useRouter();

  const handleSignOut = async () => {
    try {
      await signOut();
      router.refresh();
      router.push("/login");
    } catch (error) {
      console.error("Sign out failed", error);
    }
  };

  return (
    <nav className="border-b border-slate-200 bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center">
            <Link href="/properties" className="text-xl font-bold text-slate-900">
              VibeHome
            </Link>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={handleSignOut}
              className="rounded-md px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-900"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
