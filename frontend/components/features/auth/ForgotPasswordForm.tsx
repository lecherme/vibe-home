"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { forgotPasswordSchema, type ForgotPasswordFormValues } from "@/lib/schemas/auth";
import { resetPasswordForEmail } from "@/lib/auth/session";
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

export default function ForgotPasswordForm() {
  const [error, setError] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  const form = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: "",
    },
  });

  const onSubmit = async (values: ForgotPasswordFormValues) => {
    setError(null);

    try {
      await resetPasswordForEmail(
        values.email,
        `${window.location.origin}/reset-password`,
      );
      setIsSuccess(true);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to send reset email");
    }
  };

  if (isSuccess) {
    return (
      <div className="bg-white p-8 shadow sm:rounded-lg">
        <h2 className="mb-6 text-center text-3xl font-bold tracking-tight text-gray-900">
          Check your email
        </h2>
        <div className="rounded-md bg-green-50 p-4 text-sm text-green-700">
          If an account exists for that email, a password reset link has been
          sent.
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
        Reset your password
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
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-gray-700">Email address</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    type="email"
                    autoComplete="email"
                    className="border-gray-300 focus:border-indigo-500 focus:ring-indigo-500"
                    disabled={form.formState.isSubmitting}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div>
            <Button
              type="submit"
              disabled={form.formState.isSubmitting}
              className="w-full bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {form.formState.isSubmitting ? "Sending..." : "Send reset link"}
            </Button>
          </div>
        </form>
      </Form>

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
