"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { resetPasswordSchema, type ResetPasswordFormValues } from "@/lib/schemas/auth";
import { getSession, signOut, updateUserPassword } from "@/lib/auth/session";
import { supabase } from "@/lib/auth/supabase";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function ResetPasswordForm() {
  const router = useRouter();
  const [isCheckingSession, setIsCheckingSession] = useState(true);
  const [hasValidSession, setHasValidSession] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [debugError, setDebugError] = useState<string | null>(null);

  const form = useForm<ResetPasswordFormValues>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      password: "",
      confirmPassword: "",
    },
  });

  useEffect(() => {
    let isMounted = true;

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (!isMounted) return;
      if (event === "PASSWORD_RECOVERY" || (event === "SIGNED_IN" && session)) {
        setHasValidSession(true);
        setIsCheckingSession(false);
      }
    });

    const code = new URLSearchParams(window.location.search).get("code");

    if (code) {
      const url = new URL(window.location.href);
      url.searchParams.delete("code");
      window.history.replaceState({}, "", url.toString());

      supabase.auth.exchangeCodeForSession(code).then(({ error }) => {
        if (!isMounted) return;
        if (error) {
          setDebugError(error.message);
          // detectSessionInUrl may have consumed the code first — check session
          getSession().then((session) => {
            if (!isMounted) return;
            setHasValidSession(Boolean(session));
            setIsCheckingSession(false);
          }).catch(() => {
            if (isMounted) {
              setHasValidSession(false);
              setIsCheckingSession(false);
            }
          });
        }
        // on success: onAuthStateChange fires PASSWORD_RECOVERY → handled above
      });
    } else {
      getSession().then((session) => {
        if (!isMounted) return;
        setHasValidSession(Boolean(session));
        setIsCheckingSession(false);
      }).catch(() => {
        if (isMounted) {
          setHasValidSession(false);
          setIsCheckingSession(false);
        }
      });
    }

    return () => {
      isMounted = false;
      subscription.unsubscribe();
    };
  }, []);

  const onSubmit = async (values: ResetPasswordFormValues) => {
    setError(null);
    setIsLoading(true);

    try {
      await updateUserPassword(values.password);
      await signOut();
      router.push("/login");
      router.refresh();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to update password");
      setIsLoading(false);
    }
  };

  if (isCheckingSession) {
    return (
      <div className="bg-white p-8 shadow sm:rounded-lg">
        <h2 className="text-center text-3xl font-bold tracking-tight text-gray-900">
          Checking reset link...
        </h2>
      </div>
    );
  }

  if (!hasValidSession) {
    return (
      <div className="bg-white p-8 shadow sm:rounded-lg">
        <h2 className="mb-6 text-center text-3xl font-bold tracking-tight text-gray-900">
          Reset link expired
        </h2>
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
          This password reset link is invalid or has expired.
          {debugError && <div className="mt-2 font-mono text-xs break-all">{debugError}</div>}
        </div>
        <div className="mt-6 text-center">
          <Link
            href="/login"
            className="font-medium text-indigo-600 hover:text-indigo-500"
          >
            Back to Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-8 shadow sm:rounded-lg">
      <h2 className="mb-6 text-center text-3xl font-bold tracking-tight text-gray-900">
        Create a new password
      </h2>

      <Form {...form}>
        <form className="space-y-6" onSubmit={form.handleSubmit(onSubmit)}>
          {error && (
            <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
              {error}
            </div>
          )}

          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-gray-700">New password</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    type="password"
                    autoComplete="new-password"
                    className="border-gray-300 focus:border-indigo-500 focus:ring-indigo-500"
                    disabled={isLoading}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="confirmPassword"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-gray-700">Confirm password</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    type="password"
                    autoComplete="new-password"
                    className="border-gray-300 focus:border-indigo-500 focus:ring-indigo-500"
                    disabled={isLoading}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div>
            <Button
              type="submit"
              disabled={isLoading}
              className="w-full bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {isLoading ? "Updating..." : "Update password"}
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
