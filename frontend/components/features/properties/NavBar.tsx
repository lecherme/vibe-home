"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type { AppRole } from "@/lib/auth/roles";
import { signOut } from "@/lib/auth/session";

interface NavBarProps {
  role: AppRole;
}

export function NavBar({ role }: NavBarProps) {
  const router = useRouter();
  const homeHref = role === "admin" ? "/admin/properties" : "/properties";
  const links =
    role === "admin"
      ? [{ href: "/admin/properties", label: "Admin Console" }]
      : [
          { href: "/properties", label: "Properties" },
          { href: "/search", label: "Search" },
          { href: "/favorites", label: "Favorites" },
        ];

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
            <Link href={homeHref} className="text-xl font-bold text-slate-900">
              VibeHome
            </Link>
          </div>
          <div className="flex items-center gap-4">
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="rounded-md px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-900"
              >
                {link.label}
              </Link>
            ))}
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
